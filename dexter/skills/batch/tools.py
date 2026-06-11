"""dexter.skills.batch.tools — 3 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

from main import qbo_request
import os

def tool_crear_template_csv() -> dict:
    """Tool: Crea template CSV"""
    create_deposits_template()
    return {"success": True, "archivo": FILE_DEPOSITS_TEMPLATE}


def tool_depositar_lote_csv(
    ruta_archivo: str,
    cuenta_banco_id: str = None,
    cuenta_ingreso_id: str = None,
    confirmar: bool = True,
) -> dict:
    """
    Tool: Procesa CSV de deposits multi-cliente con el motor batch.
    Usa el Sprint 2 (DepositBatchSkill) con state machine,
    disambiguación interactiva y dry-run obligatorio.

    Args:
        ruta_archivo: Ruta al CSV (columnas: date, client_name, amount).
            Opcionales: terms, memo.
        cuenta_banco_id: ID de la cuenta bancaria. Si no se da, se auto-detecta.
        cuenta_ingreso_id: ID de la cuenta de income default. Si no se da,
            se auto-detecta buscando cuentas tipo INGRESO.
        confirmar: Si True, pide confirmación antes de ejecutar.
            Si False, solo corre el dry-run (no crea nada en QBO).
    """
    from dexter.core.batch import (
        BatchEngine, BatchStorage, Disambiguator, DepositBatchSkill,
    )
    from dexter.core.qbo_client import make_deposit_qbo_client

    if not os.path.exists(ruta_archivo):
        return {"success": False, "error": f"Archivo no encontrado: {ruta_archivo}"}

    if not cuenta_banco_id:
        cuenta_banco_id = find_bank_account_id(find_account)
        if not cuenta_banco_id:
            return {
                "success": False,
                "error": "No se pudo identificar la cuenta bancaria. "
                         "Especifica cuenta_banco_id o refresca el chart.",
            }

    if not cuenta_ingreso_id:
        results = find_account("sales", exact=False, category="INGRESO")
        if not results:
            results = find_account("income", exact=False, category="INGRESO")
        if not results:
            return {
                "success": False,
                "error": "No se pudo identificar la cuenta de income. "
                         "Especifica cuenta_ingreso_id.",
            }
        cuenta_ingreso_id = results[0]["id"]

    storage = BatchStorage("data/dexter.db")
    engine = BatchEngine(storage)
    disambiguator = Disambiguator(input_func=input, output_func=print)
    qbo = make_deposit_qbo_client(search_customer, qbo_request)

    skill = DepositBatchSkill(
        engine=engine,
        disambiguator=disambiguator,
        qbo_client=qbo,
        bank_account_id=cuenta_banco_id,
        income_account_id=cuenta_ingreso_id,
    )
    batch_id = skill.from_csv(ruta_archivo)

    # Dry-run: validar sin crear
    print(f"\n📋 BATCH {batch_id} CREADO")
    print(f"   Items: {len(storage.get_items(batch_id))}")
    print(f"   Cuenta banco: {cuenta_banco_id}")
    print(f"   Cuenta income: {cuenta_ingreso_id}")

    if not confirmar:
        return {
            "success": True,
            "batch_id": batch_id,
            "dry_run": True,
            "message": "Batch creado. Revisa con 'listar batches' antes de confirmar.",
        }

    # Confirmar y ejecutar
    if not disambiguator.confirm_batch(batch_id):
        return {
            "success": False,
            "batch_id": batch_id,
            "message": "Operación cancelada por el usuario.",
        }

    summary = skill.execute(batch_id)
    return {
        "success": summary.get("executed", 0) > 0,
        "batch_id": batch_id,
        "executed": summary.get("executed", 0),
        "failed": summary.get("failed", 0),
        "errors": summary.get("errors", []),
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

# Mapeo de nombres de tools a funciones



def tool_procesar_csv_depositos(ruta_archivo: str) -> dict:
    """Tool: Procesa CSV de depósitos.

    R-4 fix: llama tool_depositar_lote_csv DIRECTAMENTE y retorna su
    shape rico {success, batch_id, executed, failed, errors} — más útil
    para el LLM (puede citar batch_id al usuario, resumir executed/failed).
    process_deposits_csv queda como shim de backward compat (HIGH-4 test).
    """
    return tool_depositar_lote_csv(
        ruta_archivo=ruta_archivo,
        confirmar=True,
    )


