# -*- coding: utf-8 -*-
"""
Motor de aprendizaje de comportamiento del usuario.

Aprende de:
- Cuentas favoritas (Bank, Checking, etc.) por contexto
- Vendors frecuentes (ACME Corp, Tech Supply, etc.) por contexto
- Reportes generados (P&L Mensual, etc.)
- Correcciones del usuario (cuando el sistema se equivoca)

Persiste en `user_behavior_learning.json` (regenerable).
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


BEHAVIOR_LEARNING_FILE = "user_behavior_learning.json"

MAX_RECENT_TOPICS = 20
MAX_CORRECTIONS = 100
SUGGESTIONS_LIMIT = 5
CORRECTION_THRESHOLD = 2  # Cuántas veces para sugerir una corrección


class UserBehaviorLearningEngine:
    """Motor de aprendizaje de comportamiento."""

    def __init__(self, learning_file: str = BEHAVIOR_LEARNING_FILE):
        self.learning_file = learning_file
        self.max_corrections = MAX_CORRECTIONS
        self.data = self.load_learning_data()

    def load_learning_data(self) -> Dict:
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                return self._merge_with_defaults(loaded)
            except (json.JSONDecodeError, IOError):
                return self._init_structure()
        return self._init_structure()

    @staticmethod
    def _init_structure() -> Dict:
        return {
            "preferences": {
                "favorite_accounts": {},
                "frequent_vendors": {},
            },
            "report_patterns": {"frequent_reports": []},
            "conversation_context": {
                "recent_topics": [],
                "active_tasks": [],
            },
            "corrections": {"entries": []},
            "learning_stats": {
                "total_interactions": 0,
                "reports_generated": 0,
                "corrections_recorded": 0,
            },
        }

    @staticmethod
    def _merge_with_defaults(loaded: Dict) -> Dict:
        """Asegura que todos los campos esperados existan en el JSON cargado."""
        defaults = UserBehaviorLearningEngine._init_structure()
        for key, default in defaults.items():
            if key not in loaded:
                loaded[key] = default
            elif isinstance(default, dict):
                for sub_key, sub_default in default.items():
                    loaded[key].setdefault(sub_key, sub_default)
        return loaded

    def save_learning_data(self):
        os.makedirs(
            os.path.dirname(os.path.abspath(self.learning_file)) or ".",
            exist_ok=True,
        )
        with open(self.learning_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def learn_account_preference(self, account_name: str, context: str = "general"):
        key = f"{account_name}:{context}"
        accounts = self.data["preferences"]["favorite_accounts"]
        accounts[key] = accounts.get(key, 0) + 1
        self.save_learning_data()

    def learn_vendor_preference(self, vendor_name: str, context: str = "general"):
        key = f"{vendor_name}:{context}"
        vendors = self.data["preferences"]["frequent_vendors"]
        vendors[key] = vendors.get(key, 0) + 1
        self.save_learning_data()

    def learn_report_usage(self, report_config: Dict[str, Any]):
        """Registra que se generó un reporte con esta config."""
        name = report_config.get("name", "")
        if not name:
            return
        reports = self.data["report_patterns"]["frequent_reports"]
        existing = next(
            (r for r in reports if r.get("name") == name
             and r.get("period") == report_config.get("period")),
            None,
        )
        if existing:
            existing["count"] = existing.get("count", 0) + 1
            existing["last_used"] = datetime.now().isoformat()
        else:
            reports.append({
                "name": name,
                "period": report_config.get("period"),
                "count": 1,
                "last_used": datetime.now().isoformat(),
            })
        self.data["learning_stats"]["reports_generated"] += 1
        self.save_learning_data()

    def record_correction(
        self,
        wrong: str,
        correct: str,
        context: str = "general",
    ):
        """Registra una corrección del usuario."""
        entry = {
            "wrong": wrong,
            "correct": correct,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }
        entries = self.data["corrections"]["entries"]
        entries.append(entry)
        # Mantener solo las últimas N
        if len(entries) > self.max_corrections:
            self.data["corrections"]["entries"] = entries[-self.max_corrections:]
        self.data["learning_stats"]["corrections_recorded"] += 1
        self.save_learning_data()

    def update_conversation_context(
        self,
        topic: str,
        action: Optional[str] = None,
    ):
        """Registra un topic reciente."""
        self.data["conversation_context"]["recent_topics"].append({
            "topic": topic,
            "action": action,
            "timestamp": datetime.now().isoformat(),
        })
        # Mantener solo las últimas N
        if len(self.data["conversation_context"]["recent_topics"]) > MAX_RECENT_TOPICS:
            self.data["conversation_context"]["recent_topics"] = (
                self.data["conversation_context"]["recent_topics"][-MAX_RECENT_TOPICS:]
            )
        self.data["learning_stats"]["total_interactions"] += 1
        self.save_learning_data()

    def add_active_task(self, task: str):
        """Marca una tarea como activa."""
        tasks = self.data["conversation_context"]["active_tasks"]
        if task not in tasks:
            tasks.append(task)
        self.save_learning_data()

    def complete_active_task(self, task: str):
        """Marca una tarea como completada."""
        tasks = self.data["conversation_context"]["active_tasks"]
        if task in tasks:
            tasks.remove(task)
        self.save_learning_data()

    def get_suggestions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna sugerencias basadas en patrones aprendidos."""
        accounts_sorted = sorted(
            self.data["preferences"]["favorite_accounts"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:SUGGESTIONS_LIMIT]
        vendors_sorted = sorted(
            self.data["preferences"]["frequent_vendors"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:SUGGESTIONS_LIMIT]
        reports_sorted = sorted(
            self.data["report_patterns"]["frequent_reports"],
            key=lambda x: x.get("count", 0),
            reverse=True,
        )[:SUGGESTIONS_LIMIT]
        # Agrupar correcciones por (wrong, context) y sugerir si >= threshold
        from collections import Counter
        correction_counter = Counter()
        correction_lookup = {}
        for entry in self.data["corrections"]["entries"]:
            key = (entry["wrong"], entry["context"])
            correction_counter[key] += 1
            correction_lookup[key] = entry["correct"]
        corrections_to_suggest = [
            {
                "wrong": wrong,
                "context": ctx,
                "correct": correction_lookup[(wrong, ctx)],
                "count": count,
            }
            for (wrong, ctx), count in correction_counter.items()
            if count >= CORRECTION_THRESHOLD
        ]
        corrections_to_suggest.sort(key=lambda x: x["count"], reverse=True)
        return {
            "accounts": [
                {"name": name, "count": count}
                for name, count in accounts_sorted
            ],
            "vendors": [
                {"name": name, "count": count}
                for name, count in vendors_sorted
            ],
            "reports": reports_sorted,
            "corrections": corrections_to_suggest,
        }


_learning_engine: Optional[UserBehaviorLearningEngine] = None


def _get_engine() -> UserBehaviorLearningEngine:
    """Lazy singleton accessor."""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = UserBehaviorLearningEngine()
    return _learning_engine


def reset_engine(path: str = BEHAVIOR_LEARNING_FILE):
    """Resetea el singleton a una nueva instancia (útil para tests)."""
    global _learning_engine
    _learning_engine = UserBehaviorLearningEngine(learning_file=path)
    return _learning_engine


def tool_learn_from_interaction(
    interaction_type: str,
    details: Dict,
    context: str = "general",
) -> dict:
    """Aprende de una interacción del usuario."""
    engine = _get_engine()
    if interaction_type == "account_use":
        account_name = details.get("account_name")
        if not account_name:
            return {
                "success": False,
                "error": "Falta 'account_name' en details para account_use",
            }
        engine.learn_account_preference(account_name, context)
    elif interaction_type == "vendor_use":
        vendor_name = details.get("vendor_name")
        if not vendor_name:
            return {
                "success": False,
                "error": "Falta 'vendor_name' en details para vendor_use",
            }
        engine.learn_vendor_preference(vendor_name, context)
    elif interaction_type == "report_use":
        engine.learn_report_usage(details)
    else:
        return {
            "success": False,
            "error": f"Tipo de interacción desconocido: {interaction_type}",
        }
    engine.update_conversation_context(interaction_type, str(details))
    return {"success": True, "learned": True}


def tool_get_user_suggestions() -> dict:
    """Obtiene sugerencias basadas en el comportamiento histórico."""
    engine = _get_engine()
    return {
        "success": True,
        "suggestions": engine.get_suggestions(),
        "stats": engine.data["learning_stats"],
    }


def tool_record_user_correction(
    wrong: str,
    correct: str,
    context: str,
) -> dict:
    """Registra una corrección del usuario."""
    engine = _get_engine()
    engine.record_correction(wrong, correct, context)
    return {
        "success": True,
        "message": "Corrección registrada",
    }


def tool_get_conversation_context() -> dict:
    """Retorna resumen del contexto reciente y tareas activas."""
    engine = _get_engine()
    recent = engine.data["conversation_context"]["recent_topics"][-10:]
    return {
        "success": True,
        "recent_topics": [t["topic"] for t in recent],
        "active_tasks": list(engine.data["conversation_context"]["active_tasks"]),
    }
