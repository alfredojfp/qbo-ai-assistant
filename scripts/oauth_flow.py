"""
QuickBooks Online — OAuth flow inicial.

Uso:
    python3 scripts/oauth_flow.py [--environment sandbox|production] [--company NOMBRE]

Qué hace:
1. Lee Client ID, Client Secret y Redirect URI del .env
2. Genera un state aleatorio para CSRF protection
3. Arranca un servidor HTTP local en el puerto del redirect URI (default 8000)
4. Imprime la URL de autorización para que abras en el navegador
5. Espera el callback de Intuit, extrae `code` y `realmId`
6. Intercambia el code por access_token + refresh_token
7. Actualiza .env con QB_ACCESS_TOKEN, QB_REFRESH_TOKEN, QB_REALM_ID
8. Imprime resumen y termina

Por seguridad, los tokens NUNCA se imprimen a stdout — solo al .env.
"""

import argparse
import base64
import http.server
import json
import os
import secrets
import socketserver
import sys
import urllib.parse
import webbrowser
from pathlib import Path

from dotenv import dotenv_values, set_key


# Defaults leídos de .env más adelante
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
REDIRECT_HOST = "localhost"
AUTH_BASE = "https://appcenter.intuit.com/connect/oauth2"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
SCOPE = "com.intuit.quickbooks.accounting"


def _ensure_tunnel(port: int):
    """Verifica que el túnel HTTPS esté corriendo. Intenta detectar cloudflared."""
    import subprocess, shutil, time, re

    # Verificar si cloudflared YA está corriendo y obtener su URL
    try:
        import requests
        r = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
        if r.status_code == 200:
            tunnels = r.json().get("tunnels", [])
            for t in tunnels:
                url = t.get("public_url", "")
                if "trycloudflare.com" in url:
                    print(f"   ✅ Túnel detectado: {url}")
                    return url
    except Exception:
        pass

    # Intentar iniciar cloudflared automáticamente
    if shutil.which("cloudflared"):
        print(f"   📡 Iniciando cloudflared tunnel automáticamente...")
        try:
            proc = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            # Esperar a que aparezca la URL (máx 15 segundos)
            for _ in range(30):
                line = proc.stdout.readline()
                if not line:
                    break
                match = re.search(r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com', line)
                if match:
                    url = match.group(0)
                    print(f"   ✅ Túnel creado: {url}")
                    return url
                time.sleep(0.5)
        except Exception as e:
            print(f"   ⚠️  No se pudo iniciar cloudflared: {e}")

    print("   ⚠️  No se detectó túnel HTTPS.")
    print(f"   Iniciá cloudflared en otra terminal: cloudflared tunnel --url http://localhost:{port}")
    return None


def parse_args():
    p = argparse.ArgumentParser(description="QuickBooks OAuth initial flow")
    p.add_argument(
        "--environment",
        default="sandbox",
        choices=["sandbox", "production"],
        help="Entorno OAuth (default: sandbox)",
    )
    p.add_argument(
        "--company",
        default=None,
        help="Nombre de la empresa (opcional, solo informativo)",
    )
    p.add_argument(
        "--no-browser",
        action="store_true",
        help="No abrir el navegador automáticamente (imprime solo la URL)",
    )
    return p.parse_args()


def build_auth_url(client_id: str, redirect_uri: str, state: str, environment: str) -> str:
    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": SCOPE,
        "redirect_uri": redirect_uri,
        "state": state,
        "environment": environment,
    }
    qs = urllib.parse.urlencode(params)
    return f"{AUTH_BASE}?{qs}"


