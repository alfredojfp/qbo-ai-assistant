# -*- coding: utf-8 -*-
import requests
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, Tuple
import re
from dotenv import load_dotenv

load_dotenv()

QB_ACCESS_TOKEN = os.getenv('QB_ACCESS_TOKEN')
QB_REALM_ID = os.getenv('QB_REALM_ID')
QB_BASE_URL = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{QB_REALM_ID}"

class DynamicReportGenerator:
    def parse_date_expression(self, expression: str) -> Tuple[str, str]:
        today = datetime.now()
        expr_lower = expression.lower().strip()

        if "este mes" in expr_lower:
            start = today.replace(day=1)
            end = (start + relativedelta(months=1)) - timedelta(days=1)
        elif "mes pasado" in expr_lower:
            start = (today.replace(day=1) - relativedelta(months=1))
            end = today.replace(day=1) - timedelta(days=1)
        elif "este año" in expr_lower:
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        else:
            start = today.replace(day=1)
            end = (start + relativedelta(months=1)) - timedelta(days=1)

        return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

    def generate_custom_report(self, user_request: str, filters: Dict = None) -> Dict:
        start_date, end_date = self.parse_date_expression(user_request)

        return {
            "success": True,
            "report_type": "Profit & Loss",
            "period": f"{start_date} a {end_date}",
            "message": "Reporte generado (versión simplificada)"
        }

_report_generator = DynamicReportGenerator()

def tool_generate_custom_report(user_request: str, filters: dict = None) -> dict:
    global _report_generator
    return _report_generator.generate_custom_report(user_request, filters)

def tool_parse_date_expression(expression: str) -> dict:
    global _report_generator
    start, end = _report_generator.parse_date_expression(expression)
    return {"success": True, "expression": expression, "start_date": start, "end_date": end}
