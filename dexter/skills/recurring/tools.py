"""dexter.skills.recurring.tools — 2 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

from pathlib import Path

def tool_adjuntar_archivo(ruta_archivo: str, tipo_entidad: str, id_entidad: str,
                          nota: str = None) -> dict:
    """Tool: Adjunta un archivo (PDF, imagen) a una transacción (Bill, Invoice, etc.).

    ruta_archivo: path absoluto al archivo en disco
    """
    import mimetypes
    from pathlib import Path
    p = Path(ruta_archivo)
    if not p.exists():
        return {"success": False, "error": f"Archivo no encontrado: {ruta_archivo}"}
    mime, _ = mimetypes.guess_type(str(p))
    if not mime:
        return {"success": False, "error": f"No se pudo determinar MIME type de {p.suffix}"}
    content = p.read_bytes()
    return upload_attachment(content, p.name, mime, tipo_entidad, id_entidad, nota)



def tool_crear_recurringtransaction(transaccion_base: dict, nombre: str,
                                     tipo_recur: str = "Automated",
                                     intervalo: str = "Monthly", num_intervalo: int = 1,
                                     fecha_inicio: str = None, max_ocurrencias: int = None,
                                     dia_del_mes: int = None, dias_antes: int = 2,
                                     activa: bool = True) -> dict:
    """Tool: Crea una transacción recurrente (plantilla automática)."""
    return create_recurring_transaction(transaccion_base, nombre, tipo_recur,
                                        intervalo, num_intervalo, fecha_inicio,
                                        max_ocurrencias, dia_del_mes, dias_antes, activa)



