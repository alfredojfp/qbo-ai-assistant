#!/usr/bin/env python3
"""
Disconnect Webhook — Detecta si un usuario revocó el acceso de Dexter a QBO.

Requisito del QBO App Marketplace. Intuit notifica vía webhook cuando
un usuario desconecta la app. Este script se ejecuta periódicamente
(vía cron) para verificar que el refresh_token siga siendo válido.

Si el token fue revocado, limpia los datos locales de la empresa.

Uso:
    python3 scripts/disconnect_webhook.py          # verifica todas las empresas
    python3 scripts/disconnect_webhook.py --cron   # para crontab
"""
import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime


COMPANIES_DIR = Path(__file__).resolve().parent.parent / "companies"
LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "disconnect.log"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"


def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")


def check_company(company_dir: Path) -> dict:
    """Verifica si el refresh token de una empresa es válido."""
    meta_file = company_dir / "meta.json"
    if not meta_file.exists():
        return {"name": company_dir.name, "status": "no_meta"}

    meta = json.loads(meta_file.read_text())
    refresh_token = meta.get("refresh_token")
    if not refresh_token:
        return {"name": company_dir.name, "status": "no_token"}

    # Intentar refrescar token
    try:
        resp = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            return {"name": company_dir.name, "status": "ok"}
        elif resp.status_code == 400 and "invalid_grant" in resp.text:
            return {"name": company_dir.name, "status": "revoked"}
        else:
            return {"name": company_dir.name, "status": f"error_{resp.status_code}"}
    except Exception as e:
        return {"name": company_dir.name, "status": f"error: {e}"}


def cleanup_company(company_dir: Path):
    """Limpia datos de una empresa desconectada (tokens expuestos)."""
    meta_file = company_dir / "meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())
        # Borrar tokens, mantener realm_id y nombre para referencia
        meta["access_token"] = ""
        meta["refresh_token"] = ""
        meta["disconnected_at"] = datetime.now().isoformat()
        meta_file.write_text(json.dumps(meta, indent=2))
    log(f"  🧹 Tokens limpiados para {company_dir.name}")


def main():
    parser = argparse.ArgumentParser(description="QBO Disconnect Webhook Checker")
    parser.add_argument("--cron", action="store_true", help="Modo silencioso para cron")
    args = parser.parse_args()

    if not COMPANIES_DIR.exists():
        if not args.cron:
            print("No hay empresas registradas.")
        return

    results = []
    for company_dir in sorted(COMPANIES_DIR.iterdir()):
        if not company_dir.is_dir():
            continue
        result = check_company(company_dir)
        results.append(result)

        if result["status"] == "revoked":
            log(f"🔴 REVOCADO: {result['name']}")
            cleanup_company(company_dir)
        elif result["status"] != "ok":
            log(f"⚠️  {result['name']}: {result['status']}")

    # Summary
    ok = sum(1 for r in results if r["status"] == "ok")
    revoked = sum(1 for r in results if r["status"] == "revoked")
    other = len(results) - ok - revoked

    if not args.cron:
        print(f"\n📊 Resumen: {ok} OK | {revoked} revocados | {other} otros")
    if revoked > 0:
        log(f"📊 {revoked} empresa(s) desconectada(s) — tokens limpiados")


if __name__ == "__main__":
    main()
