# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter
import re

CLASSIFICATION_HISTORY_FILE = "bank_feed_classification_history.json"

class BankFeedClassificationEngine:
    def __init__(self, history_file: str = CLASSIFICATION_HISTORY_FILE):
        self.history_file = history_file
        self.history = self.load_history()

    def load_history(self) -> Dict:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"classifications": [], "patterns": {}}
        return {"classifications": [], "patterns": {}}

    def save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def record_classification(self, description: str, account_id: str, account_name: str, 
                            amount: float, date: str, vendor: str = None, qb_suggestion: str = None):
        classification = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "account_id": account_id,
            "account_name": account_name,
            "amount": amount,
            "date": date
        }
        self.history["classifications"].append(classification)
        self.save_history()

    def analyze_pending_transactions(self, transactions: List[Dict], min_confidence: float = 0.7) -> Dict:
        return {
            "total": len(transactions),
            "high_confidence": [],
            "medium_confidence": [],
            "low_confidence": [],
            "no_match": []
        }

_classification_engine = BankFeedClassificationEngine()

def tool_analyze_bank_feed_for_classification(account_name: str, transactions: List[Dict] = None, 
                                             min_confidence: float = 0.7) -> dict:
    global _classification_engine
    if transactions is None:
        return {"success": False, "message": "Necesito transacciones para analizar"}
    results = _classification_engine.analyze_pending_transactions(transactions, min_confidence)
    return {"success": True, "account": account_name, "analysis": results}

def tool_record_bank_feed_classification(description: str, account_id: str, account_name: str, 
                                        amount: float, date: str, vendor: str = None, 
                                        qb_suggestion: str = None) -> dict:
    global _classification_engine
    _classification_engine.record_classification(description, account_id, account_name, 
                                                amount, date, vendor, qb_suggestion)
    return {"success": True, "message": "Clasificación registrada"}

def tool_get_classification_history_stats() -> dict:
    global _classification_engine
    total = len(_classification_engine.history["classifications"])
    return {"success": True, "total_classifications": total, "patterns_learned": len(_classification_engine.history["patterns"])}

def tool_find_pattern_for_transaction(description: str) -> dict:
    return {"success": True, "match_found": False, "message": "Sin patrón similar"}
