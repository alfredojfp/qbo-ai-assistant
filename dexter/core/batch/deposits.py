# -*- coding: utf-8 -*-
"""
Skill de bank deposits multi-cliente con desambiguación.

Este es el ejemplo end-to-end de Sprint 1 + 2: usa el motor batch,
el disambiguator, y el motor de clasificación de bank_feed para crear
un deposit en QBO con múltiples clientes, preguntando al usuario
cuando algo falta.

Flujo:
1. Lee CSV con líneas (date, client_name, amount, terms?)
2. Para cada línea: busca cliente en QBO. Si no existe, pregunta.
3. Sugiere cuenta contable con el motor de matching.
4. Genera dry-run. Usuario confirma.
5. Crea el deposit en QBO.
6. Audit log de todo.

API testeable: QBOClient es inyectable.
"""
import csv
import json
import os
from typing import Any, Callable, Dict, List, Optional

from dexter.core.batch.disambiguator import Disambiguator
from dexter.core.batch.engine import BatchEngine
from dexter.core.batch.storage import BatchState, BatchStorage, ItemState


class QBOClientProtocol:
    """Interfaz mínima que cualquier cliente QBO debe implementar."""

    def search_customer(self, name: str) -> List[Dict[str, Any]]:
        ...

    def create_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def create_deposit(
        self,
        date: str,
        account_id: str,
        lines: List[Dict[str, Any]],
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        ...


class DepositBatchSkill:
    """Skill de bank deposits multi-cliente."""

    REQUIRED_CSV_FIELDS = ["date", "client_name", "amount"]

    def __init__(
        self,
        engine: BatchEngine,
        disambiguator: Disambiguator,
        qbo_client: QBOClientProtocol,
        classifier: Optional[Callable[[str, float], Dict[str, Any]]] = None,
        bank_account_id: str = "default_bank",
        income_account_id: str = "default_income"
    ):
        self.engine = engine
        self.disambiguator = disambiguator
        self.qbo = qbo_client
        self.classifier = classifier
        self.bank_account_id = bank_account_id
        self.income_account_id = income_account_id

    def from_csv(self, csv_path: str) -> str:
        """
        Lee un CSV de deposit items y crea un batch.

        CSV esperado: date, client_name, amount[, terms][, memo]
        """
        items = self._read_csv(csv_path)
        return self.engine.create_batch(
            "deposits", items, context={"source": csv_path}
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
                raise ValueError(f"Columnas faltantes en CSV: {missing}")
            for row in reader:
                try:
                    amount = float(row["amount"])
                except (ValueError, KeyError):
                    raise ValueError(f"Monto inválido: {row.get('amount')}")
                items.append({
                    "date": row["date"].strip(),
                    "client_name": row["client_name"].strip(),
                    "amount": amount,
                    "terms": row.get("terms", "").strip() or None,
                    "memo": row.get("memo", "").strip() or None,
                })
        if not items:
            raise ValueError("CSV sin filas")
        return items

    def resolve_clients(self, batch_id: str) -> Dict[str, Any]:
        """
        Para cada item del batch, busca el cliente en QBO.
        Si no existe, pregunta al usuario si quiere crearlo.
        Guarda el resultado en el contexto del batch.

        Returns:
            Dict con: resolved, errors
        """
        items = self.engine.storage.get_items(batch_id)
        resolved: Dict[str, str] = {}
        errors: List[Dict[str, Any]] = []

        for item in items:
            client_name = item["input"]["client_name"]
            if client_name in resolved:
                continue
            candidates = self.qbo.search_customer(client_name)
            if candidates:
                chosen_id = self._pick_from_candidates(client_name, candidates)
                if chosen_id:
                    resolved[client_name] = chosen_id
                else:
                    errors.append({
                        "index": item["index_num"],
                        "error": f"Usuario saltó selección para '{client_name}'"
                    })
            else:
                customer_id = self._create_new_customer(client_name)
                if customer_id:
                    resolved[client_name] = customer_id
                else:
                    errors.append({
                        "index": item["index_num"],
                        "error": f"Cliente '{client_name}' no resuelto"
                    })

        self.engine.storage.update_batch_context(batch_id, {
            "resolved_clients": resolved
        })
        return {"resolved": resolved, "errors": errors}

    def _pick_from_candidates(
        self,
        client_name: str,
        candidates: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Elige un candidato. Si hay uno solo, lo toma. Si hay varios, pregunta."""
        if len(candidates) == 1:
            self.disambiguator.output(
                f"  ✓ Cliente encontrado: {client_name} → ID {candidates[0]['id']}"
            )
            return candidates[0]["id"]

        options = [f"{c.get('name', '?')} (ID: {c.get('id', '?')})"
                   for c in candidates]
        choice = self.disambiguator.ask_choice(
            f"Cliente '{client_name}' tiene {len(candidates)} coincidencias:",
            options,
            allow_new=False
        )
        if choice is None:
            return None
        for c in candidates:
            if str(c.get("id", "?")) in choice:
                return c["id"]
        return candidates[0]["id"] if candidates else None

    def _create_new_customer(self, client_name: str) -> Optional[str]:
        """Pregunta al usuario y crea un cliente nuevo en QBO."""
        self.disambiguator.output(f"  ⚠️  Cliente no encontrado: '{client_name}'")
        new_data = self.disambiguator.ask_new_customer(client_name)
        if new_data is None:
            return None
        try:
            created = self.qbo.create_customer(new_data)
            self.disambiguator.output(
                f"  ✓ Cliente creado: {client_name} → ID {created['id']}"
            )
            return created["id"]
        except Exception as e:
            self.disambiguator.show_error(
                f"Error creando cliente '{client_name}'", str(e)
            )
            return None

    def validate(self, batch_id: str) -> Dict[str, Any]:
        """
        Valida el batch completo:
        1. Resuelve clientes (busca o crea)
        2. Marca items como READY o FAILED
        """
        result = self.resolve_clients(batch_id)
        items = self.engine.storage.get_items(batch_id)
        ready = 0
        failed_indices = {e["index"] for e in result["errors"]}

        for item in items:
            client_name = item["input"]["client_name"]
            if item["index_num"] in failed_indices:
                self.engine.storage.update_item(
                    item["id"], ItemState.FAILED,
                    error=next((e["error"] for e in result["errors"]
                                if e["index"] == item["index_num"]), "Unknown")
                )
            elif client_name in result["resolved"]:
                self.engine.storage.update_item(item["id"], ItemState.READY)
                ready += 1
            else:
                self.engine.storage.update_item(
                    item["id"], ItemState.FAILED, error="Cliente no resuelto"
                )

        self.engine.storage.update_batch_state(
            batch_id, BatchState.VALIDATED,
            summary={
                "ready": ready,
                "failed": len(failed_indices),
                "resolved_clients": result["resolved"]
            }
        )
        return {
            "ready": ready,
            "failed": len(failed_indices),
            "resolved_clients": result["resolved"]
        }

    def execute(self, batch_id: str) -> Dict[str, Any]:
        """
        Ejecuta el batch: crea un deposit por cada item en QBO.
        Asume que ya pasó por validate + dry_run + confirm.
        """
        return self.engine.execute(batch_id, self._executor_for(batch_id))

    def _executor_for(self, batch_id: str):
        def executor(item_input: Dict[str, Any]) -> tuple:
            client_name = item_input["client_name"]
            batch = self.engine.storage.get_batch(batch_id)
            resolved = batch.get("context", {}).get("resolved_clients", {})
            customer_id = resolved.get(client_name)

            if not customer_id:
                return (None, f"Cliente '{client_name}' no resuelto")

            description = item_input.get("memo") or f"Deposit from {client_name}"
            account_id = self.income_account_id
            if self.classifier:
                suggestion = self.classifier(description, item_input["amount"])
                if suggestion.get("account_id"):
                    account_id = suggestion["account_id"]

            try:
                result = self.qbo.create_deposit(
                    date=item_input["date"],
                    account_id=self.bank_account_id,
                    lines=[{
                        "amount": item_input["amount"],
                        "from_account_id": account_id,
                        "customer_id": customer_id,
                        "description": description,
                    }],
                    memo=f"Batch {batch_id[:8]} - {client_name}"
                )
                return ({"qbo_deposit_id": result.get("id")}, None)
            except Exception as e:
                return (None, f"Error QBO: {e}")
        return executor
