"""dexter.skills.amortizacion — Distribución de gastos en el tiempo."""
from typing import Any, Dict, List

SCHEMA: List[Dict[str, Any]] = []
FUNCTIONS: Dict[str, Any] = {}
KEYWORDS: List[str] = ["amortizar", "distribuir", "prorratear", "prepaid", "diferir"]

# Lazy import (las funciones están en main.py para backward compat)
def _lazy_load():
    global SCHEMA, FUNCTIONS
    if not FUNCTIONS:
        from main import tool_calcular_distribucion, tool_ejecutar_distribucion
        FUNCTIONS = {
            "calcular_distribucion": tool_calcular_distribucion,
            "ejecutar_distribucion": tool_ejecutar_distribucion,
        }
        SCHEMA = [
            {
                "type": "function",
                "function": {
                    "name": "calcular_distribucion",
                    "description": "Calcula un plan de amortizacion para distribuir un gasto en N meses. Paso 1 de 2. Pregunta: cuenta puente, tipo distribucion, dia del mes, vendor.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "monto": {"type": "number", "description": "Monto total"},
                            "cuenta_origen": {"type": "string", "description": "Cuenta de gasto"},
                            "meses": {"type": "integer", "description": "Número de meses"},
                            "cuenta_puente": {"type": "string", "description": "Cuenta puente"},
                            "fecha_inicio": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                            "distribucion": {"type": "string", "description": "equitativa o personalizada"},
                            "montos_personalizados": {"type": "array", "items": {"type": "number"}},
                            "dia_mes": {"type": "integer", "description": "1=principio, 15=mitad, 28=final"},
                            "vendor": {"type": "string", "description": "Proveedor (opcional)"},
                        },
                        "required": ["monto", "cuenta_origen"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "ejecutar_distribucion",
                    "description": "Ejecuta el plan de amortizacion. Paso 2 de 2. Crea journal entries en QBO.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "plan": {"type": "object", "description": "Plan de calcular_distribucion"},
                        },
                        "required": ["plan"],
                    },
                },
            },
        ]

_lazy_load()
