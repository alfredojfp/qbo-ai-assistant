#!/usr/bin/env python3
"""
TSheets Quick Launcher — Abre la página de TSheets en el navegador.

Uso:
    python3 scripts/tsheets_launch.py
    python3 scripts/tsheets_launch.py 9130353977251266
"""
import sys
import webbrowser

# Realm ID por defecto (el que mencionaste)
DEFAULT_REALM = "9130353977251266"

realm = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REALM
url = f"https://tsheets.intuit.com/?realm_id={realm}&s=26"

print(f"Abriendo TSheets: {url}")
webbrowser.open(url)
