# -*- coding: utf-8 -*-
"""
Motor de Clasificación de Bank Feed para Dexter.

Estrategia de matching (en orden de prioridad):
1. Match exacto en histórico (confidence 100%)
2. Regex patterns aprendidos del usuario (confidence 95%)
3. Fuzzy match con SequenceMatcher ≥ 0.85 (confidence 68-80%)
4. Fuzzy match débil 0.70-0.85 (confidence 42-60%)
5. Default sugerido por monto (confidence 10-15%)

API pública (compatible con versión anterior):
- tool_analyze_bank_feed_for_classification
- tool_record_bank_feed_classification
- tool_get_classification_history_stats
- tool_find_pattern_for_transaction

Funciones nuevas:
- normalize_description
- classify_transaction (núcleo del motor)
- BankFeedClassificationEngine.classify() (wrapper de clase)
"""
import json
import os
import re
from collections import Counter
from datetime import datetime
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

CLASSIFICATION_HISTORY_FILE = "data/bank_feed_classification_history.json"

CONFIDENCE_EXACT = 100
CONFIDENCE_REGEX = 95
CONFIDENCE_FUZZY_HIGH_BASE = 80
CONFIDENCE_FUZZY_LOW_BASE = 60
CONFIDENCE_DEFAULT_SMALL_EXPENSE = 15
CONFIDENCE_DEFAULT_MID_EXPENSE = 12
CONFIDENCE_DEFAULT_LARGE_EXPENSE = 10
CONFIDENCE_DEFAULT_INCOME = 15

FUZZY_HIGH_THRESHOLD = 0.85
FUZZY_LOW_THRESHOLD = 0.70

AMOUNT_SMALL_THRESHOLD = 100
AMOUNT_MID_THRESHOLD = 1000


