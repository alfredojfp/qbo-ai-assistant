#!/usr/bin/env python3
"""
Setup Wizard — Configuración interactiva de Dexter para primera vez.

Se ejecuta automáticamente cuando no existe .env o faltan credenciales.
Guía al usuario paso a paso para configurar:
  1. QuickBooks OAuth (Client ID, Client Secret)
  2. OpenRouter API Key (LLM)
  3. Google Gemini API Key (OCR, opcional)
  4. Registrar primera empresa
"""
import os
import sys
import re
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    def input_wrapper(prompt):
        return input(prompt)


def banner():
    if HAS_RICH:
        console.print(Panel.fit(
            "[bold cyan]🧠  DEXTER — Setup Wizard[/bold cyan]\n"
            "[dim]Configuración inicial del asistente contable con IA[/dim]",
            border_style="cyan"
        ))
    else:
        print("=" * 60)
        print("  DEXTER — Setup Wizard")
        print("  Configuración inicial")
        print("=" * 60)
    print()


def section(title):
    if HAS_RICH:
        console.print(f"\n[bold yellow]▸ {title}[/bold yellow]")
    else:
        print(f"\n► {title}")


def prompt(text, default=None, password=False):
    if HAS_RICH:
        if password:
            return Prompt.ask(f"  {text}", password=True)
        return Prompt.ask(f"  {text}", default=default or "")
    else:
        if password:
            import getpass
            return getpass.getpass(f"  {text}: ")
        val = input(f"  {text}: ").strip()
        return val or default or ""


def validate_not_empty(value, field_name):
    if not value or not value.strip():
        print(f"  ❌ {field_name} es obligatorio")
        return None
    return value.strip()


def validate_url(value):
    if not value:
        return value
    # Extract realm_id from QuickBooks URL
    match = re.search(r'companyId=(\d{10,20})', value)
    if match:
        return match.group(1)
    # If it's just a number, use it
    if value.isdigit() and 10 <= len(value) <= 20:
        return value
    return value if value.startswith("http") else None


