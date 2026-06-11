"""dexter.skills.bank_feed.tools — 1 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

def tool_procesar_bank_feed_csv(archivo_csv: str) -> dict:
    """Tool: Procesa CSV de Bank Feed con splits.

    MED-8 fix: usa verbose=False y captura log en list para que el
    LLM reciba el progreso en el dict (no en stdout mezclado).
    """
    log_lines: list = []
    result = procesar_csv_bank_feed(archivo_csv, verbose=False, log=log_lines)
    result.setdefault("log_lines", log_lines)
    return result