def exchange_code_for_tokens(client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict:
    basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    import requests
    resp = requests.post(TOKEN_URL, headers=headers, data=data, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Token exchange failed: HTTP {resp.status_code}\n{resp.text}")
    return resp.json()


def main():
    args = parse_args()
    env = dotenv_values(ENV_FILE)

    client_id = env.get("QB_CLIENT_ID")
    client_secret = env.get("QB_CLIENT_SECRET")
    redirect_uri = env.get("QB_REDIRECT_URI") or f"http://{REDIRECT_HOST}:8000/callback"

    if not client_id or not client_secret:
        print("❌ Faltan QB_CLIENT_ID o QB_CLIENT_SECRET en .env", file=sys.stderr)
        sys.exit(1)

    # Extraer puerto del redirect URI
    parsed = urllib.parse.urlparse(redirect_uri)
    port = parsed.port or 8000  # Siempre 8000 (cloudflared/ngrok forwardean HTTPS→localhost:8000)
    path = parsed.path or "/callback"

    state = secrets.token_urlsafe(24)

    # Si es producción con dominio externo, verificar que el túnel esté corriendo
    # pero NO iniciar uno nuevo si ya hay una URL configurada
    if args.environment == "production" and not parsed.hostname.startswith("localhost"):
        tunnel_url = _ensure_tunnel(port)
        if tunnel_url and tunnel_url not in redirect_uri:
            redirect_uri = f"{tunnel_url}/callback"
            set_key(ENV_FILE, "QB_REDIRECT_URI", redirect_uri)
            print(f"   ✅ .env actualizado: QB_REDIRECT_URI={redirect_uri}")
        if not tunnel_url:
            print(f"   ⚠️  Usando redirect_uri actual: {redirect_uri}")
            print(f"   Asegurate de que cloudflared esté corriendo y la URL coincida con Intuit Developer.")
        print(f"   ⚠️  Verificá que este Redirect URI esté en Intuit Developer:")
        print(f"      {redirect_uri}")

    auth_url = build_auth_url(client_id, redirect_uri, state, args.environment)

    # Result holder (compartido entre el handler y main)
    result = {"code": None, "realm_id": None, "error": None}

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, fmt, *args_):
            pass  # silenciar logs del server

        def do_GET(self):
            qs = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(qs)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if self.path.startswith(path):
                received_state = (params.get("state") or [""])[0]
                if received_state != state:
                    result["error"] = f"State mismatch: esperado {state!r}, recibido {received_state!r}"
                    self.wfile.write(b"<h1>Error</h1><p>State mismatch. Puedes cerrar esta ventana.</p>")
                    return
                if "error" in params:
                    result["error"] = f"Intuit devolvi\u00f3 error: {params.get('error')[0]}"
                    self.wfile.write(f"<h1>Error</h1><p>{result['error']}</p>".encode())
                    return
                result["code"] = (params.get("code") or [None])[0]
                result["realm_id"] = (params.get("realmId") or [None])[0]
                self.wfile.write(
                    b"<h1>Listo</h1><p>Autorizacion completada. Puedes cerrar esta ventana y volver a la terminal.</p>"
                )
            else:
                self.wfile.write(b"<h1>404</h1>")

    print("=" * 60)
    print(f"  QuickBooks OAuth flow ({args.environment})")
    if args.company:
        print(f"  Empresa: {args.company}")
    print("=" * 60)
    print()
    print("1) Abre esta URL en tu navegador (autoriza con tu Intuit user):")
    print()
    print(f"   {auth_url}")
    print()
    if not args.no_browser:
        try:
            webbrowser.open(auth_url)
            print("   (Ya se intent\u00f3 abrir el navegador autom\u00e1ticamente)")
        except Exception as e:
            print(f"   (No se pudo abrir navegador: {e})")
    print()
    print(f"2) Espera el callback a {redirect_uri}")
    print("   (El servidor local est\u00e1 escuchando...)")
    print()

    try:
        with socketserver.TCPServer(("127.0.0.1", port), CallbackHandler) as httpd:
            print(f"   Servidor HTTP en http://127.0.0.1:{port}{path}  [Ctrl+C para abortar]")
            while result["code"] is None and result["error"] is None:
                httpd.handle_request()
    except OSError as e:
        print(f"❌ No se pudo abrir puerto {port}: {e}", file=sys.stderr)
        print("   Cierra el proceso que usa ese puerto y reintenta.", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\nAbortado por el usuario.")
        sys.exit(130)

    if result["error"]:
        print(f"❌ {result['error']}", file=sys.stderr)
        sys.exit(3)

    if not result["code"]:
        print("❌ No se recibi\u00f3 code", file=sys.stderr)
        sys.exit(3)

    realm_id = result["realm_id"]
    print(f"3) Realm ID recibido: {realm_id}")
    print("4) Intercambiando code por tokens...")

    try:
        tokens = exchange_code_for_tokens(client_id, client_secret, result["code"], redirect_uri)
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(4)

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in")

    if not access_token or not refresh_token:
        print(f"❌ Respuesta inesperada (sin access/refresh): {json.dumps(tokens)[:300]}", file=sys.stderr)
        sys.exit(4)

    # Guardar en .env (NUNCA imprimir tokens)
    set_key(ENV_FILE, "QB_ACCESS_TOKEN", access_token)
    set_key(ENV_FILE, "QB_REFRESH_TOKEN", refresh_token)
    if realm_id:
        set_key(ENV_FILE, "QB_REALM_ID", realm_id)

    print()
    print("=" * 60)
    print("  \u2705 Tokens guardados en .env (no se imprimieron por seguridad)")
    print(f"  QB_REALM_ID       = {realm_id}")
    print(f"  expires_in        = {expires_in}s (~{expires_in // 3600}h)")
    print(f"  QB_ACCESS_TOKEN   = {access_token[:6]}...{access_token[-4:]}  (longitud {len(access_token)})")
    print(f"  QB_REFRESH_TOKEN  = {refresh_token[:6]}...{refresh_token[-4:]}  (longitud {len(refresh_token)})")
    print("=" * 60)
    print()
    print("Pr\u00f3ximo paso: lanzar Dexter y registrar la empresa con este Realm ID.")


if __name__ == "__main__":
    main()