def run_setup():
    banner()

    # ── Paso 1: QuickBooks ──
    section("1/4 — QuickBooks Online API")

    print("  Necesitás credenciales de Intuit Developer.")
    print("  Si no las tenés: https://developer.intuit.com → My Apps → Create App")
    print()

    client_id = None
    while not client_id:
        val = prompt("QB_CLIENT_ID")
        client_id = validate_not_empty(val, "Client ID")

    client_secret = None
    while not client_secret:
        val = prompt("QB_CLIENT_SECRET", password=True)
        client_secret = validate_not_empty(val, "Client Secret")

    # ── Paso 2: LLM Provider ──
    section("2/4 — Proveedor LLM (Motor de IA)")

    print("  Elegí qué proveedor de IA usará Dexter para 'pensar':")
    print()
    print("  1. OpenRouter (recomendado) — acceso a 200+ modelos")
    print("  2. OpenAI (ChatGPT) — gpt-4o, gpt-4o-mini")
    print("  3. DeepSeek — deepseek-chat (V3)")
    print("  4. Google Gemini — gemini-2.5-flash")
    print("  5. Groq — llama-3.3-70b (rápido, barato)")
    print("  6. Custom — tu propio endpoint compatible con OpenAI API")
    print()

    providers = {
        "1": ("openrouter", "OpenRouter API Key (sk-or-v1-...)", "https://openrouter.ai → Settings → API Keys"),
        "2": ("openai", "OpenAI API Key (sk-...)", "https://platform.openai.com/api-keys"),
        "3": ("deepseek", "DeepSeek API Key (sk-...)", "https://platform.deepseek.com/api_keys"),
        "4": ("gemini", "Google API Key (AIza...)", "https://aistudio.google.com/apikey"),
        "5": ("groq", "Groq API Key (gsk_...)", "https://console.groq.com/keys"),
        "6": ("custom", "API Key", "Tu propio endpoint"),
    }

    choice = prompt("Elegí (1-6) [1]", default="1")
    provider_name, key_label, key_url = providers.get(choice, providers["1"])

    print(f"\n  Proveedor: {provider_name}")
    print(f"  Obtené tu API key en: {key_url}")
    print()

    llm_key = None
    while not llm_key:
        val = prompt(key_label)
        if val and len(val) > 10:
            llm_key = val.strip()
        else:
            print("  ❌ API Key inválida o muy corta")

    # ── Paso 3: Gemini (OCR) ──
    section("3/4 — Google Gemini API (OCR de facturas, opcional)")

    print("  Necesaria para procesar PDFs de facturas y estados de cuenta.")
    print("  Si no la tenés: https://aistudio.google.com/apikey")
    print("  Podés saltear este paso y configurarlo después.")
    print()

    gemini_key = prompt("GOOGLE_GEMINI_API_KEY (Enter para saltar)")
    gemini_key = gemini_key.strip() if gemini_key else ""

    # ── Paso 4: Empresa ──
    section("4/4 — Registrar tu primera empresa")

    print("  Pegá el link de QuickBooks o el Realm ID de tu empresa.")
    print("  Lo encontrás en: QBO → Configuración → Cuenta y configuración → Empresa")
    print()

    company_name = None
    while not company_name:
        val = prompt("Nombre de la empresa (ej: Mi Empresa)")
        company_name = validate_not_empty(val, "Nombre de empresa")

    realm_id = None
    while not realm_id:
        val = prompt("Link de QBO o Realm ID")
        realm_id = validate_url(val)
        if not realm_id:
            print("  ❌ Ingresá un link de QBO o un Realm ID válido (10-20 dígitos)")

    # ── Guardar .env ──
    print()
    if HAS_RICH:
        console.print("[bold green]✓[/bold green] Guardando configuración...")
    else:
        print("✓ Guardando configuración...")

    env_file = Path(__file__).resolve().parent / ".env"
    env_content = f"""# ── QuickBooks Online ──
QB_CLIENT_ID={client_id}
QB_CLIENT_SECRET={client_secret}
QB_REDIRECT_URI=http://localhost:8000/callback
QB_ENV=development
QB_MINOR_VERSION=70

# ── LLM (IA) ──
LLM_PROVIDER={provider_name}
LLM_API_KEY={llm_key}

# ── Google Gemini (OCR) ──
GOOGLE_GEMINI_API_KEY={gemini_key}

# ── Configuración avanzada ──
QB_REQUEST_TIMEOUT=30
MAX_REPORT_BYTES=250000
"""
    env_file.write_text(env_content)

    print("  ✅ .env creado")

    # ── Registrar empresa ──
    if HAS_RICH:
        console.print("\n[bold green]✓[/bold green] Ejecutando OAuth...")
    else:
        print("\n✓ Ejecutando OAuth...")

    # Intentar OAuth flow
    from dotenv import load_dotenv
    load_dotenv(override=True)

    try:
        from main import tool_gestionar_empresas
        result = tool_gestionar_empresas(
            accion="registrar",
            nombre=company_name,
            link_o_id=realm_id,
        )
        if result.get("success"):
            print(f"  ✅ Empresa '{company_name}' registrada")
        else:
            print(f"  ⚠️ {result.get('message', 'Error al registrar')}")
            print("  Podés registrarla después desde Dexter con: /gestionar_empresas")
    except Exception as e:
        print(f"  ⚠️ No se pudo registrar automáticamente: {e}")
        print("  Podés registrarla después desde Dexter.")

    # ── Final ──
    if HAS_RICH:
        console.print(Panel.fit(
            "[bold green]✅ ¡Configuración completa![/bold green]\n\n"
            "Ejecutá [bold]./run_dexter.sh[/bold] para iniciar Dexter.\n"
            "La primera carga estudiará tu empresa automáticamente.\n\n"
            "[dim]Si necesitás reconfigurar: borrá .env y volvé a ejecutar.[/dim]",
            border_style="green"
        ))
    else:
        print("\n" + "=" * 60)
        print("  ✅ ¡Configuración completa!")
        print("  Ejecutá ./run_dexter.sh para iniciar Dexter.")
        print("=" * 60)


if __name__ == "__main__":
    run_setup()
