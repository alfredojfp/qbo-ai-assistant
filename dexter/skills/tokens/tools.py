"""dexter.skills.tokens.tools — 2 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

from datetime import datetime
import os

def tool_generar_informe_tokens() -> dict:
    """Tool: Genera informe de tokens (Excel + summary estructurado)."""
    generate_token_report()
    # Calcula summary para que el LLM pueda mostrar totales sin re-leer
    summary: Dict[str, Any] = {
        "success": True,
        "archivo": FILE_TOKEN_REPORT,
    }
    if os.path.exists(FILE_TOKEN_USAGE):
        try:
            import pandas as pd
            df = pd.read_csv(FILE_TOKEN_USAGE)
            if not df.empty:
                summary["total_sesiones"] = int(len(df))
                summary["total_input_tokens"] = int(df["input_tokens"].sum())
                summary["total_output_tokens"] = int(df["output_tokens"].sum())
                summary["total_tokens"] = int(df["total_tokens"].sum())
                summary["costo_total_usd"] = round(float(df["costo_usd"].sum()), 4)
                summary["operaciones_totales"] = int(df["operaciones"].sum())
                summary["duracion_total_min"] = round(
                    float(df["duracion_min"].sum()), 1
                )
                summary["costo_promedio_sesion"] = round(
                    float(df["costo_usd"].mean()), 4
                )
        except Exception as e:
            summary["warning"] = f"No se pudo calcular summary: {e}"
    return summary


def tool_obtener_estadisticas_tokens(periodo: str) -> dict:
    """Tool: Estadísticas de tokens.

    Args:
        periodo: "sesion" (sesión actual), "dia" (hoy desde CSV histórico),
                 "mes" (mes actual desde CSV histórico),
                 "YYYY-MM-DD" o "YYYY-MM" específicos.
    """
    if periodo == "sesion":
        return {
            "periodo": "Sesión actual",
            "input_tokens": session_state["input_tokens"],
            "output_tokens": session_state["output_tokens"],
            "total_tokens": session_state["input_tokens"] + session_state["output_tokens"],
            "costo_usd": round(calculate_session_cost(), 4),
            "duracion_min": round((datetime.now() - session_state["start_time"]).total_seconds() / 60, 1)
        }

    if not os.path.exists(FILE_TOKEN_USAGE):
        return {
            "error": f"No hay datos históricos en {FILE_TOKEN_USAGE}",
            "sugerencia": "Usa periodo='sesion' para ver consumo de la sesión actual.",
        }

    try:
        import pandas as pd
        df = pd.read_csv(FILE_TOKEN_USAGE)
    except Exception as e:
        return {"error": f"Error leyendo {FILE_TOKEN_USAGE}: {e}"}

    if df.empty or "fecha" not in df.columns:
        return {
            "error": f"{FILE_TOKEN_USAGE} está vacío o no tiene columna 'fecha'",
        }

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"])
    if df.empty:
        return {"error": "No hay fechas válidas en el CSV."}

    hoy = datetime.now().date()
    if periodo == "dia":
        mask = df["fecha"].dt.date == hoy
        label = f"Día {hoy.isoformat()}"
    elif periodo == "mes":
        mask = (df["fecha"].dt.year == hoy.year) & (df["fecha"].dt.month == hoy.month)
        label = f"Mes {hoy.year:04d}-{hoy.month:02d}"
    elif len(periodo) == 10 and periodo[4] == "-" and periodo[7] == "-":
        # YYYY-MM-DD específico
        try:
            target = datetime.strptime(periodo, "%Y-%m-%d").date()
            mask = df["fecha"].dt.date == target
            label = f"Día {periodo}"
        except ValueError:
            return {"error": f"Fecha inválida: {periodo}"}
    elif len(periodo) == 7 and periodo[4] == "-":
        # YYYY-MM específico
        try:
            y, m = periodo.split("-")
            mask = (df["fecha"].dt.year == int(y)) & (df["fecha"].dt.month == int(m))
            label = f"Mes {periodo}"
        except (ValueError, IndexError):
            return {"error": f"Mes inválido: {periodo}"}
    else:
        return {
            "error": f"Periodo '{periodo}' no reconocido. "
                     f"Usa 'sesion', 'dia', 'mes', 'YYYY-MM-DD' o 'YYYY-MM'."
        }

    sub = df.loc[mask]
    if sub.empty:
        return {
            "periodo": label,
            "sesiones": 0,
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "costo_usd": 0.0,
            "operaciones": 0,
            "mensaje": f"Sin datos para {label}",
        }

    return {
        "periodo": label,
        "sesiones": int(len(sub)),
        "input_tokens": int(sub["input_tokens"].sum()),
        "output_tokens": int(sub["output_tokens"].sum()),
        "total_tokens": int(sub["total_tokens"].sum()),
        "costo_usd": round(float(sub["costo_usd"].sum()), 4),
        "operaciones": int(sub["operaciones"].sum()),
        "duracion_min": round(float(sub["duracion_min"].sum()), 1),
    }


