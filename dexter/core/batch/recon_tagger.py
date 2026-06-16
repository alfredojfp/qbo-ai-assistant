# -*- coding: utf-8 -*-
"""
Skill de Reconciliation Tagger (BNK-RECON).

Esta skill NO crea transactions nuevas. Solo agrega un tag
(BNK-RECON-YYYY-MM-xxxxx) a las transactions existentes de QBO
que matchean con las filas del CSV del bank statement.

Casos de uso:
- El usuario quiere ayuda para reconciliar en QBO UI
- No quiere duplicados si QBO ya importó algo
- Necesita un marcador visible para saber qué filas ya cruzaron

Campos usados en QBO:
- Deposit.Memo
- Bill.PrivateNote
- Purchase.PrivateNote
- Invoice.PrivateNote (no usado en este flujo)
"""
import csv
import hashlib
import json
import os
import random
import string
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from dexter.core.batch.disambiguator import Disambiguator
from dexter.core.batch.engine import BatchEngine
from dexter.core.batch.storage import BatchState, BatchStorage, ItemState


class QBOClientProtocol:
    """Interfaz mínima del cliente QBO para reconciliation."""

    def get_transactions(
        self,
        account_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Retorna transactions de QBO en el período para esa cuenta."""
        ...

    def update_transaction(
        self,
        txn_type: str,
        txn_id: str,
        fields: Dict[str, Any],
        sync_token: str = "0",
    ) -> Dict[str, Any]:
        """Actualiza campos de una transaction (Memo, PrivateNote, etc.)."""
        ...


# Mapeo de tipo de transaction → campo de tag
TAG_FIELD_BY_TYPE = {
    "Deposit": "Memo",
    "Bill": "PrivateNote",
    "Purchase": "PrivateNote",
    "Expense": "PrivateNote",
}


@dataclass
class Match:
    qbo_id: str
    qbo_type: str
    qbo_date: str
    qbo_amount: float
    match_type: str  # "exact" | "fuzzy" | "weak"
    confidence: int
    csv_row: Dict[str, Any]


class ReconciliationTaggerSkill:
    """Marca transactions de QBO que matchean con un bank statement."""

    REQUIRED_CSV_FIELDS = ["date", "description", "amount"]

    def __init__(
        self,
        engine: BatchEngine,
        qbo_client: QBOClientProtocol,
        period_start: str,
        period_end: str,
        account_id: str,
        fuzzy_days: int = 2,
        fuzzy_amount: float = 0.50,
        fuzzy_confidence_threshold: int = 80,
    ):
        self.engine = engine
        self.qbo = qbo_client
        self.period_start = period_start
        self.period_end = period_end
        self.account_id = account_id
        self.fuzzy_days = fuzzy_days
        self.fuzzy_amount = fuzzy_amount
        self.fuzzy_confidence_threshold = fuzzy_confidence_threshold
        month_str = period_start[:7]  # YYYY-MM
        self.tag_prefix = f"BNK-RECON-{month_str}"

    def from_csv(self, csv_path: str) -> str:
        """Lee el CSV del bank statement y crea un batch."""
        items = self._read_csv(csv_path)
        return self.engine.create_batch(
            "recon_tagger", items, context={
                "csv": csv_path,
                "period": f"{self.period_start} a {self.period_end}",
                "account_id": self.account_id,
                "tag_prefix": self.tag_prefix,
            }
        )

    def _read_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV no encontrado: {csv_path}")
        items = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            missing = [fld for fld in self.REQUIRED_CSV_FIELDS
                       if fld not in reader.fieldnames]
            if missing:
                raise ValueError(f"Columnas faltantes: {missing}")
            for row in reader:
                try:
                    amount = float(row["amount"])
                except (ValueError, KeyError):
                    raise ValueError(f"Monto inválido: {row.get('amount')}")
                items.append({
                    "date": row["date"].strip(),
                    "description": row.get("description", "").strip(),
                    "amount": amount,
                    "reference": row.get("reference", "").strip() or None,
                })
        if not items:
            raise ValueError("CSV sin filas")
        return items

    def fetch_qbo_transactions(self) -> List[Dict[str, Any]]:
        """Descarga transactions de QBO para el período."""
        return self.qbo.get_transactions(
            self.account_id, self.period_start, self.period_end
        )

    def find_matches(
        self,
        csv_items: List[Dict[str, Any]],
        qbo_txns: List[Dict[str, Any]]
    ) -> Tuple[List[Match], List[Dict[str, Any]]]:
        """
        Encuentra matches para cada fila del CSV.

        Returns:
            (matches, unmatched_csv_rows)
        """
        matches: List[Match] = []
        used_qbo_ids = set()

        for row in csv_items:
            best = None
            best_score = 0
            for qbo in qbo_txns:
                if qbo["id"] in used_qbo_ids:
                    continue
                score, match_type = self._score_match(row, qbo)
                if score > best_score:
                    best_score = score
                    best = qbo
                    best_type = match_type

            if best and best_score >= 60:
                matches.append(Match(
                    qbo_id=best["id"],
                    qbo_type=best["type"],
                    qbo_date=best["date"],
                    qbo_amount=best["amount"],
                    match_type=best_type,
                    confidence=best_score,
                    csv_row=row,
                ))
                used_qbo_ids.add(best["id"])
            else:
                matches.append(Match(
                    qbo_id="", qbo_type="", qbo_date="", qbo_amount=0,
                    match_type="none", confidence=0, csv_row=row,
                ))

        unmatched = [m for m in matches if m.match_type == "none"]
        matched = [m for m in matches if m.match_type != "none"]
        return matched, [m.csv_row for m in unmatched]

    def _score_match(
        self,
        csv_row: Dict[str, Any],
        qbo: Dict[str, Any]
    ) -> Tuple[int, str]:
        """Calcula score de match (0-100) y tipo."""
        csv_amount = csv_row["amount"]
        qbo_amount = qbo["amount"]
        # Considerar signos (en bank CSV, débitos son positivos, en QBO Bill.amount es positivo)
        amount_diff = abs(abs(csv_amount) - abs(qbo_amount))

        if amount_diff > self.fuzzy_amount:
            return 0, "none"

        # Misma fecha y mismo monto = exacto
        if csv_row["date"] == qbo["date"] and amount_diff < 0.01:
            return 100, "exact"

        # Mismo monto, fecha ±N días = fuzzy
        csv_date = self._parse_date(csv_row["date"])
        qbo_date = self._parse_date(qbo["date"])
        if csv_date and qbo_date:
            day_diff = abs((csv_date - qbo_date).days)
            if day_diff <= self.fuzzy_days:
                # Score depende de qué tan cerca está
                if day_diff == 0:
                    return 90, "fuzzy"
                return 75 - (day_diff * 5), "fuzzy"

        return 0, "none"

    @staticmethod
    def _parse_date(s: str) -> Optional[datetime]:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        return None

    def _generate_tag(self, csv_row: Dict[str, Any]) -> str:
        """Genera un tag único basado en la fila del CSV."""
        key = f"{csv_row['date']}|{csv_row['amount']}|{csv_row.get('description', '')}"
        hash_part = hashlib.sha1(key.encode()).hexdigest()[:5]
        return f"{self.tag_prefix}-{hash_part}"

    def run(self, batch_id: str) -> Dict[str, Any]:
        """
        Ejecuta el flujo completo con state machine:
        1. validate() — descarga QBO y matchea
        2. engine.dry_run() — muestra resumen
        3. engine.confirm() — usuario confirma
        4. execute() — aplica tags

        Returns:
            Dict con matched, unmatched, errors, report_path
        """
        self.validate(batch_id)

        batch = self.engine.storage.get_batch(batch_id)
        summary = batch.get("summary", {})
        matched_count = summary.get("matched", 0)
        unmatched_count = summary.get("unmatched", 0)

        if matched_count == 0:
            self.engine.storage.update_batch_state(batch_id, BatchState.EXECUTED,
                summary={"matched": 0, "unmatched": unmatched_count, "executed": 0, "failed": 0})
            return {"matched": 0, "exact": 0, "fuzzy": 0, "unmatched": unmatched_count,
                    "errors": 0, "report_path": "", "tag_prefix": self.tag_prefix}

        self.engine.dry_run(batch_id)
        self.engine.confirm(batch_id)
        return self.execute(batch_id)

    def validate(self, batch_id: str) -> Dict[str, Any]:
        self.engine._assert_transition(batch_id, BatchState.VALIDATED)
        items = self.engine.storage.get_items(batch_id)
        csv_items = [item["input"] for item in items]
        qbo_txns = self.fetch_qbo_transactions()

        matched, unmatched = self.find_matches(csv_items, qbo_txns)
        ready = 0

        for item in items:
            inp = item["input"]
            found = any(m.csv_row is inp for m in matched)
            if found:
                self.engine.storage.update_item(item["id"], ItemState.READY)
                ready += 1
            else:
                self.engine.storage.update_item(item["id"], ItemState.FAILED,
                    error="No match encontrado en QBO")

        self.engine.storage.update_batch_context(batch_id, {
            "_matched": [{"qbo_id": m.qbo_id, "qbo_type": m.qbo_type,
                          "match_type": m.match_type, "confidence": m.confidence,
                          "csv_row": m.csv_row} for m in matched],
            "_unmatched": unmatched,
        })
        self.engine.storage.update_batch_state(batch_id, BatchState.VALIDATED,
            summary={"matched": len(matched), "ready": ready, "unmatched": len(unmatched)})
        return {"matched": len(matched), "ready": ready, "unmatched": len(unmatched)}

    def execute(self, batch_id: str) -> Dict[str, Any]:
        self.engine._assert_transition(batch_id, BatchState.EXECUTING)
        self.engine.storage.update_batch_state(batch_id, BatchState.EXECUTING)

        ctx = self.engine.storage.get_batch(batch_id).get("context", {})
        matched = ctx.get("_matched", [])
        unmatched = ctx.get("_unmatched", [])

        results: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        executed = 0
        failed = 0
        items = self.engine.storage.get_items(batch_id)

        for match in matched:
            tag = self._generate_tag(match["csv_row"])
            field = TAG_FIELD_BY_TYPE.get(match["qbo_type"], "PrivateNote")
            try:
                self.qbo.update_transaction(
                    match["qbo_type"], match["qbo_id"], {field: tag}
                )
                results.append({
                    "csv_date": match["csv_row"]["date"],
                    "csv_amount": match["csv_row"]["amount"],
                    "csv_description": match["csv_row"].get("description", ""),
                    "tag": tag,
                    "qbo_id": match["qbo_id"],
                    "qbo_type": match["qbo_type"],
                    "field_updated": field,
                    "match_type": match["match_type"],
                    "confidence": match["confidence"],
                })
                executed += 1
            except Exception as e:
                failed += 1
                errors.append({
                    "csv_row": match["csv_row"],
                    "qbo_id": match["qbo_id"],
                    "error": str(e),
                })

        # Mark items
        for item in items:
            inp = item["input"]
            was_matched = any(
                m["csv_row"]["date"] == inp["date"]
                and m["csv_row"]["amount"] == inp["amount"]
                and m["csv_row"].get("description") == inp.get("description")
                for m in matched
            )
            if was_matched:
                tag_errored = any(
                    e["csv_row"]["date"] == inp["date"]
                    and e["csv_row"]["amount"] == inp["amount"]
                    for e in errors
                )
                if tag_errored:
                    self.engine.storage.update_item(item["id"], ItemState.FAILED,
                        error="Error aplicando tag")
                else:
                    self.engine.storage.update_item(item["id"], ItemState.EXECUTED)
            # FAILED items already marked by validate

        report_path = self._write_report(batch_id, results, unmatched, errors)
        self.engine.storage.update_batch_context(
            batch_id, {"report_path": report_path}
        )

        final_state = BatchState.EXECUTED if failed == 0 else BatchState.FAILED
        summary = {
            "matched": len(results),
            "exact": sum(1 for r in results if r["match_type"] == "exact"),
            "fuzzy": sum(1 for r in results if r["match_type"] == "fuzzy"),
            "unmatched": len(unmatched),
            "errors": len(errors),
            "executed": executed,
            "failed": failed,
            "report_path": report_path,
            "tag_prefix": self.tag_prefix,
        }
        self.engine.storage.update_batch_state(batch_id, final_state, summary=summary)
        return summary

    def _write_report(
        self,
        batch_id: str,
        matched: List[Dict[str, Any]],
        unmatched: List[Dict[str, Any]],
        errors: List[Dict[str, Any]]
    ) -> str:
        """Genera CSV de mapping."""
        os.makedirs("data", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"data/recon_{batch_id[:8]}_{timestamp}.csv"
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "csv_date", "csv_amount", "csv_description", "tag",
                "qbo_id", "qbo_type", "field_updated", "match_type", "confidence"
            ])
            writer.writeheader()
            for row in matched:
                writer.writerow(row)
            for row in unmatched:
                writer.writerow({
                    "csv_date": row.get("date", ""),
                    "csv_amount": row.get("amount", 0),
                    "csv_description": row.get("description", ""),
                    "tag": "",
                    "qbo_id": "",
                    "qbo_type": "",
                    "field_updated": "",
                    "match_type": "none",
                    "confidence": 0,
                })
            for err in errors:
                writer.writerow({
                    "csv_date": err["csv_row"].get("date", ""),
                    "csv_amount": err["csv_row"].get("amount", 0),
                    "csv_description": err["csv_row"].get("description", ""),
                    "tag": "",
                    "qbo_id": err.get("qbo_id", ""),
                    "qbo_type": "",
                    "field_updated": "",
                    "match_type": "error",
                    "confidence": 0,
                })
        return path

    def cleanup_tags(self, batch_id: str) -> Dict[str, Any]:
        """
        Limpia los tags aplicados por esta skill.
        Lee el reporte y borra los Memo/PrivateNote que coincidan.
        """
        batch = self.engine.storage.get_batch(batch_id)
        report_path = batch.get("context", {}).get("report_path")
        if not report_path or not os.path.exists(report_path):
            return {"removed": 0, "error": "No hay reporte para este batch"}
        removed = 0
        errors = []
        with open(report_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row["tag"] or row["match_type"] == "error":
                    continue
                field = row["field_updated"]
                try:
                    self.qbo.update_transaction(
                        row["qbo_type"], row["qbo_id"], {field: ""}
                    )
                    removed += 1
                except Exception as e:
                    errors.append({"qbo_id": row["qbo_id"], "error": str(e)})
        return {"removed": removed, "errors": errors}
