"""dexter.skills.batch.tools — imports desde main.py (shims).

⚠️  Las implementaciones reales viven en main.py, NO aquí.
Esto evita circular imports durante el auto-descubrimiento de skills.
Si modificás una implementación, editala en main.py también.
"""
from main import (
    tool_crear_template_csv,
    tool_procesar_csv_depositos,
    tool_depositar_lote_csv,
)