def normalize_description(description: str) -> str:
    """
    Normaliza una descripción para matching robusto.

    Pasos:
    1. Lowercase
    2. Quitar punctuation
    3. Quitar números (generalmente son IDs, no semánticos)
    4. Colapsar espacios múltiples
    """
    if not description:
        return ""
    s = description.lower()
    s = re.sub(r'[^\w\s]', ' ', s, flags=re.UNICODE)
    s = re.sub(r'\d+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def _default_account_for_amount(amount: float) -> Tuple[str, int]:
    """
    Sugiere una cuenta default basada en el monto cuando no hay match.

    Returns: (account_name, confidence)
    """
    abs_amount = abs(amount)
    if amount > 0:
        return "Sales Income", CONFIDENCE_DEFAULT_INCOME
    if abs_amount < AMOUNT_SMALL_THRESHOLD:
        return "Office Supplies", CONFIDENCE_DEFAULT_SMALL_EXPENSE
    if abs_amount < AMOUNT_MID_THRESHOLD:
        return "Operating Expenses", CONFIDENCE_DEFAULT_MID_EXPENSE
    return "Major Purchases", CONFIDENCE_DEFAULT_LARGE_EXPENSE


def _exact_match(normalized: str, history: Dict) -> Optional[Dict]:
    """Busca match exacto en el histórico."""
    for c in history.get("classifications", []):
        if normalize_description(c.get("description", "")) == normalized:
            return {
                "account_id": c.get("account_id"),
                "account_name": c.get("account_name"),
                "confidence": CONFIDENCE_EXACT,
                "reasoning": "Match exacto con clasificación previa",
                "match_type": "exact"
            }
    return None


def _regex_match(normalized: str, history: Dict) -> Optional[Dict]:
    """Busca contra los regex patterns aprendidos."""
    for pattern, account in history.get("patterns", {}).items():
        try:
            if re.search(pattern, normalized):
                return {
                    "account_id": account.get("account_id"),
                    "account_name": account.get("account_name"),
                    "confidence": CONFIDENCE_REGEX,
                    "reasoning": f"Match con patrón aprendido '{pattern}'",
                    "match_type": "regex"
                }
        except re.error:
            continue
    return None


def _fuzzy_match(normalized: str, history: Dict) -> Optional[Dict]:
    """Busca fuzzy match con SequenceMatcher."""
    best = None
    best_ratio = 0.0
    for c in history.get("classifications", []):
        c_norm = normalize_description(c.get("description", ""))
        ratio = SequenceMatcher(None, normalized, c_norm).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best = c
    if not best or best_ratio < FUZZY_LOW_THRESHOLD:
        return None
    if best_ratio >= FUZZY_HIGH_THRESHOLD:
        confidence = int(best_ratio * CONFIDENCE_FUZZY_HIGH_BASE)
        match_type = "fuzzy"
    else:
        confidence = int(best_ratio * CONFIDENCE_FUZZY_LOW_BASE)
        match_type = "fuzzy_weak"
    return {
        "account_id": best.get("account_id"),
        "account_name": best.get("account_name"),
        "confidence": confidence,
        "reasoning": f"Fuzzy match {best_ratio:.0%} con clasificación previa",
        "match_type": match_type
    }


def classify_transaction(description: str, amount: float, history: Dict) -> Dict:
    """
    Clasifica una transacción usando el motor de matching en cascada.

    Args:
        description: Texto de la transacción (ej: "AMZN Mktp US*MK4J2")
        amount: Monto (negativo=gasto, positivo=ingreso)
        history: Dict con 'classifications' (lista) y 'patterns' (dict)

    Returns:
        Dict con keys: account_id, account_name, confidence, reasoning, match_type
    """
    normalized = normalize_description(description)

    if not normalized:
        account_name, confidence = _default_account_for_amount(amount)
        return {
            "account_id": None,
            "account_name": account_name,
            "confidence": confidence,
            "reasoning": "Descripción vacía, usando default",
            "match_type": "default"
        }

    match = _exact_match(normalized, history)
    if match:
        return match

    match = _regex_match(normalized, history)
    if match:
        return match

    match = _fuzzy_match(normalized, history)
    if match:
        return match

    account_name, confidence = _default_account_for_amount(amount)
    return {
        "account_id": None,
        "account_name": account_name,
        "confidence": confidence,
        "reasoning": "Sin match, usando default por monto",
        "match_type": "default"
    }


class BankFeedClassificationEngine:
    """Motor de clasificación con persistencia."""

    def __init__(self, history_file: str = CLASSIFICATION_HISTORY_FILE):
        self.history_file = history_file
        self.history = self.load_history()

    def load_history(self) -> Dict:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if "classifications" not in data:
                    data["classifications"] = []
                if "patterns" not in data:
                    data["patterns"] = {}
                return data
            except (json.JSONDecodeError, OSError):
                return {"classifications": [], "patterns": {}}
        return {"classifications": [], "patterns": {}}

    def save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def record_classification(
        self,
        description: str,
        account_id: str,
        account_name: str,
        amount: float,
        date: str,
        vendor: Optional[str] = None,
        qb_suggestion: Optional[str] = None
    ):
        classification = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "account_id": account_id,
            "account_name": account_name,
            "amount": amount,
            "date": date
        }
        if vendor is not None:
            classification["vendor"] = vendor
        if qb_suggestion is not None:
            classification["qb_suggestion"] = qb_suggestion
        self.history["classifications"].append(classification)
        self.save_history()

    def record_pattern(self, pattern: str, account_id: str, account_name: str):
        """Registra un regex pattern aprendido."""
        self.history["patterns"][pattern] = {
            "account_id": account_id,
            "account_name": account_name
        }
        self.save_history()

    def classify(self, description: str, amount: float) -> Dict:
        """Wrapper que clasifica una transacción contra el historial actual."""
        return classify_transaction(description, amount, self.history)

    def analyze_pending_transactions(
        self,
        transactions: List[Dict],
        min_confidence: float = 0.7
    ) -> Dict:
        """
        Analiza una lista de transacciones y las agrupa por nivel de confianza.

        Returns:
            Dict con keys: total, high_confidence, medium_confidence,
                           low_confidence, no_match
        """
        high = []
        medium = []
        low = []
        no_match = []

        for txn in transactions:
            description = txn.get("description", "")
            amount = float(txn.get("amount", 0))
            result = self.classify(description, amount)
            conf_pct = result["confidence"] / 100.0
            enriched = {
                "description": description,
                "amount": amount,
                "classification": result
            }
            if conf_pct >= min_confidence:
                if result["confidence"] >= 80:
                    high.append(enriched)
                elif result["confidence"] >= 50:
                    medium.append(enriched)
                else:
                    low.append(enriched)
            else:
                no_match.append(enriched)

        return {
            "total": len(transactions),
            "high_confidence": high,
            "medium_confidence": medium,
            "low_confidence": low,
            "no_match": no_match
        }


_classification_engine = BankFeedClassificationEngine()


def tool_analyze_bank_feed_for_classification(
    account_name: str,
    transactions: Optional[List[Dict]] = None,
    min_confidence: float = 0.7
) -> dict:
    global _classification_engine
    if transactions is None:
        return {"success": False, "message": "Necesito transacciones para analizar"}
    results = _classification_engine.analyze_pending_transactions(transactions, min_confidence)
    return {"success": True, "account": account_name, "analysis": results}


def tool_record_bank_feed_classification(
    description: str,
    account_id: str,
    account_name: str,
    amount: float,
    date: str,
    vendor: Optional[str] = None,
    qb_suggestion: Optional[str] = None
) -> dict:
    global _classification_engine
    _classification_engine.record_classification(
        description, account_id, account_name, amount, date, vendor, qb_suggestion
    )
    return {"success": True, "message": "Clasificación registrada"}


def tool_get_classification_history_stats() -> dict:
    global _classification_engine
    total = len(_classification_engine.history["classifications"])
    return {
        "success": True,
        "total_classifications": total,
        "patterns_learned": len(_classification_engine.history["patterns"])
    }


def tool_find_pattern_for_transaction(description: str) -> dict:
    """
    Busca un patrón en el historial que coincida con la descripción.
    Returns match_found=True si encuentra match con confidence >= 50%.
    """
    global _classification_engine
    result = _classification_engine.classify(description, 0.0)
    if result["confidence"] >= 50:
        return {
            "success": True,
            "match_found": True,
            "classification": result
        }
    return {
        "success": True,
        "match_found": False,
        "message": "Sin patrón con confidence suficiente"
    }
