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
    OPTIONAL_CSV_FIELDS = ["bank_account", "line_account", "terms", "memo"]

    def __init__(
        self,
        engine: BatchEngine,
        disambiguator: Disambiguator,
        qbo_client: QBOClientProtocol,
        classifier: Optional[Callable[[str, float], Dict[str, Any]]] = None,
        bank_account_id: str = "default_bank",
        income_account_id: str = "default_income",
        account_finder: Optional[Callable[..., List[Dict[str, Any]]]] = None,
    ):
        self.engine = engine
        self.disambiguator = disambiguator
        self.qbo = qbo_client
        self.classifier = classifier
        self.bank_account_id = bank_account_id
        self.income_account_id = income_account_id
        self._account_finder = account_finder

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
                       if fld not in (reader.fieldnames or [])]
            if missing:
                raise ValueError(f"Columnas faltantes en CSV: {missing}")
            for row_num, row in enumerate(reader, start=2):  # row 1 = header
                try:
                    raw_amount = str(row["amount"]).strip().replace("$", "").replace(",", "").replace(" ", "")
                    amount = float(raw_amount)
                except (ValueError, KeyError):
                    client = row.get("client_name", "?")
                    raw = row.get("amount", "(vacío)")
                    raise ValueError(
                        f"Fila {row_num}: monto inválido '{raw}' para cliente '{client}'. "
                        f"Debe ser un número (ej: 1500.00, no '$1,500')"
                    )
                item = {
                    "date": row["date"].strip(),
                    "client_name": row["client_name"].strip(),
                    "amount": amount,
                    "terms": row.get("terms", "").strip() or None,
                    "memo": row.get("memo", "").strip() or None,
                    "bank_account": row.get("bank_account", "").strip() or None,
                    "line_account": row.get("line_account", "").strip() or None,
                }
                # backward compat: if old template has 'to_account', treat as bank_account
                if not item["bank_account"] and row.get("to_account", "").strip():
                    item["bank_account"] = row["to_account"].strip()
                # backward compat: if old template has 'from_account', treat as line_account
                if not item["line_account"] and row.get("from_account", "").strip():
                    item["line_account"] = row["from_account"].strip()
                items.append(item)
        if not items:
            raise ValueError("CSV sin filas")
        return items

    def resolve_clients(self, batch_id: str, rules: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Para cada item del batch, busca el cliente en QBO.
        Si no existe y hay 2+, pregunta en lote (sin pedir email/terms).
        Si es solo 1, usa el flujo interactivo con datos opcionales.

        HIGH-2b: si `crear_clientes_sin_preguntar = true` en las reglas,
        crea clientes automáticamente sin preguntar.

        Returns:
            Dict con: resolved, errors
        """
        rules = rules or {}
        auto_create = rules.get("crear_clientes_sin_preguntar") == "true"

        items = self.engine.storage.get_items(batch_id)
        resolved: Dict[str, str] = {}
        errors: List[Dict[str, Any]] = []
        unfound: List[str] = []
        client_to_index: Dict[str, int] = {}

        # Primera pasada: buscar clientes, separar encontrados de no encontrados
        for item in items:
            client_name = item["input"]["client_name"]
            if client_name not in client_to_index:
                client_to_index[client_name] = item["index_num"]
            if client_name in resolved:
                continue
            candidates = self.qbo.search_customer(client_name)
            if candidates:
                chosen_id = self._pick_from_candidates(client_name, candidates, rules)
                if chosen_id == "__NEW__":
                    unfound.append(client_name)
                elif chosen_id:
                    resolved[client_name] = chosen_id
                else:
                    errors.append({
                        "index": client_to_index[client_name],
                        "error": f"Usuario saltó selección para '{client_name}'"
                    })
            else:
                unfound.append(client_name)

        if not unfound:
            self.engine.storage.update_batch_context(batch_id, {
                "resolved_clients": resolved
            })
            return {"resolved": resolved, "errors": errors}

        if auto_create:
            for name in unfound:
                cid = self._create_customer_minimal(name)
                if cid:
                    resolved[name] = cid
                    self.disambiguator.output(
                        f"  ✓ Cliente auto-creado: {name} → ID {cid}"
                    )
                else:
                    errors.append({
                        "index": client_to_index[name],
                        "error": f"No se pudo crear '{name}' automáticamente"
                    })
        elif len(unfound) >= 2:
            to_create = self.disambiguator.ask_bulk_new_customers(unfound)
            if to_create:
                for name in to_create:
                    cid = self._create_customer_minimal(name)
                    if cid:
                        resolved[name] = cid
                    else:
                        errors.append({
                            "index": client_to_index[name],
                            "error": f"No se pudo crear '{name}'"
                        })
            else:
                for name in unfound:
                    errors.append({
                        "index": client_to_index[name],
                        "error": f"Usuario canceló creación de '{name}'"
                    })
        else:
            cid = self._create_new_customer(unfound[0])
            if cid:
                resolved[unfound[0]] = cid
            else:
                errors.append({
                    "index": client_to_index[unfound[0]],
                    "error": f"Cliente '{unfound[0]}' no resuelto"
                })

        self.engine.storage.update_batch_context(batch_id, {
            "resolved_clients": resolved
        })
        return {"resolved": resolved, "errors": errors}

    def _pick_from_candidates(
        self,
        client_name: str,
        candidates: List[Dict[str, Any]],
        rules: Dict[str, str] = None,
    ) -> Optional[str]:
        """Elige un candidato. Si es fuzzy (≥85%), pregunta al usuario.

        HIGH-2b: si `fuzzy_auto_select = true`, usa el mejor fuzzy match sin preguntar.
        """
        rules = rules or {}
        is_fuzzy = any("_fuzzy_score" in c for c in candidates)

        if len(candidates) == 1 and not is_fuzzy:
            self.disambiguator.output(
                f"  ✓ Cliente encontrado: {client_name} → ID {candidates[0]['id']}"
            )
            return candidates[0]["id"]

        if is_fuzzy:
            if rules.get("fuzzy_auto_select") == "true" and candidates:
                best = candidates[0]
                best_score = best.get("_fuzzy_score", 0)
                if best_score >= 0.95:
                    self.disambiguator.output(
                        f"  ✓ Fuzzy auto-select (≥95%): {client_name} → {best['name']} "
                        f"({int(best_score * 100)}%) → ID {best['id']}"
                    )
                    return best["id"]
                else:
                    self.disambiguator.output(
                        f"  ⚠️  Fuzzy match bajo ({int(best_score * 100)}% < 95%) para '{client_name}', preguntando..."
                    )
            return self.disambiguator.ask_fuzzy_customer_match(client_name, candidates)

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
        return self._create_qbo_customer(new_data)

    def _create_customer_minimal(self, client_name: str) -> Optional[str]:
        """Crea un cliente en QBO solo con DisplayName, sin preguntar info opcional."""
        try:
            created = self.qbo.create_customer({"DisplayName": client_name})
            cid = created.get("Id", created.get("id", ""))
            self.disambiguator.output(
                f"  ✓ Cliente creado: {client_name} → ID {cid}"
            )
            return cid
        except Exception as e:
            self.disambiguator.show_error(
                f"Error creando cliente '{client_name}'", str(e)
            )
            return None

    def _create_qbo_customer(self, new_data: Dict[str, Any]) -> Optional[str]:
        """Crea un cliente en QBO con los datos del disambiguator."""
        try:
            qbo_payload = {"DisplayName": new_data["name"]}
            if new_data.get("email"):
                qbo_payload["PrimaryEmailAddr"] = new_data["email"]
            if new_data.get("company"):
                qbo_payload["CompanyName"] = new_data["company"]
            created = self.qbo.create_customer(qbo_payload)
            cid = created.get("Id", created.get("id", ""))
            self.disambiguator.output(
                f"  ✓ Cliente creado: {new_data['name']} → ID {cid}"
            )
            return cid
        except Exception as e:
            self.disambiguator.show_error(
                f"Error creando cliente '{new_data.get('name', '?')}'", str(e)
            )
            return None

    def resolve_accounts(self, items: List[Dict[str, Any]], defaults: Dict[str, str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Resuelve nombres de cuenta (bank_account, line_account) a IDs.
        HIGH-2: soporta cuentas de cualquier tipo (Bank, Income, Liability, etc.).

        Args:
            items: lista de items del batch
            defaults: dict con claves como 'banco_default', 'deposito_default'
                      Si un nombre de cuenta resuelve al mismo ID que el default,
                      se auto-selecciona sin preguntar al usuario.
        """
        defaults = defaults or {}
        if not self._account_finder:
            return {}

        resolved: Dict[str, Dict[str, Any]] = {}
        names = set()
        for item in items:
            inp = item.get("input", item)
            for col in ("bank_account", "line_account"):
                name = inp.get(col) or ""
                if name:
                    names.add(name)

        for name in sorted(names):
            candidates = self._account_finder(name, False, None)
            if not candidates:
                self.disambiguator.output(
                    f"  ⚠️  Cuenta '{name}' no encontrada en el Chart of Accounts"
                )
                continue
            if len(candidates) == 1:
                resolved[name] = {
                    "id": candidates[0]["id"],
                    "name": candidates[0]["name"],
                    "type": candidates[0].get("type", ""),
                }
                self.disambiguator.output(
                    f"  ✓ Cuenta encontrada: {name} → {candidates[0]['id']} ({candidates[0]['name']})"
                )
                continue
            # Multiple candidates — check if one matches a default
            default_id = defaults.get("banco_default") if "bank" in name.lower() or "checking" in name.lower() else defaults.get("deposito_default")
            if default_id:
                match = next((c for c in candidates if c.get("id") == default_id), None)
                if match:
                    resolved[name] = {
                        "id": match["id"],
                        "name": match["name"],
                        "type": match.get("type", ""),
                    }
                    self.disambiguator.output(
                        f"  ✓ Cuenta default: {name} → {match['id']} ({match['name']})"
                    )
                    continue
            # Still ambiguous — ask user
            choice = self.disambiguator.ask_account(
                f"Cuenta '{name}' tiene {len(candidates)} coincidencias",
                candidates,
            )
            if choice:
                match = next((c for c in candidates if c.get("id") == choice), None)
                resolved[name] = {
                    "id": choice,
                    "name": match["name"] if match else name,
                    "type": match.get("type", "") if match else "",
                }
            else:
                self.disambiguator.output(
                    f"  ⚠️  Cuenta '{name}' — usuario no seleccionó ninguna"
                )

        return resolved

    def validate(self, batch_id: str, rules: Dict[str, str] = None, defaults: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Valida el batch completo:
        1. Resuelve clientes (busca o crea) — aplica reglas de memoria
        2. Resuelve cuentas (bank_account / line_account) HIGH-2 — auto-select defaults
        3. Marca items como READY o FAILED
        """
        self.engine._assert_transition(batch_id, BatchState.VALIDATED)
        result = self.resolve_clients(batch_id, rules=rules)
        items = self.engine.storage.get_items(batch_id)
        resolved_accounts = self.resolve_accounts(items, defaults=defaults)

        self.engine.storage.update_batch_context(batch_id, {
            "resolved_clients": result["resolved"],
            "resolved_accounts": resolved_accounts,
        })

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
                "resolved_clients": result["resolved"],
            }
        )
        return {
            "ready": ready,
            "failed": len(failed_indices),
            "resolved_clients": result["resolved"],
            "resolved_accounts": resolved_accounts,
        }

    def execute(self, batch_id: str) -> Dict[str, Any]:
        """
        Ejecuta el batch agrupando items con mismo date+bank_account
        en UN solo depósito multi-línea (HIGH-2 grouping).

        Asume que ya pasó por validate + dry_run + confirm.
        """
        self.engine._assert_transition(batch_id, BatchState.EXECUTING)
        self.engine.storage.update_batch_state(batch_id, BatchState.EXECUTING)

        items = self.engine.storage.get_items(batch_id)
        ready_items = [i for i in items if i["state"] == ItemState.READY.value]
        if not ready_items:
            self.engine.storage.update_batch_state(batch_id, BatchState.EXECUTED,
                summary={"executed": 0, "failed": 0, "total": len(items)})
            return {"executed": 0, "failed": 0, "total": len(items), "errors": []}

        batch = self.engine.storage.get_batch(batch_id)
        ctx = batch.get("context", {})
        resolved_clients = ctx.get("resolved_clients", {})
        resolved_accounts = ctx.get("resolved_accounts", {})

        from collections import defaultdict
        groups = defaultdict(list)
        for item in ready_items:
            inp = item["input"]
            bank = inp.get("bank_account") or ""
            bank_id = resolved_accounts.get(bank, {}).get("id") or self.bank_account_id if bank else self.bank_account_id
            key = (inp["date"], bank_id)
            groups[key].append(item)

        executed = 0
        failed = 0
        errors = []

        for (date, bank_account_id), group_items in groups.items():
            lines = []
            group_item_ids = []
            group_inputs = []
            batch_memo_parts = []

            for item in group_items:
                inp = item["input"]
                client_name = inp["client_name"]
                customer_id = resolved_clients.get(client_name)
                if not customer_id:
                    failed += 1
                    errors.append({"index": item["index_num"], "client": client_name, "error": "Cliente no resuelto"})
                    self.engine.storage.update_item(item["id"], ItemState.FAILED, error="Cliente no resuelto")
                    continue

                line_acc = self.income_account_id
                la = inp.get("line_account") or ""
                if la and la in resolved_accounts:
                    line_acc = resolved_accounts[la]["id"]

                description = inp.get("memo") or client_name
                if self.classifier and not la:
                    suggestion = self.classifier(description, inp["amount"])
                    if suggestion.get("account_id"):
                        line_acc = suggestion["account_id"]

                lines.append({
                    "amount": inp["amount"],
                    "from_account_id": line_acc,
                    "customer_id": customer_id,
                    "description": description,
                })
                group_item_ids.append(item["id"])
                group_inputs.append(inp)
                batch_memo_parts.append(client_name)

            if not lines:
                continue

            memo = f"Batch {batch_id[:8]} — {len(group_items)} clientes"
            try:
                result = self.qbo.create_deposit(
                    date=date,
                    account_id=bank_account_id,
                    lines=lines,
                    memo=memo,
                )
                deposit_id = result.get("deposit_id", result.get("Id", result.get("id", "")))
                output = {"qbo_deposit_id": deposit_id, "lines": len(lines)}
                for item_id, inp in zip(group_item_ids, group_inputs):
                    self.engine.storage.update_item(item_id, ItemState.EXECUTED, output=output)
                    executed += 1
                self.disambiguator.output(
                    f"  ✓ Depósito creado: {date} | {bank_account_id} | ${sum(l['amount'] for l in lines):.2f} | {len(lines)} clientes → ID {deposit_id}"
                )
            except Exception as e:
                err_msg = f"Error creando depósito agrupado ({len(group_items)} items, {date}): {e}"
                for item_id, inp in zip(group_item_ids, group_inputs):
                    self.engine.storage.update_item(item_id, ItemState.FAILED, error=err_msg)
                    failed += 1
                errors.append({"date": date, "bank": bank_account_id, "clients": batch_memo_parts, "error": str(e)})

        final_state = BatchState.EXECUTED if failed == 0 else BatchState.FAILED
        self.engine.storage.update_batch_state(batch_id, final_state,
            summary={"executed": executed, "failed": failed, "total": len(items), "errors": errors})
        return {"executed": executed, "failed": failed, "total": len(items), "errors": errors}
