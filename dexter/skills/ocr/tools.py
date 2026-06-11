"""dexter.skills.ocr.tools — 3 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

from main import buscar_cliente, buscar_vendor, buscar_cuenta, buscar_item
import os

def tool_procesar_csv_corregido(csv_path: str, crear_bills: bool = False) -> dict:
    """Tool: Procesa un CSV de bills corregido manualmente por Alfredo.

    Lee el CSV editado, detecta correcciones vs la extracción original,
    registra los tips de aprendizaje, y opcionalmente crea los bills.

    Usar después de que Alfredo editó el CSV preview generado por OCR.
    """
    from ocr_bills import procesar_csv_corregido
    result = procesar_csv_corregido(csv_path)

    if not result.get("success"):
        return result

    # Registrar tips de aprendizaje
    for tip_info in result.get("tips_learned", []):
        tool_registrar_provider_tip(tip_info["provider"], tip_info["tip"])

    # Si se pide crear bills, hacerlo
    created = []
    if crear_bills and result.get("bills"):
        for bill in result["bills"]:
            vendor_name = bill.get("vendor_name", "")
            amount = bill.get("total_amount", 0)
            account = bill.get("account_name", "")
            customer = bill.get("customer_name", "")
            invoice_num = bill.get("invoice_number", "")
            invoice_date = bill.get("invoice_date", "")

            if not vendor_name or amount <= 0:
                continue

            try:
                # Buscar o crear vendor
                vendors = buscar_vendor(vendor_name)
                vendor_id = vendors[0]["id"] if vendors else None

                created.append({
                    "vendor": vendor_name,
                    "amount": amount,
                    "account": account,
                    "customer": customer,
                    "invoice": invoice_num,
                    "vendor_id": vendor_id,
                    "status": "pendiente_crear",
                })
            except Exception as e:
                created.append({
                    "vendor": vendor_name,
                    "amount": amount,
                    "error": str(e),
                    "status": "error",
                })

    return {
        "success": True,
        "bills_procesados": len(result.get("bills", [])),
        "tips_aprendidos": len(result.get("tips_learned", [])),
        "tips": result.get("tips_learned", []),
        "creados": created if crear_bills else [],
        "mensaje": "CSV procesado. Revisá los tips aprendidos." if not crear_bills
                   else f"CSV procesado con {len(created)} bills.",
    }



def tool_procesar_estado_cuenta(pdf_path: str, bank_name: str = None) -> dict:
    """Tool: Convierte PDF de estado de cuenta bancario a CSV via OCR.

    Compatible con cualquier banco (Santander, BBVA, Chase, etc.).
    Genera CSV en data/ para usar con el motor de reconciliación.
    """
    try:
        from scripts.bank_statement_ocr import process_bank_statement
    except ImportError:
        return {"success": False, "error": "Módulo bank_statement_ocr no disponible"}
    tips = _get_provider_tips(bank_name) if bank_name else None
    return process_bank_statement(pdf_path, bank_name=bank_name, provider_tips=tips)


# Resolver el path del log una vez para tool_ver_log_errores
from dexter.error_log import LOG_FILE as _LOG_FILE_FOR_TOOLS


def tool_procesar_lote_bills(nombre_archivo: str = None) -> dict:
    """Tool: Procesa lote de bills desde PDF en carpeta 'Pending bills'."""
    return procesar_lote_bills(nombre_archivo)



