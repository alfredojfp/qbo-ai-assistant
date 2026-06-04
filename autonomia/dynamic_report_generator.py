# -*- coding: utf-8 -*-
"""
Generador de reportes dinámicos con detección de fechas en lenguaje natural.

Soporta expresiones como:
- "este mes", "mes pasado", "este año", "año pasado"
- "este trimestre", "último trimestre", "Q1", "Q3 2025"
- "última semana", "últimos 7 días", "últimos 30 días"
- "hoy", "ayer"
- "enero", "febrero", ..., "diciembre" (mes actual)
- "2024", "2026-03"

Y detecta el tipo de reporte:
- P&L / pérdidas y ganancias → ProfitAndLoss
- Balance / balance general → BalanceSheet
- Flujo de caja → CashFlow
- Trial balance / balance de comprobación → TrialBalance
"""
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

# dateutil es opcional; si no está, usamos un fallback propio
try:
    from dateutil.relativedelta import relativedelta
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False


MONTHS_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

MONTHS_EN = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

REPORT_TYPES = {
    "ProfitAndLoss": ["p&l", "p y l", "pnl", "perdidas y ganancias",
                      "pérdidas y ganancias", "profit", "income", "ingresos y gastos"],
    # TrialBalance debe ir ANTES de BalanceSheet porque "balance de comprobación"
    # contiene "balance" como substring.
    "TrialBalance": ["trial", "balance de comprobacion", "balance de comprobación",
                      "comprobacion", "comprobación"],
    "BalanceSheet": ["balance sheet", "balance general", "estado de situacion",
                     "estado de situación", "activos y pasivos", "balance"],
    "CashFlow": ["flujo de caja", "flujo", "cash flow", "cashflow"],
}


def _add_months(dt: datetime, months: int) -> datetime:
    """Agrega N meses a una fecha (fallback si dateutil no está)."""
    if HAS_DATEUTIL:
        return dt + relativedelta(months=months)
    month = dt.month + months
    year = dt.year + (month - 1) // 12
    month = ((month - 1) % 12) + 1
    return dt.replace(year=year, month=month)


def _last_day_of_month(year: int, month: int) -> int:
    """Último día del mes (28-31)."""
    if month == 12:
        return 31
    return (datetime(year, month + 1, 1) - timedelta(days=1)).day


