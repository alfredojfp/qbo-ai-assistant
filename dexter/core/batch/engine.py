# -*- coding: utf-8 -*-
"""
Motor batch de Dexter: orquesta el ciclo de vida de un batch.

Estados permitidos y transiciones:

    PENDING → VALIDATED → DRY_RUN → CONFIRMED → EXECUTING → EXECUTED
                ↓           ↓           ↓
              CANCELLED  CANCELLED   CANCELLED
                ↓
              FAILED

El engine es agnóstico al dominio. El dominio concreto (deposits, bills, etc.)
provee callbacks de validación y ejecución.
"""
from typing import Any, Callable, Dict, List, Optional, Tuple

from dexter.core.batch.storage import BatchState, BatchStorage, ItemState

# Transiciones válidas
_VALID_TRANSITIONS: Dict[BatchState, List[BatchState]] = {
    BatchState.PENDING: [BatchState.VALIDATED, BatchState.CANCELLED, BatchState.FAILED],
    BatchState.VALIDATED: [BatchState.DRY_RUN, BatchState.CANCELLED, BatchState.FAILED],
    BatchState.DRY_RUN: [BatchState.CONFIRMED, BatchState.CANCELLED, BatchState.FAILED],
    BatchState.CONFIRMED: [BatchState.EXECUTING, BatchState.CANCELLED, BatchState.FAILED],
    BatchState.EXECUTING: [BatchState.EXECUTED, BatchState.FAILED],
    BatchState.EXECUTED: [],
    BatchState.CANCELLED: [],
    BatchState.FAILED: [BatchState.PENDING],  # Permite reintentar
}


# Tipo del callback: recibe input del item, retorna (output, error)
ExecutorFunc = Callable[[Dict[str, Any]], Tuple[Optional[Dict[str, Any]], Optional[str]]]


class InvalidStateTransition(Exception):
    """Se intenta una transición de estado no permitida."""
    pass


