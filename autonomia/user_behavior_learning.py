# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from typing import Dict, List

BEHAVIOR_LEARNING_FILE = "user_behavior_learning.json"

class UserBehaviorLearningEngine:
    def __init__(self, learning_file: str = BEHAVIOR_LEARNING_FILE):
        self.learning_file = learning_file
        self.data = self.load_learning_data()

    def load_learning_data(self) -> Dict:
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._init_structure()
        return self._init_structure()

    def _init_structure(self) -> Dict:
        return {
            "preferences": {"favorite_accounts": {}, "frequent_vendors": {}},
            "report_patterns": {"frequent_reports": []},
            "conversation_context": {"recent_topics": [], "active_tasks": []},
            "learning_stats": {"total_interactions": 0, "reports_generated": 0}
        }

    def save_learning_data(self):
        with open(self.learning_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def learn_account_preference(self, account_name: str, context: str = "general"):
        key = f"{account_name}:{context}"
        if key not in self.data["preferences"]["favorite_accounts"]:
            self.data["preferences"]["favorite_accounts"][key] = 0
        self.data["preferences"]["favorite_accounts"][key] += 1
        self.save_learning_data()

    def update_conversation_context(self, topic: str, action: str = None):
        self.data["conversation_context"]["recent_topics"].append({
            "topic": topic, "timestamp": datetime.now().isoformat()
        })
        if len(self.data["conversation_context"]["recent_topics"]) > 20:
            self.data["conversation_context"]["recent_topics"] = self.data["conversation_context"]["recent_topics"][-20:]
        self.data["learning_stats"]["total_interactions"] += 1
        self.save_learning_data()

_learning_engine = UserBehaviorLearningEngine()

def tool_learn_from_interaction(interaction_type: str, details: Dict, context: str = "general") -> dict:
    global _learning_engine
    if interaction_type == "account_use":
        _learning_engine.learn_account_preference(details["account_name"], context)
    _learning_engine.update_conversation_context(interaction_type, str(details))
    return {"success": True, "learned": True}

def tool_get_user_suggestions() -> dict:
    global _learning_engine
    stats = {"total_interactions": _learning_engine.data["learning_stats"]["total_interactions"]}
    return {"success": True, "suggestion": None, "stats": stats}

def tool_record_user_correction(wrong: str, correct: str, context: str) -> dict:
    return {"success": True, "message": "Corrección registrada"}

def tool_get_conversation_context() -> dict:
    global _learning_engine
    recent = _learning_engine.data["conversation_context"]["recent_topics"][-10:]
    return {"success": True, "recent_topics": [t["topic"] for t in recent]}
