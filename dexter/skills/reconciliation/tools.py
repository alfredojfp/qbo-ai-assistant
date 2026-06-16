"""dexter.skills.reconciliation.tools — imports desde main.py (shims).

⚠️  Las implementaciones reales viven en main.py, NO aquí.
Esto evita circular imports durante el auto-descubrimiento de skills.
Si modificás una implementación, editala en main.py también.
"""
from main import (
    tool_procesar_reconciliacion_bancaria,
    tool_taggear_reconciliacion,
    tool_limpiar_tags_reconciliacion,
)
