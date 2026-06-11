"""dexter.skills.admin.tools — 7 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

from main import load_chart_of_accounts
from pathlib import Path
import json

def tool_gestionar_empresas(accion: str, nombre: str = None, link_o_id: str = None) -> dict:
    """
    Tool: Gestiona el registro y cambio de empresas.

    MED-12 fix: usa _company_lock (threading.RLock) para serializar
    mutaciones de estado global. Evita race condition si un tool
    largo (procesar_csv_banco, batch) está mid-flight cuando el
    usuario pide cambiar empresa.
    """
    global CURRENT_COMPANY, QB_REALM_ID, QB_BASE_URL, COMPANY_CONTEXT, QB_ACCESS_TOKEN, QB_REFRESH_TOKEN

    if accion == "cambiar":
        if not _company_lock.acquire(blocking=False):
            return {
                "success": False,
                "error": (
                    "No se puede cambiar de empresa mientras un tool está "
                    "en ejecución; espera a que termine o cancela con Ctrl+C."
                ),
                "lock_busy": True,
            }
        try:
            return _cambiar_empresa_bloqueado(nombre)
        finally:
            _company_lock.release()

    if accion == "registrar":
        if not nombre or not link_o_id:
            return {"success": False, "message": "Faltan datos (nombre o link_o_id)"}
        
        realm_id = extract_realm_id(link_o_id)
        if not realm_id:
            return {"success": False, "message": "No se pudo extraer un Realm ID válido del link proporcionado."}
        
        save_company_meta(nombre, realm_id)
        return {"success": True, "message": f"Empresa '{nombre}' (ID: {realm_id}) registrada exitosamente. Ya puedes cambiar a ella usando 'cambiar'."}
        
    elif accion == "listar":
        companies = list_local_companies()
        res = "Empresas registradas:\n"
        for c in companies:
            status = "✅" if c["has_tokens"] else "🔑"
            res += f"- {status} {c['name']} (ID: {c['realm_id']})\n"
        return {"success": True, "message": res, "empresas": companies}

    return {"success": False, "message": "Acción no reconocida."}



def tool_gestionar_memoria(target: str = "memory", action: str = "add",
                           content: str = "", old_text: str = "") -> dict:
    """Tool: gestiona la memoria persistente del agente (MEMORY.md / USER.md).

    Args:
        target: 'memory' (notas del agente) o 'user' (perfil de Alfredo)
        action: 'add' (agregar), 'remove' (eliminar por substring), 'status' (ver uso)
        content: texto a agregar (para action='add')
        old_text: substring de la entrada a eliminar (para action='remove')

    Usos típicos:
      - Después de aprender algo nuevo sobre Alfredo
      - Después de descubrir un dato del entorno (ej. realm ID)
      - Cuando Alfredo corrige algo que dijiste
    """
    mem = _get_memory()
    if action == "status":
        return mem.get_status()
    elif action == "add":
        if not content.strip():

def tool_leer_archivo(ruta: str) -> dict:
    """Tool: Lee un archivo de texto del proyecto (markdown, csv, json).

    Útil para consultar PROFILE.md, MEMORY.md, templates, o documentación.
    Solo permite archivos dentro del directorio del proyecto (seguridad).
    """
    from pathlib import Path
    base = Path(__file__).resolve().parent
    target = (base / ruta).resolve()

    # Seguridad: no permitir salir del proyecto
    if not str(target).startswith(str(base)):
        return {"success": False, "error": "Acceso denegado: ruta fuera del proyecto"}

    if not target.exists():
        return {"success": False, "error": f"Archivo no encontrado: {ruta}"}

    try:
        content = target.read_text(encoding="utf-8")
        # Limitar a 5000 chars para no saturar el contexto
        if len(content) > 5000:
            content = content[:5000] + f"\n\n... (truncado, {len(content)} chars totales)"
        return {"success": True, "path": ruta, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}



def tool_limpiar_log_errores() -> dict:
    """Tool: Borra el archivo de log de errores."""
    from dexter.error_log import clear_log
    clear_log()
    return {"success": True, "message": "Log de errores borrado."}



def tool_refrescar_chart_accounts() -> dict:
    """Tool: Refresca Chart of Accounts"""
    chart = load_chart_of_accounts(force_refresh=True)
    session_state["chart_of_accounts"] = chart

    return {
        "success": True,
        "cuentas_cargadas": len(chart),
        "mensaje": "Chart of Accounts actualizado exitosamente"
    }


def tool_registrar_provider_tip(provider: str, tip: str) -> dict:
    """Tool: Registra un tip de extracción para facturas de un proveedor.

    Usar cuando Alfredo corrige la extracción OCR de una factura.
    El tip se guarda en la memoria de la empresa y se usa en futuros
    procesamientos OCR para el mismo proveedor.

    Ejemplos:
      provider="CFE", tip="Total en negrita abajo derecha"
      provider="Amazon", tip="Usar columna USD, ignorar MXN"
      provider="Ferretería Local", tip="Factura manuscrita, leer observaciones"
    """
    provider = provider.strip()
    tip = tip.strip()
    if not provider or not tip:
        return {"success": False, "error": "provider y tip son requeridos"}

    entry = f"{provider}: {tip}"
    mem = _get_memory()
    return mem.add("memory", entry)



def tool_ver_log_errores(n: int = 20, categoria: str = None) -> dict:
    """Tool: Muestra las últimas N entradas del log de errores persistido.

    Args:
        n:        Número de entradas recientes a retornar (default 20).
        categoria: Filtrar por categoría (api_call, tool_dispatch, user_input,
                   auth, unknown). Si es None, retorna todas.
    """
    from dexter.error_log import get_recent_errors
    entries = get_recent_errors(n=max(1, min(n, 200)))
    if categoria:
        entries = [e for e in entries if e.get("category") == categoria]
    return {
        "total": len(entries),
        "log_file": str(_LOG_FILE_FOR_TOOLS),
        "entries": entries,
    }


