#!/usr/bin/env python3
"""
TSheets Punch — Marcador de entrada/salida por empresa.

Uso:
    python3 scripts/tsheets_punch.py in "Sandbox Company_US_1"
    python3 scripts/tsheets_punch.py out
    python3 scripts/tsheets_punch.py status
    python3 scripts/tsheets_punch.py jobs

Credenciales en .env:
    TSHEETS_ACCESS_TOKEN=xxx
    TSHEETS_REFRESH_TOKEN=xxx    (opcional, para refresh automático)
"""
import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
BASE_URL = "https://rest.tsheets.com/api/v1"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

def load_env():
    """Carga credenciales desde .env."""
    if not ENV_FILE.exists():
        print("❌ .env no encontrado. Asegurate de tener TSHEETS_ACCESS_TOKEN en .env")
        sys.exit(1)
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if key in ("TSHEETS_ACCESS_TOKEN", "TSHEETS_REFRESH_TOKEN") and not os.getenv(key):
            os.environ[key] = val

def get_token():
    token = os.getenv("TSHEETS_ACCESS_TOKEN", "").strip()
    if not token:
        print("❌ TSHEETS_ACCESS_TOKEN no configurado en .env")
        sys.exit(1)
    return token

def api_get(endpoint, params=None):
    token = get_token()
    resp = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
        timeout=30,
    )
    if resp.status_code == 401:
        print("⚠️  Token expirado. Refrescando...")
        refresh()
        return api_get(endpoint, params)
    resp.raise_for_status()
    return resp.json()

def api_post(endpoint, data):
    token = get_token()
    resp = requests.post(
        f"{BASE_URL}/{endpoint}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=data,
        timeout=30,
    )
    if resp.status_code == 401:
        print("⚠️  Token expirado. Refrescando...")
        refresh()
        return api_post(endpoint, data)
    resp.raise_for_status()
    return resp.json()

def api_put(endpoint, data):
    token = get_token()
    resp = requests.put(
        f"{BASE_URL}/{endpoint}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=data,
        timeout=30,
    )
    if resp.status_code == 401:
        print("⚠️  Token expirado. Refrescando...")
        refresh()
        return api_put(endpoint, data)
    resp.raise_for_status()
    return resp.json()

