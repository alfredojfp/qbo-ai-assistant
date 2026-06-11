"""dexter.skills.reports.tools — 5 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

def tool_cargar_reporte(nombre: str) -> dict:
    """Tool: Carga reporte"""
    config = load_report_config(nombre)

    if config:
        return {"success": True, "config": config}
    else:
        return {"success": False, "error": f"Reporte '{nombre}' no encontrado"}


def tool_generar_balance_sheet(fecha: str, metodo: str = "Accrual") -> dict:
    """Tool: Genera Balance Sheet. LOW-7 fix: usa list[dict] sin pandas."""
    rows = generate_balance_sheet(fecha, metodo)

    if not rows:
        return {"success": False, "error": "No se pudo generar el reporte"}

    return {
        "success": True,
        "fecha": fecha,
        "registros": len(rows),
        "resumen": _aggregate_by_category(rows),
        "data_preview": rows[:10],
    }


def tool_generar_reporte_pl(fecha_inicio: str, fecha_fin: str, metodo: str = "Accrual") -> dict:
    """Tool: Genera P&L. LOW-7 fix: usa list[dict] sin pandas."""
    rows = generate_pl_report(fecha_inicio, fecha_fin, metodo)

    if not rows:
        return {"success": False, "error": "No se pudo generar el reporte"}

    return {
        "success": True,
        "periodo": f"{fecha_inicio} a {fecha_fin}",
        "registros": len(rows),
        "resumen": _aggregate_by_category(rows),
        "data_preview": rows[:10],
    }


def tool_guardar_reporte(nombre: str, config: dict) -> dict:
    """Tool: Guarda reporte"""
    save_report_config(nombre, config)
    return {"success": True, "mensaje": f"Reporte '{nombre}' guardado exitosamente"}


def tool_listar_reportes_guardados() -> dict:
    """Tool: Lista reportes guardados"""
    saved = session_state.get("saved_reports", {})

    return {
        "total": len(saved),
        "reportes": [{
            "nombre": name,
            "creado": data["created"],
            "ultimo_uso": data["last_used"]
        } for name, data in saved.items()]
    }