class BatchEngine:
    """Orquesta el ciclo de vida de un batch."""

    def __init__(self, storage: BatchStorage):
        self.storage = storage

    def _assert_transition(self, batch_id: str, target: BatchState) -> None:
        current = self.storage.get_batch(batch_id)
        if not current:
            raise ValueError(f"Batch no existe: {batch_id}")
        current_state = BatchState(current["state"])
        if target not in _VALID_TRANSITIONS[current_state]:
            raise InvalidStateTransition(
                f"Transición inválida: {current_state.value} → {target.value}"
            )

    def create_batch(
        self,
        skill: str,
        items: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Crea un batch nuevo con sus items. Estado: PENDING."""
        batch_id = self.storage.create_batch(skill, context=context)
        for idx, item in enumerate(items):
            self.storage.add_item(batch_id, idx, item)
        return batch_id

    def validate(
        self,
        batch_id: str,
        validator: Optional[Callable[[Dict[str, Any]], Tuple[bool, Optional[str]]]] = None
    ) -> Dict[str, Any]:
        """
        Valida cada item del batch.

        Args:
            batch_id: ID del batch
            validator: función (item) -> (is_valid, error_msg)
                       Si None, se considera todo válido.

        Returns:
            Dict con: valid, invalid, errors
        """
        self._assert_transition(batch_id, BatchState.VALIDATED)
        items = self.storage.get_items(batch_id)
        valid = 0
        invalid = 0
        errors: List[Dict[str, Any]] = []

        for item in items:
            item_input = item["input"]
            is_valid = True
            error_msg: Optional[str] = None
            if validator is not None:
                is_valid, error_msg = validator(item_input)
            if is_valid:
                self.storage.update_item(item["id"], ItemState.READY)
                valid += 1
            else:
                self.storage.update_item(item["id"], ItemState.FAILED, error=error_msg)
                invalid += 1
                errors.append({"index": item["index_num"], "error": error_msg,
                              "input": item_input})

        self.storage.update_batch_state(batch_id, BatchState.VALIDATED,
                                         summary={"valid": valid, "invalid": invalid})
        return {"valid": valid, "invalid": invalid, "errors": errors}

    def dry_run(self, batch_id: str) -> Dict[str, Any]:
        """
        Genera resumen del batch sin ejecutar. Estado: DRY_RUN.

        Returns:
            Dict con: total, items, summary
        """
        self._assert_transition(batch_id, BatchState.DRY_RUN)
        items = self.storage.get_items(batch_id)
        total = len(items)
        ready = sum(1 for i in items if i["state"] == ItemState.READY.value)
        failed = sum(1 for i in items if i["state"] == ItemState.FAILED.value)
        summary = {
            "total": total,
            "ready_to_execute": ready,
            "skipped": failed,
            "items": [
                {
                    "index": i["index_num"],
                    "state": i["state"],
                    "input": i["input"]
                }
                for i in items
            ]
        }
        self.storage.update_batch_state(batch_id, BatchState.DRY_RUN, summary=summary)
        return summary

    def confirm(self, batch_id: str) -> None:
        """Usuario confirma que quiere ejecutar el batch. Estado: CONFIRMED."""
        self._assert_transition(batch_id, BatchState.CONFIRMED)
        self.storage.update_batch_state(batch_id, BatchState.CONFIRMED)

    def execute(
        self,
        batch_id: str,
        executor: ExecutorFunc
    ) -> Dict[str, Any]:
        """
        Ejecuta el batch con un callback.

        Args:
            batch_id: ID del batch
            executor: función (item_input) -> (output, error)

        Returns:
            Dict con: executed, failed, total
        """
        self._assert_transition(batch_id, BatchState.EXECUTING)
        self.storage.update_batch_state(batch_id, BatchState.EXECUTING)

        items = self.storage.get_items(batch_id)
        executed = 0
        failed = 0
        errors: List[Dict[str, Any]] = []

        for item in items:
            if item["state"] != ItemState.READY.value:
                continue
            try:
                output, error = executor(item["input"])
                if error:
                    self.storage.update_item(item["id"], ItemState.FAILED, error=error)
                    failed += 1
                    errors.append({"index": item["index_num"], "client": item["input"].get("client_name", "?"), "error": error})
                else:
                    self.storage.update_item(item["id"], ItemState.EXECUTED, output=output)
                    executed += 1
            except Exception as e:
                self.storage.update_item(item["id"], ItemState.FAILED, error=str(e))
                failed += 1
                errors.append({"index": item["index_num"], "client": item["input"].get("client_name", "?"), "error": str(e)})

        if failed == 0:
            final_state = BatchState.EXECUTED
        else:
            final_state = BatchState.FAILED
        self.storage.update_batch_state(
            batch_id, final_state,
            summary={"executed": executed, "failed": failed, "total": len(items), "errors": errors}
        )
        return {"executed": executed, "failed": failed, "total": len(items), "errors": errors}

    def cancel(self, batch_id: str) -> None:
        """Cancela un batch en cualquier estado pre-ejecución."""
        current = self.storage.get_batch(batch_id)
        if not current:
            raise ValueError(f"Batch no existe: {batch_id}")
        current_state = BatchState(current["state"])
        if BatchState.CANCELLED not in _VALID_TRANSITIONS[current_state]:
            raise InvalidStateTransition(
                f"No se puede cancelar desde {current_state.value}"
            )
        self.storage.update_batch_state(batch_id, BatchState.CANCELLED)

    def retry(self, batch_id: str) -> str:
        """Reabre un batch FAILED para reintentar. Crea un nuevo batch."""
        current = self.storage.get_batch(batch_id)
        if not current:
            raise ValueError(f"Batch no existe: {batch_id}")
        if current.get("state") != BatchState.FAILED.value:
            raise InvalidStateTransition(
                f"Solo se puede reintentar un batch en estado FAILED (actual: {current.get('state')})"
            )
        return self.create_batch(
            skill=current.get("skill", "unknown"),
            items=[i["input"] for i in self.storage.get_items(batch_id)],
            context=current.get("context", {})
        )
