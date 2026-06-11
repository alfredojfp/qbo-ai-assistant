"""dexter.skills.reconciliation.tools — 3 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

from datetime import datetime
from main import qbo_query
from main import qbo_request

def tool_limpiar_tags_reconciliacion(batch_id: str) -> dict:
    """
    Tool: Limpia los tags BNK-RECON aplicados por un batch previo.
    Lee el reporte del batch y borra los Memo/PrivateNote.
    Útil para deshacer una reconciliación de prueba.
    """
    from dexter.core.batch import BatchEngine, BatchStorage, ReconciliationTaggerSkill
    from dexter.core.qbo_client import make_qbo_client

    storage = BatchStorage("data/dexter.db")
    engine = BatchEngine(storage)
    qbo = make_qbo_client(qbo_query, qbo_request)

    batch = storage.get_batch(batch_id)
    if not batch:
        return {"success": False, "error": f"Batch {batch_id} no existe"}

    period_start = batch.get("context", {}).get("period", "").split(" a ")[0]
    if not period_start:
        return {
            "success": False,
            "error": "No se puede reconstruir el período del batch.",
        }

    skill = ReconciliationTaggerSkill(
        engine=engine,
        qbo_client=qbo,
        period_start=period_start,
        period_end=period_start,
        account_id="",
    )
    result = skill.cleanup_tags(batch_id)
    return {
        "success": True,
        "removed": result.get("removed", 0),
        "errors": result.get("errors", []),
    }



def tool_procesar_reconciliacion_bancaria(archivo_csv: str) -> dict:
    """Tool: Procesa CSV de reconciliación bancaria"""
    return procesar_reconciliacion_bancaria(archivo_csv)



def tool_taggear_reconciliacion(
    archivo_csv: str,
    cuenta_id: str = None,
    fecha_inicio: str = None,
    fecha_fin: str = None,
    dias_fuzzy: int = 2,
    monto_fuzzy: float = 0.50,
) -> dict:
    """
    Tool: BNK-RECON tagger. Marca transactions existentes en QBO
    con el tag BNK-RECON-YYYY-MM-xxxxx en Memo/PrivateNote.
    NO crea transactions nuevas.

    Args:
        archivo_csv: Ruta al CSV del bank statement
            (columnas requeridas: date, description, amount).
        cuenta_id: ID de la cuenta bancaria en QBO. Si no se da,
            se busca automáticamente por categoría BANK.
        fecha_inicio: ISO date (YYYY-MM-DD). Default: mes actual.
        fecha_fin: ISO date (YYYY-MM-DD). Default: fin de mes.
        dias_fuzzy: Días de tolerancia para fuzzy match (default 2).
        monto_fuzzy: Diferencia máxima de monto en USD (default 0.50).
    """
    from datetime import datetime
    from dexter.core.batch import (
        BatchEngine, BatchStorage, ReconciliationTaggerSkill,
    )
    from dexter.core.qbo_client import make_qbo_client, find_bank_account_id

    if not cuenta_id:
        cuenta_id = find_bank_account_id(find_account)
        if not cuenta_id:
            return {
                "success": False,
                "error": "No se pudo identificar la cuenta bancaria. "
                         "Especifica cuenta_id o refresca el chart.",
            }

    if not fecha_inicio:
        hoy = datetime.now()
        fecha_inicio = f"{hoy.year:04d}-{hoy.month:02d}-01"
    if not fecha_fin:
        hoy = datetime.now()
        if hoy.month == 12:
            fin = f"{hoy.year + 1}-01-01"
        else:
            fin = f"{hoy.year:04d}-{hoy.month + 1:02d}-01"

    storage = BatchStorage("data/dexter.db")
    engine = BatchEngine(storage)
    qbo = make_qbo_client(qbo_query, qbo_request)

    skill = ReconciliationTaggerSkill(
        engine=engine,
        qbo_client=qbo,
        period_start=fecha_inicio,
        period_end=fecha_fin,
        account_id=cuenta_id,
        fuzzy_days=dias_fuzzy,
        fuzzy_amount=monto_fuzzy,
    )
    batch_id = skill.from_csv(archivo_csv)
    summary = skill.run(batch_id)
    return {
        "success": True,
        "batch_id": batch_id,
        "matched": summary["matched"],
        "exact": summary["exact"],
        "fuzzy": summary["fuzzy"],
        "unmatched": summary["unmatched"],
        "errors": summary["errors"],
        "report_path": summary["report_path"],
        "tag_prefix": summary["tag_prefix"],
    }



