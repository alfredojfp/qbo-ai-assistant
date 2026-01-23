from dotenv import load_dotenv
import os
import base64
import requests
import json

load_dotenv()

CLIENT_ID = os.getenv("QB_CLIENT_ID")
CLIENT_SECRET = os.getenv("QB_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("QB_REFRESH_TOKEN")

if not CLIENT_ID or not CLIENT_SECRET or not REFRESH_TOKEN:
    print("Faltan QB_CLIENT_ID, QB_CLIENT_SECRET o QB_REFRESH_TOKEN en el .env")
    exit(1)

# Endpoint oficial de tokens de Intuit (producción/sandbox usan el mismo)
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

# Authorization: Basic base64(client_id:client_secret)
basic_auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
headers = {
    "Authorization": f"Basic {basic_auth}",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN
}

resp = requests.post(TOKEN_URL, headers=headers, data=data)
print("HTTP:", resp.status_code)

if resp.status_code != 200:
    print("Error al refrescar token:")
    print(resp.text)
    exit(1)

tokens = resp.json()
print("\nNUEVOS TOKENS (cópialos al .env):\n")
print("QB_ACCESS_TOKEN=", tokens.get("access_token"))
print("QB_REFRESH_TOKEN=", tokens.get("refresh_token"))
print("\nRecuerda reemplazar estos valores en tu archivo .env.")
