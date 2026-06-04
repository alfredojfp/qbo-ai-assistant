"""dexter.tools.reports — 5 tools."""
from typing import Any, Dict, List

from main import (
    tool_generar_reporte_pl,
    tool_generar_balance_sheet,
    tool_guardar_reporte,
    tool_cargar_reporte,
    tool_listar_reportes_guardados,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'generar_reporte_pl', 'description': 'Genera reporte de Profit & Loss (P&L / Estado de Resultados).', 'parameters': {'type': 'object', 'properties': {'fecha_inicio': {'type': 'string', 'description': 'Fecha inicio YYYY-MM-DD'}, 'fecha_fin': {'type': 'string', 'description': 'Fecha fin YYYY-MM-DD'}, 'metodo': {'type': 'string', 'enum': ['Accrual', 'Cash'], 'default': 'Accrual'}}, 'required': ['fecha_inicio', 'fecha_fin']}}},
        {'type': 'function', 'function': {'name': 'generar_balance_sheet', 'description': 'Genera reporte de Balance Sheet (Balance General).', 'parameters': {'type': 'object', 'properties': {'fecha': {'type': 'string', 'description': 'Fecha del balance YYYY-MM-DD'}, 'metodo': {'type': 'string', 'enum': ['Accrual', 'Cash'], 'default': 'Accrual'}}, 'required': ['fecha']}}},
        {'type': 'function', 'function': {'name': 'guardar_reporte', 'description': 'Guarda configuración de un reporte para uso futuro.', 'parameters': {'type': 'object', 'properties': {'nombre': {'type': 'string', 'description': 'Nombre para identificar el reporte'}, 'config': {'type': 'object', 'description': 'Configuración del reporte'}}, 'required': ['nombre', 'config']}}},
        {'type': 'function', 'function': {'name': 'cargar_reporte', 'description': 'Carga configuración de un reporte guardado previamente.', 'parameters': {'type': 'object', 'properties': {'nombre': {'type': 'string'}}, 'required': ['nombre']}}},
        {'type': 'function', 'function': {'name': 'listar_reportes_guardados', 'description': 'Lista todos los reportes guardados por el usuario.', 'parameters': {'type': 'object', 'properties': {}}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["reporte", "p&l", "balance", "estado", "guardar reporte", "cargar reporte"]
FUNCTIONS: Dict[str, Any] = {
    "generar_reporte_pl": tool_generar_reporte_pl,
    "generar_balance_sheet": tool_generar_balance_sheet,
    "guardar_reporte": tool_guardar_reporte,
    "cargar_reporte": tool_cargar_reporte,
    "listar_reportes_guardados": tool_listar_reportes_guardados,
}