class DynamicReportGenerator:
    """Generador de reportes con detección de fechas y tipo."""

    def parse_date_expression(self, expression: str) -> Tuple[str, str]:
        today = datetime.now()
        expr_lower = expression.lower().strip()
        # Quitar acentos simples
        expr_normalized = (
            expr_lower.replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
        )

        # Mes específico en formato ISO YYYY-MM (checkear ANTES del año)
        iso_month_match = re.search(r'\b(20\d{2})-(0[1-9]|1[0-2])\b', expression)
        if iso_month_match:
            year = int(iso_month_match.group(1))
            month = int(iso_month_match.group(2))
            start = f"{year:04d}-{month:02d}-01"
            end = f"{year:04d}-{month:02d}-{_last_day_of_month(year, month):02d}"
            return start, end

        # Q1/Q2/Q3/Q4 con o sin año
        q_match = re.search(r'q([1-4])', expr_normalized, re.I)
        if q_match:
            q = int(q_match.group(1))
            year_match = re.search(r'\b(20\d{2})\b', expression)
            year = int(year_match.group(1)) if year_match else today.year
            start_month = (q - 1) * 3 + 1
            end_month = q * 3
            start = f"{year:04d}-{start_month:02d}-01"
            end = f"{year:04d}-{end_month:02d}-{_last_day_of_month(year, end_month):02d}"
            return start, end

        # Mes específico en español/inglés
        for month_name, month_num in {**MONTHS_ES, **MONTHS_EN}.items():
            if month_name in expr_normalized:
                # Detectar año (opcional)
                year_match = re.search(r'\b(20\d{2})\b', expression)
                year = int(year_match.group(1)) if year_match else today.year
                last_day = _last_day_of_month(year, month_num)
                start = f"{year:04d}-{month_num:02d}-01"
                end = f"{year:04d}-{month_num:02d}-{last_day:02d}"
                return start, end

        # Año específico
        year_match = re.search(r'\b(20\d{2})\b', expression)
        if year_match:
            year = int(year_match.group(1))
            return f"{year:04d}-01-01", f"{year:04d}-12-31"

        # "últimos N días" (usar expr_normalized que no tiene tildes)
        n_days_match = re.search(r'ultimos?\s+(\d+)\s+dias?|last\s+(\d+)\s+days?', expr_normalized, re.I)
        if n_days_match:
            n = int(n_days_match.group(1) or n_days_match.group(2))
            start_date = today - timedelta(days=n - 1)
            return (
                start_date.strftime('%Y-%m-%d'),
                today.strftime('%Y-%m-%d'),
            )

        # "última semana" / "semana pasada"
        if any(kw in expr_normalized for kw in ["ultima semana", "semana pasada", "last week"]):
            last_monday = today - timedelta(days=today.weekday() + 7)
            last_sunday = last_monday + timedelta(days=6)
            return (
                last_monday.strftime('%Y-%m-%d'),
                last_sunday.strftime('%Y-%m-%d'),
            )

        # "hoy"
        if expr_normalized in ("hoy", "today"):
            return today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')

        # "ayer"
        if expr_normalized in ("ayer", "yesterday"):
            y = today - timedelta(days=1)
            return y.strftime('%Y-%m-%d'), y.strftime('%Y-%m-%d')

        # "este mes" / "mes actual"
        if any(kw in expr_normalized for kw in ["este mes", "mes actual", "this month"]):
            first = today.replace(day=1)
            last = _add_months(first, 1) - timedelta(days=1)
            return first.strftime('%Y-%m-%d'), last.strftime('%Y-%m-%d')

        # "mes pasado" / "último mes"
        if any(kw in expr_normalized for kw in ["mes pasado", "ultimo mes", "last month"]):
            first_this = today.replace(day=1)
            first_prev = _add_months(first_this, -1)
            last_prev = first_this - timedelta(days=1)
            return first_prev.strftime('%Y-%m-%d'), last_prev.strftime('%Y-%m-%d')

        # "este año"
        if any(kw in expr_normalized for kw in ["este año", "año actual", "this year"]):
            return f"{today.year:04d}-01-01", f"{today.year:04d}-12-31"

        # "año pasado" / "último año"
        if any(kw in expr_normalized for kw in ["año pasado", "ultimo año", "last year"]):
            last_year = today.year - 1
            return f"{last_year:04d}-01-01", f"{last_year:04d}-12-31"

        # "este trimestre"
        if any(kw in expr_normalized for kw in ["este trimestre", "trimestre actual", "this quarter"]):
            q = (today.month - 1) // 3
            start_month = q * 3 + 1
            end_month = (q + 1) * 3
            start = today.replace(month=start_month, day=1)
            end_month_last_day = _last_day_of_month(today.year, end_month)
            end = today.replace(month=end_month, day=end_month_last_day)
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

        # "último trimestre" / "trimestre pasado"
        if any(kw in expr_normalized for kw in ["ultimo trimestre", "trimestre pasado", "last quarter"]):
            current_q = (today.month - 1) // 3
            prev_q = (current_q - 1) % 4
            year = today.year if current_q > 0 else today.year - 1
            start_month = prev_q * 3 + 1
            end_month = prev_q * 3 + 3
            start = today.replace(year=year, month=start_month, day=1)
            end_month_last_day = _last_day_of_month(year, end_month)
            end = today.replace(year=year, month=end_month, day=end_month_last_day)
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

        # Default: mes actual
        first = today.replace(day=1)
        last = _add_months(first, 1) - timedelta(days=1)
        return first.strftime('%Y-%m-%d'), last.strftime('%Y-%m-%d')

    def detect_report_type(self, user_request: str) -> str:
        """Detecta el tipo de reporte a generar."""
        expr = user_request.lower()
        expr_normalized = (
            expr.replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
        )
        for report_type, keywords in REPORT_TYPES.items():
            for kw in keywords:
                kw_normalized = (
                    kw.replace("á", "a")
                    .replace("é", "e")
                    .replace("í", "i")
                    .replace("ó", "o")
                    .replace("ú", "u")
                )
                if kw_normalized in expr_normalized:
                    return report_type
        return "ProfitAndLoss"  # default

    def generate_custom_report(
        self,
        user_request: str,
        filters: Optional[Dict] = None,
    ) -> Dict:
        start_date, end_date = self.parse_date_expression(user_request)
        report_type = self.detect_report_type(user_request)
        accounting_method = (filters or {}).get("accounting_method", "Accrual")

        token = os.getenv("QB_ACCESS_TOKEN")
        realm = os.getenv("QB_REALM_ID")
        if not token:
            return {
                "success": False,
                "error": "QB_ACCESS_TOKEN no configurado en .env",
            }
        if not realm:
            return {
                "success": False,
                "error": "QB_REALM_ID no configurado en .env",
            }

        import requests
        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm}/reports/{report_type}"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "accounting_method": accounting_method,
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "report_type": report_type,
                    "period": f"{start_date} a {end_date}",
                    "start_date": start_date,
                    "end_date": end_date,
                    "accounting_method": accounting_method,
                    "data": data,
                }
            return {
                "success": False,
                "error": f"QBO API error: HTTP {response.status_code}",
                "details": response.text[:500],
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error contacting QBO: {e}",
            }


_report_generator = DynamicReportGenerator()


def tool_generate_custom_report(
    user_request: str,
    filters: Optional[dict] = None,
) -> dict:
    """Genera un reporte personalizado interpretando lenguaje natural."""
    return _report_generator.generate_custom_report(user_request, filters)


def tool_parse_date_expression(expression: str) -> dict:
    """Parsea una expresión de fecha en lenguaje natural a start/end."""
    start, end = _report_generator.parse_date_expression(expression)
    return {
        "success": True,
        "expression": expression,
        "start_date": start,
        "end_date": end,
    }