def refresh():
    """Refresca el access token usando el refresh token."""
    rt = os.getenv("TSHEETS_REFRESH_TOKEN", "").strip()
    if not rt:
        print("❌ No hay TSHEETS_REFRESH_TOKEN. Obtén un token nuevo en:")
        print("   https://tsheets.intuit.com → Feature Add-ons → API → Add Application")
        sys.exit(1)
    resp = requests.post(
        f"{BASE_URL}/grant",
        data={
            "grant_type": "refresh_token",
            "refresh_token": rt,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"❌ No se pudo refrescar: {resp.text}")
        sys.exit(1)
    data = resp.json()
    token = data.get("access_token", "")
    new_rt = data.get("refresh_token", rt)
    os.environ["TSHEETS_ACCESS_TOKEN"] = token
    # Actualizar .env
    lines = ENV_FILE.read_text().splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("TSHEETS_ACCESS_TOKEN="):
            new_lines.append(f"TSHEETS_ACCESS_TOKEN='{token}'")
        elif line.startswith("TSHEETS_REFRESH_TOKEN="):
            new_lines.append(f"TSHEETS_REFRESH_TOKEN='{new_rt}'")
        else:
            new_lines.append(line)
    ENV_FILE.write_text("\n".join(new_lines) + "\n")
    print("✅ Token refrescado.")

# ── Comandos ────────────────────────────────────────────────────────

def cmd_jobs():
    """Lista los jobcodes (empresas/proyectos) disponibles."""
    data = api_get("jobcodes")
    jobcodes = data.get("results", {}).get("jobcodes", {})
    if not jobcodes:
        print("No hay jobcodes configurados.")
        return
    print("\n📋 Empresas / Proyectos disponibles:\n")
    for jid, jc in sorted(jobcodes.items()):
        name = jc.get("name", "Sin nombre")
        parent = jc.get("parent_id", 0)
        active = jc.get("active", True)
        status = "✅" if active else "❌"
        parent_tag = "  └ Sub-proyecto" if parent else ""
        print(f"  {status} ID: {jid:<10} {name}{parent_tag}")

def cmd_status():
    """Muestra si hay un timesheet abierto ahora."""
    data = api_get("timesheets", params={"on_the_clock": "yes", "limit": 5})
    results = data.get("results", {}).get("timesheets", [])
    if not results:
        print("⏸️  No hay ningún timesheet abierto.")
        return
    print("\n⏱️  Timesheets abiertos:\n")
    for ts_id, ts in results.items() if isinstance(results, dict) else enumerate(results):
        if isinstance(results, dict):
            ts = results[ts_id]
        start = ts.get("start", "?")
        jobcode_id = ts.get("jobcode_id", "?")
        # Obtener nombre del jobcode
        try:
            jc_data = api_get("jobcodes", params={"ids": str(jobcode_id)})
            jc_name = list(jc_data.get("results", {}).get("jobcodes", {}).values())[0].get("name", "?")
        except Exception:
            jc_name = str(jobcode_id)
        print(f"  🟢 {jc_name}")
        print(f"     Inicio: {start}")
        print(f"     ID: {ts_id if isinstance(results, dict) else ts.get('id', '?')}")

def cmd_in(job_name: str):
    """Marca entrada para una empresa/proyecto."""
    # Buscar el jobcode por nombre
    data = api_get("jobcodes")
    jobcodes = data.get("results", {}).get("jobcodes", {})
    
    match = None
    for jid, jc in jobcodes.items():
        if jc.get("name", "").lower() == job_name.lower():
            match = (jid, jc)
            break
    
    if not match:
        # Fuzzy match
        for jid, jc in jobcodes.items():
            if job_name.lower() in jc.get("name", "").lower():
                match = (jid, jc)
                break
    
    if not match:
        print(f"❌ No encontré '{job_name}'. Usá 'jobs' para ver la lista.")
        sys.exit(1)
    
    jid, jc = match
    
    # Verificar si ya hay un timesheet abierto para este jobcode
    open_data = api_get("timesheets", params={"on_the_clock": "yes", "jobcode_ids": str(jid)})
    open_ts = open_data.get("results", {}).get("timesheets", {})
    if open_ts:
        ts = list(open_ts.values())[0]
        print(f"⚠️  Ya hay un timesheet abierto para '{jc['name']}' desde {ts.get('start', '?')}")
        print("   Usá 'out' para cerrarlo primero.")
        sys.exit(1)
    
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    result = api_post("timesheets", {
        "data": [{
            "jobcode_id": int(jid),
            "start": now,
            "type": "regular",
        }]
    })
    print(f"✅ Entrada marcada en '{jc['name']}' — {now}")

def cmd_out():
    """Marca salida del timesheet abierto actual."""
    data = api_get("timesheets", params={"on_the_clock": "yes", "limit": 10})
    # TSheets API returns results as dict {timesheet_id: {...}}
    results = data.get("results", {})
    if isinstance(results, dict):
        timesheets = list(results.get("timesheets", {}).values())
    else:
        timesheets = results
    
    if not timesheets:
        print("⏸️  No hay ningún timesheet abierto.")
        return
    
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    if len(timesheets) == 1:
        ts = timesheets[0]
        ts_id = ts.get("id")
    else:
        print("📋 Timesheets abiertos:")
        for i, ts in enumerate(timesheets, 1):
            jid = ts.get("jobcode_id", "?")
            try:
                jc_data = api_get("jobcodes", params={"ids": str(jid)})
                jc_name = list(jc_data.get("results", {}).get("jobcodes", {}).values())[0].get("name", "?")
            except Exception:
                jc_name = str(jid)
            print(f"  {i}. {jc_name} (desde {ts.get('start', '?')})")
        choice = input("\n¿Cuál cerrar? (número o Enter para todos): ").strip()
        if choice:
            try:
                idx = int(choice) - 1
                timesheets = [timesheets[idx]]
            except (ValueError, IndexError):
                print("❌ Opción inválida.")
                return
    
    for ts in timesheets:
        ts_id = ts.get("id")
        api_put("timesheets", {
            "data": [{"id": ts_id, "end": now}]
        })
        jid = ts.get("jobcode_id", "?")
        try:
            jc_data = api_get("jobcodes", params={"ids": str(jid)})
            jc_name = list(jc_data.get("results", {}).get("jobcodes", {}).values())[0].get("name", "?")
        except Exception:
            jc_name = str(jid)
        print(f"✅ Salida marcada en '{jc_name}' — {now}")

# ── Main ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    load_env()
    
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd in ("in", "entrada"):
        name = sys.argv[2] if len(sys.argv) > 2 else None
        if not name:
            print("❌ Especificá el nombre de la empresa. Ej: tsheets_punch.py in 'Sandbox'")
            sys.exit(1)
        cmd_in(name)
    elif cmd in ("out", "salida"):
        cmd_out()
    elif cmd in ("status", "estado"):
        cmd_status()
    elif cmd in ("jobs", "empresas", "proyectos"):
        cmd_jobs()
    else:
        print(f"❌ Comando desconocido: {cmd}")
        print(__doc__)
        sys.exit(1)
