# -*- coding: utf-8 -*-
"""
Storage SQLite para el motor batch de Dexter.

Tres tablas:
- batches: metadatos de cada batch
- items: cada item dentro de un batch
- audit_log: log inmutable de eventos

Las operaciones son idempotentes donde es posible para soportar re-ejecución.
"""
import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional


class BatchState(str, Enum):
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    DRY_RUN = "DRY_RUN"
    CONFIRMED = "CONFIRMED"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ItemState(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


SCHEMA = """
CREATE TABLE IF NOT EXISTS batches (
    id TEXT PRIMARY KEY,
    skill TEXT NOT NULL,
    state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    context_json TEXT,
    summary_json TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL,
    index_num INTEGER NOT NULL,
    state TEXT NOT NULL,
    input_json TEXT NOT NULL,
    output_json TEXT,
    error TEXT,
    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_items_batch ON items(batch_id);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT,
    item_id TEXT,
    event TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    details_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_batch ON audit_log(batch_id);
CREATE INDEX IF NOT EXISTS idx_audit_item ON audit_log(item_id);
"""


class BatchStorage:
    """Wrapper sobre sqlite3 con API específica para batches."""

    def __init__(self, db_path: str = "data/dexter.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._init_schema()

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    def create_batch(
        self,
        skill: str,
        context: Optional[Dict[str, Any]] = None,
        batch_id: Optional[str] = None
    ) -> str:
        bid = batch_id or str(uuid.uuid4())
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO batches (id, skill, state, created_at, updated_at, context_json)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (bid, skill, BatchState.PENDING.value, now, now,
                 json.dumps(context or {}, ensure_ascii=False))
            )
            self._log_event(conn, bid, None, "BATCH_CREATED", {"skill": skill})
        return bid

    def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM batches WHERE id = ?", (batch_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_batch(row)

    def update_batch_context(
        self,
        batch_id: str,
        context: Dict[str, Any]
    ) -> None:
        """Actualiza el context_json del batch (merge con el existente)."""
        current = self.get_batch(batch_id)
        if not current:
            return
        merged = dict(current.get("context", {}))
        merged.update(context)
        with self._conn() as conn:
            conn.execute(
                """UPDATE batches
                   SET context_json = ?, updated_at = ?
                   WHERE id = ?""",
                (json.dumps(merged, ensure_ascii=False),
                 datetime.now().isoformat(),
                 batch_id)
            )
            self._log_event(conn, batch_id, None, "BATCH_CONTEXT_UPDATED",
                          {"keys": list(context.keys())})

    def update_batch_state(
        self,
        batch_id: str,
        state: BatchState,
        summary: Optional[Dict[str, Any]] = None
    ) -> None:
        now = datetime.now().isoformat()
        with self._conn() as conn:
            if summary is not None:
                conn.execute(
                    """UPDATE batches
                       SET state = ?, updated_at = ?, summary_json = ?
                       WHERE id = ?""",
                    (state.value, now, json.dumps(summary, ensure_ascii=False), batch_id)
                )
            else:
                conn.execute(
                    """UPDATE batches
                       SET state = ?, updated_at = ?
                       WHERE id = ?""",
                    (state.value, now, batch_id)
                )
            self._log_event(conn, batch_id, None, "BATCH_STATE_CHANGED",
                          {"state": state.value, "summary": summary})

    def add_item(
        self,
        batch_id: str,
        index_num: int,
        input_data: Dict[str, Any],
        item_id: Optional[str] = None
    ) -> str:
        iid = item_id or str(uuid.uuid4())
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO items (id, batch_id, index_num, state, input_json)
                   VALUES (?, ?, ?, ?, ?)""",
                (iid, batch_id, index_num, ItemState.PENDING.value,
                 json.dumps(input_data, ensure_ascii=False))
            )
            self._log_event(conn, batch_id, iid, "ITEM_ADDED", {"index": index_num})
        return iid

    def get_items(self, batch_id: str) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT * FROM items
                   WHERE batch_id = ?
                   ORDER BY index_num""",
                (batch_id,)
            ).fetchall()
        return [self._row_to_item(r) for r in rows]

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM items WHERE id = ?", (item_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_item(row)

    def update_item(
        self,
        item_id: str,
        state: ItemState,
        output: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT batch_id FROM items WHERE id = ?", (item_id,)
            ).fetchone()
            if not row:
                return
            batch_id = row["batch_id"]
            conn.execute(
                """UPDATE items
                   SET state = ?, output_json = ?, error = ?
                   WHERE id = ?""",
                (state.value,
                 json.dumps(output, ensure_ascii=False) if output else None,
                 error,
                 item_id)
            )
            self._log_event(conn, batch_id, item_id, "ITEM_STATE_CHANGED",
                          {"state": state.value, "error": error})

    def log_event(
        self,
        batch_id: Optional[str],
        event: str,
        details: Optional[Dict[str, Any]] = None,
        item_id: Optional[str] = None
    ) -> None:
        with self._conn() as conn:
            self._log_event(conn, batch_id, item_id, event, details)

    def _log_event(
        self,
        conn: sqlite3.Connection,
        batch_id: Optional[str],
        item_id: Optional[str],
        event: str,
        details: Optional[Dict[str, Any]]
    ) -> None:
        conn.execute(
            """INSERT INTO audit_log (batch_id, item_id, event, timestamp, details_json)
               VALUES (?, ?, ?, ?, ?)""",
            (batch_id, item_id, event, datetime.now().isoformat(),
             json.dumps(details or {}, ensure_ascii=False))
        )

    def get_audit_log(self, batch_id: str) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT * FROM audit_log
                   WHERE batch_id = ?
                   ORDER BY id""",
                (batch_id,)
            ).fetchall()
        return [
            {
                "id": r["id"],
                "batch_id": r["batch_id"],
                "item_id": r["item_id"],
                "event": r["event"],
                "timestamp": r["timestamp"],
                "details": json.loads(r["details_json"] or "{}")
            }
            for r in rows
        ]

    def list_batches(
        self,
        skill: Optional[str] = None,
        state: Optional[BatchState] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM batches"
        conditions = []
        params: List[Any] = []
        if skill:
            conditions.append("skill = ?")
            params.append(skill)
        if state:
            conditions.append("state = ?")
            params.append(state.value)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_batch(r) for r in rows]

    def _row_to_batch(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "skill": row["skill"],
            "state": row["state"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "context": json.loads(row["context_json"] or "{}"),
            "summary": json.loads(row["summary_json"] or "{}")
        }

    def _row_to_item(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "batch_id": row["batch_id"],
            "index_num": row["index_num"],
            "state": row["state"],
            "input": json.loads(row["input_json"] or "{}"),
            "output": json.loads(row["output_json"] or "{}") if row["output_json"] else None,
            "error": row["error"]
        }
