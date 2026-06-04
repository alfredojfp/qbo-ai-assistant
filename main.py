"""
TMP AI Assistant - Main Application
Asistente inteligente para automatización de tareas contables

Autor: Alfredo
Fecha: Enero 2026
"""

import os
import json
import csv
import re
import requests
from datetime import datetime, timedelta
import glob
import shutil
from ocr_bills import extraer_bills_de_pdf, generar_csv_preview

# ============================================================================
# AUTONOMÍA Y APRENDIZAJE - AUTO-INSTALADO 2026-01-21 22:13:27
# ============================================================================
from autonomia.autonomia_nivel1_websearch import tool_search_web, tool_search_qbo_docs
from autonomia.autonomia_nivel2_api_explorer import (
    tool_create_journal_entry,
    tool_create_transfer,
    tool_qbo_generic_request,
    tool_list_qbo_endpoints,
    tool_get_endpoint_info
)
from autonomia.autonomia_nivel3_code_executor import tool_execute_python
from autonomia.bank_feed_intelligence import (
    tool_analyze_bank_feed_for_classification,
    tool_record_bank_feed_classification,
    tool_get_classification_history_stats,
    tool_find_pattern_for_transaction
)
from autonomia.user_behavior_learning import (
    tool_learn_from_interaction,
    tool_get_user_suggestions,
    tool_record_user_correction,
    tool_get_conversation_context
)
from autonomia.dynamic_report_generator import (
    tool_generate_custom_report,
    tool_parse_date_expression
)
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple, Any

# Multi-company support
from company_manager import (
    select_company_interactive,
    load_current_company,
    save_company_selection,
    load_company_context,
    save_company_context,
    list_local_companies,
    extract_realm_id,
    save_company_meta,
    get_company_meta
)
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from difflib import SequenceMatcher

# ==================== CONFIGURACIÓN ====================
load_dotenv()

# ═════════════════════════════════════════════════════════════════
# MULTI-COMPANY GLOBALS
# ═════════════════════════════════════════════════════════════════
CURRENT_COMPANY = None
COMPANY_CONTEXT = None


# Credenciales QuickBooks
QB_ACCESS_TOKEN = os.getenv("QB_ACCESS_TOKEN")
QB_REFRESH_TOKEN = os.getenv("QB_REFRESH_TOKEN")
QB_CLIENT_ID = os.getenv("QB_CLIENT_ID")
QB_CLIENT_SECRET = os.getenv("QB_CLIENT_SECRET")
QB_REALM_ID = os.getenv("QB_REALM_ID")

# Credenciales OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# URLs QuickBooks
QB_BASE_URL = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{QB_REALM_ID}"
QB_AUTH_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

# Configuración LLM (Hybrid Model Routing)
LLM_MODEL_HEAVY = "deepseek/deepseek-chat"
LLM_MODEL_LIGHT = "meta-llama/llama-3.1-8b-instruct"
LLM_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Precios promedio (USD por millón de tokens)
PRICE_INPUT_DEEPSEEK = 0.14
PRICE_OUTPUT_DEEPSEEK = 0.28
PRICE_INPUT_LLAMA = 0.05
PRICE_OUTPUT_LLAMA = 0.08

# Archivos del sistema
FILE_CHART_CACHE = "chart_of_accounts.json"
FILE_SAVED_REPORTS = "saved_reports.json"
FILE_TOKEN_USAGE = "token_usage.csv"
FILE_TOKEN_REPORT = "token_usage_report.xlsx"
FILE_DEPOSITS_TEMPLATE = "deposits_template.csv"

# Estado de la sesión
session_state = {
    "start_time": datetime.now(),
    "input_tokens": 0,
    "output_tokens": 0,
    "total_cost": 0.0,
    "operations": {
        "searches": 0,
        "deposits": 0,
        "invoices": 0,
        "bills": 0,
        "payments": 0,
        "reports": 0,
        "csv_batches": 0
    },
    "chart_of_accounts": {},
    "saved_reports": {},
    "last_search_results": {},
    "language": "es"
}

# Historial de conversación
conversation_history = []

# ==================== UTILIDADES GENERALES ====================

def log_operation(op_type: str):
    """Registra una operación en las estadísticas de la sesión"""
    if op_type in session_state["operations"]:
        session_state["operations"][op_type] += 1

def similarity_score(a: str, b: str) -> float:
    """Calcula similitud entre dos strings (0-1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def update_env_file(key: str, value: str):
    """Actualiza una variable en el archivo .env"""
    env_path = ".env"
    lines = []

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()

    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            updated = True
            break

    if not updated:
        lines.append(f"{key}={value}\n")

    with open(env_path, 'w') as f:
        f.writelines(lines)

def parse_date(date_str: str) -> str:
    """Convierte diferentes formatos de fecha a YYYY-MM-DD"""
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")

    # Si ya está en formato correcto
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str

    # Intentar parsear diferentes formatos
    formats = [
        "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d",
        "%d/%m/%y", "%d-%m-%y",
        "%B %d, %Y", "%d %B %Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except:
            continue

    # Si no se puede parsear, usar hoy
    print(f"⚠️ No se pudo parsear fecha '{date_str}', usando hoy")
    return datetime.now().strftime("%Y-%m-%d")

def format_currency(amount: float) -> str:
    """Formatea cantidad como moneda"""
    return f"${amount:,.2f}"

# ==================== AUTENTICACIÓN QUICKBOOKS ====================

def refresh_qb_token():
    """Refresca el access token de QuickBooks"""
    global QB_ACCESS_TOKEN, QB_REFRESH_TOKEN

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": QB_REFRESH_TOKEN
    }

    response = requests.post(
        QB_AUTH_URL,
        headers=headers,
        data=data,
        auth=(QB_CLIENT_ID, QB_CLIENT_SECRET)
    )

    if response.status_code == 200:
        tokens = response.json()
        QB_ACCESS_TOKEN = tokens["access_token"]
        QB_REFRESH_TOKEN = tokens["refresh_token"]

        # Actualizar .env (como respaldo)
        update_env_file("QB_ACCESS_TOKEN", QB_ACCESS_TOKEN)
        update_env_file("QB_REFRESH_TOKEN", QB_REFRESH_TOKEN)

        # Actualizar tokens de la empresa actual
        if CURRENT_COMPANY:
            save_company_meta(
                CURRENT_COMPANY["name"], 
                CURRENT_COMPANY["realm_id"], 
                access_token=QB_ACCESS_TOKEN, 
                refresh_token=QB_REFRESH_TOKEN
            )

        print(f"✅ Token refrescado exitosamente para {CURRENT_COMPANY['name'] if CURRENT_COMPANY else 'QBO'}")
        return True
    else:
        print(f"❌ Error al refrescar token: {response.text}")
        return False

def qbo_request(method: str, endpoint: str, data: dict = None, params: dict = None) -> requests.Response:
    """Realiza request a QuickBooks con manejo automático de refresh token"""
    global QB_ACCESS_TOKEN

    headers = {
        "Authorization": f"Bearer {QB_ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = f"{QB_BASE_URL}/{endpoint}"

    if method == "GET":
        response = requests.get(url, headers=headers, params=params)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    else:
        raise ValueError(f"Método no soportado: {method}")

    # Si es 401, refrescar token y reintentar
    if response.status_code == 401:
        print("🔄 Token expirado, refrescando...")
        if refresh_qb_token():
            headers["Authorization"] = f"Bearer {QB_ACCESS_TOKEN}"
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            else:
                response = requests.post(url, headers=headers, json=data)

    return response

def qbo_query(sql: str) -> dict:
    """Ejecuta query SQL en QuickBooks"""
    response = qbo_request("GET", "query", params={"query": sql})

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text, "status": response.status_code}

# ==================== CHART OF ACCOUNTS ====================

def load_chart_of_accounts(force_refresh: bool = False) -> dict:
    """Carga Chart of Accounts desde QBO (con caché opcional)"""
    # Intentar cargar desde caché si no es refresh forzado
    if not force_refresh and os.path.exists(FILE_CHART_CACHE):
        try:
            with open(FILE_CHART_CACHE, 'r') as f:
                cache = json.load(f)
                cache_date = datetime.fromisoformat(cache.get("last_updated", "2020-01-01"))

                if datetime.now() - cache_date < timedelta(days=1):
                    print(f"📊 Chart of Accounts cargado desde caché ({len(cache['accounts'])} cuentas)")
                    return cache["accounts"]
        except Exception as e:
            print(f"⚠️ Error leyendo caché: {e}")

    # Cargar desde QBO
    print("📥 Descargando Chart of Accounts desde QuickBooks Online...")
    sql = "SELECT * FROM Account WHERE Active = true"
    result = qbo_query(sql)

    if "error" in result:
        print(f"❌ Error cargando Chart of Accounts: {result['error']}")
        return {}

    accounts_data = result.get("QueryResponse", {}).get("Account", [])

    # Procesar cuentas
    chart = {}
    categories = {"ACTIVO": 0, "PASIVO": 0, "INGRESO": 0, "GASTO": 0, "OTRO": 0}

    for acc in accounts_data:
        acc_id = acc.get("Id")
        acc_type = acc.get("AccountType")
        category = get_account_category(acc_type)

        chart[acc_id] = {
            "id": acc_id,
            "name": acc.get("Name"),
            "number": acc.get("AcctNum", ""),
            "type": acc_type,
            "subtype": acc.get("AccountSubType", ""),
            "category": category,
            "active": acc.get("Active", True),
            "balance": float(acc.get("CurrentBalance", 0))
        }

        categories[category] += 1

    # Guardar caché
    cache_data = {
        "last_updated": datetime.now().isoformat(),
        "accounts": chart
    }

    with open(FILE_CHART_CACHE, 'w') as f:
        json.dump(cache_data, f, indent=2)

    print(f"✅ {len(chart)} cuentas cargadas")
    print(f"   Activos: {categories['ACTIVO']} | Pasivos: {categories['PASIVO']} | Ingresos: {categories['INGRESO']} | Gastos: {categories['GASTO']}")

    return chart

def get_account_category(account_type: str) -> str:
    """Determina la categoría principal de una cuenta"""
    asset_types = ["Bank", "Other Current Asset", "Fixed Asset", "Other Asset", "Accounts Receivable"]
    liability_types = ["Accounts Payable", "Credit Card", "Other Current Liability", "Long Term Liability"]
    income_types = ["Income", "Other Income"]
    expense_types = ["Expense", "Other Expense", "Cost of Goods Sold"]

    if account_type in asset_types:
        return "ACTIVO"
    elif account_type in liability_types:
        return "PASIVO"
    elif account_type in income_types:
        return "INGRESO"
    elif account_type in expense_types:
        return "GASTO"
    else:
        return "OTRO"

def find_account(search_term: str, exact: bool = False, category: str = None) -> List[dict]:
    """Busca cuenta por nombre o número con fuzzy matching"""
    chart = session_state.get("chart_of_accounts", {})
    results = []

    for acc_id, acc in chart.items():
        # Filtrar por categoría si se especifica
        if category and acc["category"] != category.upper():
            continue

        # Buscar por número exacto
        if acc["number"] == search_term:
            return [acc]

        # Buscar por nombre
        if exact:
            if acc["name"].lower() == search_term.lower():
                results.append(acc)
        else:
            score = similarity_score(search_term, acc["name"])
            if score > 0.6:  # 60% de similitud mínima
                results.append({**acc, "match_score": score})

    # Ordenar por score si es fuzzy search
    if not exact and results:
        results.sort(key=lambda x: x.get("match_score", 0), reverse=True)

    return results

# ==================== TRACKING DE TOKENS ====================

def update_token_usage(input_tokens: int, output_tokens: int, model: str):
    """Actualiza los contadores de tokens y el costo acumulado de la sesión"""
    session_state["input_tokens"] += input_tokens
    session_state["output_tokens"] += output_tokens
    
    # Calcular costo de este llamado basado en el modelo
    if "deepseek" in model.lower():
        cost = (input_tokens / 1_000_000 * PRICE_INPUT_DEEPSEEK) + (output_tokens / 1_000_000 * PRICE_OUTPUT_DEEPSEEK)
    else:
        cost = (input_tokens / 1_000_000 * PRICE_INPUT_LLAMA) + (output_tokens / 1_000_000 * PRICE_OUTPUT_LLAMA)
        
    session_state["total_cost"] += cost

def calculate_session_cost() -> float:
    """Retorna el costo acumulado de la sesión"""
    return session_state.get("total_cost", 0.0)

def save_session_to_csv():
    """Guarda los datos de la sesión en el CSV histórico"""
    duration = (datetime.now() - session_state["start_time"]).total_seconds() / 60
    operations_count = sum(session_state["operations"].values())
    operations_detail = ", ".join([
        f"{count} {op}" for op, count in session_state["operations"].items() if count > 0
    ])

    row = {
        "fecha": session_state["start_time"].strftime("%Y-%m-%d"),
        "sesion_inicio": session_state["start_time"].strftime("%H:%M"),
        "sesion_fin": datetime.now().strftime("%H:%M"),
        "duracion_min": round(duration, 1),
        "input_tokens": session_state["input_tokens"],
        "output_tokens": session_state["output_tokens"],
        "total_tokens": session_state["input_tokens"] + session_state["output_tokens"],
        "costo_usd": round(calculate_session_cost(), 4),
        "operaciones": operations_count,
        "detalles": operations_detail or "Sin operaciones"
    }

    # Crear archivo si no existe
    file_exists = os.path.exists(FILE_TOKEN_USAGE)

    with open(FILE_TOKEN_USAGE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def generate_token_report():
    """Genera informe Excel con estadísticas de consumo (SOBRESCRIBE)"""
    if not os.path.exists(FILE_TOKEN_USAGE):
        print("⚠️ No hay datos de consumo todavía")
        return

    # Leer datos
    df = pd.read_csv(FILE_TOKEN_USAGE)

    # Crear Excel
    wb = Workbook()

    # Hoja 1: Resumen mensual
    ws1 = wb.active
    ws1.title = "Resumen Mensual"

    df['fecha'] = pd.to_datetime(df['fecha'])
    monthly = df.groupby(df['fecha'].dt.to_period('M')).agg({
        'costo_usd': 'sum',
        'operaciones': 'sum',
        'duracion_min': 'sum',
        'total_tokens': 'sum'
    }).reset_index()
    monthly['fecha'] = monthly['fecha'].astype(str)

    # Encabezados
    headers = ["Mes", "Costo USD", "Operaciones", "Duración (min)", "Total Tokens"]
    ws1.append(headers)

    for cell in ws1[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.font = Font(color="FFFFFF", bold=True)

    for _, row in monthly.iterrows():
        ws1.append([row['fecha'], round(row['costo_usd'], 4), int(row['operaciones']),
                   round(row['duracion_min'], 1), int(row['total_tokens'])])

    # Hoja 2: Por sesión
    ws2 = wb.create_sheet("Por Sesión")
    for r in dataframe_to_rows(df, index=False, header=True):
        ws2.append(r)

    for cell in ws2[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.font = Font(color="FFFFFF", bold=True)

    # Hoja 3: Estadísticas
    ws3 = wb.create_sheet("Estadísticas")

    total_cost = df['costo_usd'].sum()
    total_sessions = len(df)
    avg_cost = df['costo_usd'].mean()
    total_operations = df['operaciones'].sum()

    stats = [
        ["Métrica", "Valor"],
        ["Total gastado", f"${total_cost:.4f}"],
        ["Sesiones totales", total_sessions],
        ["Costo promedio/sesión", f"${avg_cost:.4f}"],
        ["Operaciones totales", int(total_operations)],
        ["Promedio operaciones/sesión", round(total_operations / total_sessions, 1)],
        ["Proyección mensual", f"${total_cost / max(len(monthly), 1):.2f}"],
        ["Proyección anual", f"${(total_cost / max(len(monthly), 1)) * 12:.2f}"]
    ]

    for row in stats:
        ws3.append(row)

    for cell in ws3[1]:
        cell.font = Font(bold=True)

    # Hoja 4: Por tipo de operación
    ws4 = wb.create_sheet("Por Tipo")

    # Analizar detalles de operaciones
    operation_counts = {}
    for detail in df['detalles'].dropna():
        for op in detail.split(", "):
            if op.strip():
                parts = op.strip().split()
                if len(parts) >= 2:
                    count = parts[0]
                    op_type = " ".join(parts[1:])
                    operation_counts[op_type] = operation_counts.get(op_type, 0) + (int(count) if count.isdigit() else 1)

    ws4.append(["Tipo de Operación", "Cantidad"])
    for cell in ws4[1]:
        cell.font = Font(bold=True)

    for op_type, count in sorted(operation_counts.items(), key=lambda x: x[1], reverse=True):
        ws4.append([op_type, count])

    # Guardar (SOBRESCRIBE)
    wb.save(FILE_TOKEN_REPORT)
    print(f"✅ Informe sobrescrito: {FILE_TOKEN_REPORT}")
    print(f"   📊 {len(df)} sesiones | ${total_cost:.4f} total | {int(total_operations)} operaciones")

# ==================== BÚSQUEDAS EN QUICKBOOKS ====================

def search_customer(search_term: str, exact: bool = False) -> List[dict]:
    """Busca clientes en QuickBooks"""
    log_operation("searches")

    if exact:
        sql = f"SELECT * FROM Customer WHERE DisplayName = '{search_term}'"
    else:
        sql = f"SELECT * FROM Customer WHERE DisplayName LIKE '%{search_term}%'"

    result = qbo_query(sql)

    if "error" in result:
        return []

    customers = result.get("QueryResponse", {}).get("Customer", [])
    results = []

    for c in customers:
        results.append({
            "id": c.get("Id"),
            "name": c.get("DisplayName"),
            "company": c.get("CompanyName", ""),
            "balance": float(c.get("Balance", 0)),
            "active": c.get("Active", True)
        })

    return results

def search_vendor(search_term: str, exact: bool = False) -> List[dict]:
    """Busca vendors en QuickBooks"""
    log_operation("searches")

    if exact:
        sql = f"SELECT * FROM Vendor WHERE DisplayName = '{search_term}'"
    else:
        sql = f"SELECT * FROM Vendor WHERE DisplayName LIKE '%{search_term}%'"

    result = qbo_query(sql)

    if "error" in result:
        return []

    vendors = result.get("QueryResponse", {}).get("Vendor", [])
    results = []

    for v in vendors:
        results.append({
            "id": v.get("Id"),
            "name": v.get("DisplayName"),
            "company": v.get("CompanyName", ""),
            "balance": float(v.get("Balance", 0)),
            "active": v.get("Active", True)
        })

    return results

def search_item(search_term: str) -> List[dict]:
    """Busca items/servicios en QuickBooks"""
    log_operation("searches")

    sql = f"SELECT * FROM Item WHERE Name LIKE '%{search_term}%'"
    result = qbo_query(sql)

    if "error" in result:
        return []

    items = result.get("QueryResponse", {}).get("Item", [])
    results = []

    for item in items:
        results.append({
            "id": item.get("Id"),
            "name": item.get("Name"),
            "type": item.get("Type"),
            "price": float(item.get("UnitPrice", 0)),
            "description": item.get("Description", ""),
            "active": item.get("Active", True)
        })

    return results

# ==================== CREACIÓN DE TRANSACCIONES ====================

def create_invoice(customer_id: str, line_items: List[dict], txn_date: str = None,
                  memo: str = None, custom_fields: dict = None) -> dict:
    """Crea un invoice en QuickBooks"""
    log_operation("invoices")

    if not txn_date:
        txn_date = datetime.now().strftime("%Y-%m-%d")

    invoice_data = {
        "CustomerRef": {"value": customer_id},
        "TxnDate": txn_date,
        "Line": []
    }

    # Agregar líneas
    for idx, item in enumerate(line_items, 1):
        line = {
            "DetailType": "SalesItemLineDetail",
            "Amount": item["amount"],
            "SalesItemLineDetail": {
                "ItemRef": {"value": item["item_id"]},
                "Qty": item.get("quantity", 1),
                "UnitPrice": item["amount"] / item.get("quantity", 1)
            }
        }

        if "description" in item:
            line["Description"] = item["description"]

        invoice_data["Line"].append(line)

    if memo:
        invoice_data["PrivateNote"] = memo

    if custom_fields:
        invoice_data["CustomField"] = [
            {"DefinitionId": k, "StringValue": v}
            for k, v in custom_fields.items()
        ]

    response = qbo_request("POST", "invoice", data=invoice_data)

    if response.status_code == 200:
        invoice = response.json()["Invoice"]
        return {
            "success": True,
            "invoice_id": invoice["Id"],
            "doc_number": invoice.get("DocNumber"),
            "total": invoice.get("TotalAmt"),
            "balance": invoice.get("Balance")
        }
    else:
        return {
            "success": False,
            "error": response.text
        }

def create_bill(vendor_id: str, line_items: List[dict], txn_date: str = None,
               due_date: str = None, memo: str = None) -> dict:
    """Crea un bill en QuickBooks"""
    log_operation("bills")

    if not txn_date:
        txn_date = datetime.now().strftime("%Y-%m-%d")

    if not due_date:
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    bill_data = {
        "VendorRef": {"value": vendor_id},
        "TxnDate": txn_date,
        "DueDate": due_date,
        "Line": []
    }

    # Agregar líneas
    for item in line_items:
        line = {
            "DetailType": "AccountBasedExpenseLineDetail",
            "Amount": item["amount"],
            "AccountBasedExpenseLineDetail": {
                "AccountRef": {"value": item["account_id"]}
            }
        }

        if "description" in item:
            line["Description"] = item["description"]

        bill_data["Line"].append(line)

    if memo:
        bill_data["PrivateNote"] = memo

    response = qbo_request("POST", "bill", data=bill_data)

    if response.status_code == 200:
        bill = response.json()["Bill"]
        return {
            "success": True,
            "bill_id": bill["Id"],
            "doc_number": bill.get("DocNumber"),
            "total": bill.get("TotalAmt"),
            "balance": bill.get("Balance")
        }
    else:
        return {
            "success": False,
            "error": response.text
        }

def create_deposit(account_id: str, line_items: List[dict], txn_date: str = None,
                  memo: str = None) -> dict:
    """Crea un depósito en QuickBooks"""
    log_operation("deposits")

    if not txn_date:
        txn_date = datetime.now().strftime("%Y-%m-%d")

    deposit_data = {
        "DepositToAccountRef": {"value": account_id},
        "TxnDate": txn_date,
        "Line": []
    }

    total_amount = 0

    # Agregar líneas
    for item in line_items:
        line = {
            "DetailType": "DepositLineDetail",
            "Amount": item["amount"],
            "DepositLineDetail": {
                "AccountRef": {"value": item["from_account_id"]}
            }
        }

        if "customer_id" in item:
            line["DepositLineDetail"]["Entity"] = {
                "Type": "Customer",
                "EntityRef": {"value": item["customer_id"]}
            }

        if "description" in item:
            line["Description"] = item["description"]

        deposit_data["Line"].append(line)
        total_amount += item["amount"]

    if memo:
        deposit_data["PrivateNote"] = memo

    response = qbo_request("POST", "deposit", data=deposit_data)

    if response.status_code == 200:
        deposit = response.json()["Deposit"]
        return {
            "success": True,
            "deposit_id": deposit["Id"],
            "total": deposit.get("TotalAmt"),
            "date": deposit.get("TxnDate")
        }
    else:
        return {
            "success": False,
            "error": response.text
        }

def create_payment(customer_id: str, amount: float, account_id: str,
                  txn_date: str = None, apply_to_invoices: List[dict] = None) -> dict:
    """Crea un payment received en QuickBooks"""
    log_operation("payments")

    if not txn_date:
        txn_date = datetime.now().strftime("%Y-%m-%d")

    payment_data = {
        "CustomerRef": {"value": customer_id},
        "TotalAmt": amount,
        "DepositToAccountRef": {"value": account_id},
        "TxnDate": txn_date
    }

    # Aplicar a invoices específicos si se proporcionan
    if apply_to_invoices:
        payment_data["Line"] = []
        for inv in apply_to_invoices:
            payment_data["Line"].append({
                "Amount": inv["amount"],
                "LinkedTxn": [{
                    "TxnId": inv["invoice_id"],
                    "TxnType": "Invoice"
                }]
            })

    response = qbo_request("POST", "payment", data=payment_data)

    if response.status_code == 200:
        payment = response.json()["Payment"]
        return {
            "success": True,
            "payment_id": payment["Id"],
            "total": payment.get("TotalAmt")
        }
    else:
        return {
            "success": False,
            "error": response.text
        }

# ==================== REPORTES ====================

def generate_pl_report(start_date: str, end_date: str,
                      accounting_method: str = "Accrual") -> pd.DataFrame:
    """Genera reporte de Profit & Loss"""
    log_operation("reports")

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "accounting_method": accounting_method
    }

    response = qbo_request("GET", "reports/ProfitAndLoss", params=params)

    if response.status_code != 200:
        print(f"❌ Error generando reporte: {response.text}")
        return pd.DataFrame()

    report_data = response.json()
    rows_data = report_data.get("Rows", {}).get("Row", [])

    # Parsear datos del reporte
    data = []

    def parse_row(row, parent_name=""):
        if row.get("type") == "Data":
            cols = row.get("ColData", [])
            if len(cols) >= 2:
                account_name = cols[0].get("value", "")
                amount = cols[1].get("value", "0")

                try:
                    amount_float = float(amount.replace(",", ""))
                except:
                    amount_float = 0

                data.append({
                    "cuenta": account_name,
                    "categoria": parent_name,
                    "monto": amount_float
                })

        # Procesar subrows recursivamente
        if "Rows" in row:
            current_name = row.get("Header", {}).get("ColData", [{}])[0].get("value", parent_name)
            for subrow in row["Rows"].get("Row", []):
                parse_row(subrow, current_name)

    for row in rows_data:
        parse_row(row)

    df = pd.DataFrame(data)
    return df

def generate_balance_sheet(as_of_date: str, accounting_method: str = "Accrual") -> pd.DataFrame:
    """Genera reporte de Balance Sheet"""
    log_operation("reports")

    params = {
        "date": as_of_date,
        "accounting_method": accounting_method
    }

    response = qbo_request("GET", "reports/BalanceSheet", params=params)

    if response.status_code != 200:
        print(f"❌ Error generando reporte: {response.text}")
        return pd.DataFrame()

    report_data = response.json()
    rows_data = report_data.get("Rows", {}).get("Row", [])

    data = []

    def parse_row(row, parent_name=""):
        if row.get("type") == "Data":
            cols = row.get("ColData", [])
            if len(cols) >= 2:
                account_name = cols[0].get("value", "")
                amount = cols[1].get("value", "0")

                try:
                    amount_float = float(amount.replace(",", ""))
                except:
                    amount_float = 0

                data.append({
                    "cuenta": account_name,
                    "categoria": parent_name,
                    "monto": amount_float
                })

        if "Rows" in row:
            current_name = row.get("Header", {}).get("ColData", [{}])[0].get("value", parent_name)
            for subrow in row["Rows"].get("Row", []):
                parse_row(subrow, current_name)

    for row in rows_data:
        parse_row(row)

    df = pd.DataFrame(data)
    return df

def save_report_config(name: str, config: dict):
    """Guarda configuración de reporte para uso futuro"""
    saved_reports = session_state.get("saved_reports", {})

    saved_reports[name] = {
        "config": config,
        "created": datetime.now().isoformat(),
        "last_used": datetime.now().isoformat()
    }

    session_state["saved_reports"] = saved_reports

    with open(FILE_SAVED_REPORTS, 'w') as f:
        json.dump(saved_reports, f, indent=2)

    print(f"✅ Reporte '{name}' guardado")

def load_report_config(name: str) -> Optional[dict]:
    """Carga configuración de reporte guardado"""
    saved_reports = session_state.get("saved_reports", {})

    if name in saved_reports:
        config = saved_reports[name]
        config["last_used"] = datetime.now().isoformat()

        with open(FILE_SAVED_REPORTS, 'w') as f:
            json.dump(saved_reports, f, indent=2)

        return config["config"]

    return None

# ==================== PROCESAMIENTO CSV ====================

def process_deposits_csv(csv_path: str) -> dict:
    """Procesa archivo CSV de depósitos y los crea en batch"""
    log_operation("csv_batches")

    if not os.path.exists(csv_path):
        return {"success": False, "error": f"Archivo no encontrado: {csv_path}"}

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return {"success": False, "error": f"Error leyendo CSV: {e}"}

    required_cols = ["customer_name", "amount", "from_account", "to_account", "date"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        return {"success": False, "error": f"Columnas faltantes: {missing_cols}"}

    results = {
        "total": len(df),
        "success": 0,
        "errors": []
    }

    for idx, row in df.iterrows():
        # Buscar customer
        customers = search_customer(row["customer_name"])
        if not customers:
            results["errors"].append(f"Fila {idx+1}: Cliente '{row['customer_name']}' no encontrado")
            continue

        customer_id = customers[0]["id"]

        # Buscar cuentas
        from_accounts = find_account(row["from_account"])
        to_accounts = find_account(row["to_account"])

        if not from_accounts or not to_accounts:
            results["errors"].append(f"Fila {idx+1}: Cuenta no encontrada")
            continue

        from_account_id = from_accounts[0]["id"]
        to_account_id = to_accounts[0]["id"]

        # Crear depósito
        deposit_result = create_deposit(
            account_id=to_account_id,
            line_items=[{
                "amount": float(row["amount"]),
                "from_account_id": from_account_id,
                "customer_id": customer_id,
                "description": row.get("memo", "")
            }],
            txn_date=parse_date(str(row["date"]))
        )

        if deposit_result["success"]:
            results["success"] += 1
        else:
            results["errors"].append(f"Fila {idx+1}: {deposit_result['error']}")

    return results

def create_deposits_template():
    """Crea archivo CSV template para depósitos"""
    template_data = {
        "customer_name": ["Cliente Ejemplo 1", "Cliente Ejemplo 2"],
        "amount": [1500.00, 2300.50],
        "from_account": ["Client Retainers", "Prepaid Labour"],
        "to_account": ["Checking Account", "Checking Account"],
        "date": ["2026-01-15", "2026-01-16"],
        "memo": ["Anticipo proyecto A", "Prepago servicios enero"]
    }

    df = pd.DataFrame(template_data)
    df.to_csv(FILE_DEPOSITS_TEMPLATE, index=False)

    print(f"✅ Template creado: {FILE_DEPOSITS_TEMPLATE}")

# ==================== BANK FEED PROCESSING ====================

def validar_suma_deposit(lines: List[dict], bank_feed_amount: float) -> Tuple[bool, float]:
    """Valida que la suma de las líneas coincida con el monto del Bank Feed"""
    total = sum(float(line['amount']) for line in lines)
    diferencia = abs(total - bank_feed_amount)
    es_valido = diferencia < 0.01  # Tolerancia de 1 centavo
    return es_valido, diferencia

def agrupar_bank_feed_por_deposit_id(csv_file: str) -> Optional[dict]:
    """
    Lee el CSV de Bank Feed y agrupa las líneas por deposit_id

    Formato esperado del CSV:
    bank_feed_date,bank_feed_amount,deposit_id,line_type,customer_name,amount,account,memo

    Returns:
        dict: {deposit_id: {'date': ..., 'amount': ..., 'lines': [...]}}
    """
    from collections import defaultdict

    deposits = defaultdict(lambda: {'lines': []})

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                deposit_id = row['deposit_id'].strip()

                if not deposit_id:
                    print(f"⚠️  Fila {row_num}: deposit_id vacío, saltando...")
                    continue

                # Guardar metadata del depósito
                if 'date' not in deposits[deposit_id]:
                    deposits[deposit_id]['date'] = row['bank_feed_date'].strip()
                    deposits[deposit_id]['bank_feed_amount'] = float(row['bank_feed_amount'])
                    deposits[deposit_id]['deposit_id'] = deposit_id

                # Agregar línea
                line = {
                    'line_type': row['line_type'].strip().lower(),
                    'customer_name': row['customer_name'].strip() if row['customer_name'].strip() else None,
                    'amount': float(row['amount']),
                    'account': row['account'].strip(),
                    'memo': row['memo'].strip()
                }

                deposits[deposit_id]['lines'].append(line)

        return dict(deposits)

    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {csv_file}")
        return None
    except Exception as e:
        print(f"❌ Error al procesar CSV: {e}")
        return None

def crear_deposito_bank_feed(fecha: str, lines: List[dict], 
                             cuenta_bancaria_id: str = None,
                             memo_principal: str = "Bank Feed Deposit") -> dict:
    """
    Crea un depósito en QuickBooks con múltiples líneas (splits)
    incluyendo ingresos y fees

    Args:
        fecha: Fecha del depósito (YYYY-MM-DD)
        lines: Lista de líneas con format:
               [{'line_type': 'income'|'fee', 'customer_name': str, 
                 'amount': float, 'account': str, 'memo': str}, ...]
        cuenta_bancaria_id: ID de la cuenta bancaria destino (opcional, busca Checking)
        memo_principal: Memo general del depósito

    Returns:
        dict: {'success': bool, 'deposit_id': str, 'message': str}
    """
    # Determinar cuenta bancaria destino
    if not cuenta_bancaria_id:
        # Buscar Checking Account
        checking_accounts = find_account("Checking", category="ACTIVO")
        if not checking_accounts:
            return {
                'success': False,
                'message': 'No se encontró Checking Account'
            }
        cuenta_bancaria_id = checking_accounts[0]['id']

    # Construir las líneas del depósito
    deposit_lines = []

    for line in lines:
        line_type = line['line_type']
        customer_name = line['customer_name']
        amount = line['amount']
        account_name = line['account']
        memo = line['memo']

        # Buscar la cuenta contable
        accounts = find_account(account_name)
        if not accounts:
            return {
                'success': False,
                'message': f"Cuenta no encontrada: {account_name}"
            }

        account_id = accounts[0]['id']

        # Construir línea del depósito
        deposit_line = {
            "Amount": abs(amount),
            "DetailType": "DepositLineDetail",
            "DepositLineDetail": {
                "AccountRef": {"value": account_id}
            },
            "Description": memo
        }

        # Si tiene cliente asociado, agregarlo
        if customer_name:
            customers = search_customer(customer_name)
            if customers:
                deposit_line["DepositLineDetail"]["Entity"] = {
                    "EntityRef": {
                        "value": customers[0]['id'], 
                        "name": customers[0]['name']
                    },
                    "Type": "Customer"
                }

        deposit_lines.append(deposit_line)

    # Crear el depósito
    deposit_body = {
        "TxnDate": fecha,
        "DepositToAccountRef": {"value": cuenta_bancaria_id},
        "Line": deposit_lines,
        "PrivateNote": memo_principal
    }

    response = qbo_request("POST", "deposit", data=deposit_body)

    if response.status_code != 200:
        return {
            'success': False,
            'message': f"Error QuickBooks: {response.status_code} - {response.text[:200]}"
        }

    deposit_created = response.json().get("Deposit", {})

    return {
        'success': True,
        'deposit_id': deposit_created.get('Id'),
        'message': 'Depósito creado exitosamente',
        'total_amount': deposit_created.get('TotalAmt')
    }

def procesar_csv_bank_feed(csv_file: str) -> dict:
    """
    Procesa un CSV de Bank Feed y crea depósitos con splits en QuickBooks

    Args:
        csv_file: Ruta al archivo CSV

    Returns:
        dict: Estadísticas del procesamiento
    """
    print(f"\n📁 Procesando Bank Feed CSV: {csv_file}")
    print("="*60)

    # 1. Agrupar por deposit_id
    deposits = agrupar_bank_feed_por_deposit_id(csv_file)

    if not deposits:
        return {
            'success': False,
            'message': 'Error al leer el archivo CSV'
        }

    print(f"\n✅ {len(deposits)} depósito(s) encontrado(s) en el CSV")
    print()

    # 2. Procesar cada depósito
    results = {
        'total': len(deposits),
        'success': 0,
        'errors': 0,
        'details': []
    }

    for dep_id, dep_data in deposits.items():
        print(f"🔄 Procesando {dep_id}...")

        bank_feed_amount = dep_data['bank_feed_amount']
        date = dep_data['date']
        lines = dep_data['lines']

        # Validar suma
        es_valido, diferencia = validar_suma_deposit(lines, bank_feed_amount)

        if not es_valido:
            error_msg = f"  ❌ Suma no cuadra: diferencia de ${diferencia:.2f}"
            print(error_msg)
            results['errors'] += 1
            results['details'].append({
                'deposit_id': dep_id,
                'status': 'error',
                'message': error_msg
            })
            continue

        print(f"  ✓ Suma validada: ${bank_feed_amount:.2f}")

        # Crear el depósito con splits
        resultado = crear_deposito_bank_feed(
            fecha=date,
            lines=lines,
            memo_principal=f"Bank Feed Classification - {dep_id}"
        )

        if resultado['success']:
            print(f"  ✅ Depósito creado (ID: {resultado['deposit_id']})")
            print(f"     • {len(lines)} líneas procesadas")
            print(f"     • Monto total: ${bank_feed_amount:.2f}")
            results['success'] += 1
            results['details'].append({
                'deposit_id': dep_id,
                'qb_deposit_id': resultado['deposit_id'],
                'status': 'success',
                'amount': bank_feed_amount,
                'lines': len(lines)
            })
        else:
            print(f"  ❌ Error: {resultado['message']}")
            results['errors'] += 1
            results['details'].append({
                'deposit_id': dep_id,
                'status': 'error',
                'message': resultado['message']
            })

        print()

    # 3. Resumen final
    print("="*60)
    print("📊 RESUMEN DEL PROCESAMIENTO")
    print("="*60)
    print(f"Total depósitos: {results['total']}")
    print(f"✅ Exitosos: {results['success']}")
    print(f"❌ Errores: {results['errors']}")

    log_operation("csv_batches")

    return results



def procesar_reconciliacion_bancaria(csv_file: str) -> dict:
    """Procesa CSV de reconciliación bancaria con balance opcional"""
    from decimal import Decimal

    print(f"\n🏦 RECONCILIACIÓN BANCARIA")
    print("="*70)
    print(f"📁 Archivo: {csv_file}\n")

    if not os.path.exists(csv_file):
        return {"success": False, "error": f"Archivo no encontrado: {csv_file}"}

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            required = ['date', 'description', 'debit', 'credit']
            missing = [col for col in required if col not in headers]
            if missing:
                return {"success": False, "error": f"Columnas faltantes: {missing}"}
            has_balance = 'balance' in headers
            balance_mode = "CON balance" if has_balance else "SIN balance"
            print(f"📋 Modo: {balance_mode}")
            rows = list(reader)
    except Exception as e:
        return {"success": False, "error": f"Error leyendo CSV: {e}"}

    if not rows:
        return {"success": False, "error": "CSV vacío"}

    transactions = []
    opening_balance = Decimal('0')
    ending_balance = Decimal('0')
    running_balance = Decimal('0')
    total_debits = Decimal('0')
    total_credits = Decimal('0')
    validation_errors = []

    for idx, row in enumerate(rows, start=2):
        date = row['date'].strip()
        description = row['description'].strip()
        debit_str = row['debit'].strip()
        credit_str = row['credit'].strip()
        reference = row.get('reference', '').strip()
        balance_str = row.get('balance', '').strip() if has_balance else ''

        try:
            debit = Decimal(debit_str) if debit_str else Decimal('0')
            credit = Decimal(credit_str) if credit_str else Decimal('0')
            balance = Decimal(balance_str) if balance_str else None
        except:
            validation_errors.append(f"Fila {idx}: Formato inválido")
            continue

        desc_lower = description.lower()
        is_opening = 'opening' in desc_lower and 'balance' in desc_lower
        is_ending = 'ending' in desc_lower and 'balance' in desc_lower

        if is_opening:
            opening_balance = balance if (has_balance and balance) else Decimal('0')
            running_balance = opening_balance
            continue

        if is_ending:
            if has_balance and balance:
                ending_balance = balance
            continue

        if debit > 0 and credit > 0:
            validation_errors.append(f"Fila {idx}: Debit Y credit simultáneos")
            continue

        if debit > 0:
            total_debits += debit
            running_balance -= debit
        if credit > 0:
            total_credits += credit
            running_balance += credit

        if has_balance and balance is not None:
            diff = abs(balance - running_balance)
            if diff > Decimal('0.01'):
                validation_errors.append(f"Fila {idx}: Balance no cuadra")

        transactions.append({
            'row_num': idx, 'date': date, 'description': description,
            'debit': float(debit), 'credit': float(credit),
            'balance': float(running_balance), 'reference': reference
        })

    calculated_ending = opening_balance + total_credits - total_debits

    if validation_errors:
        return {"success": False, "error": "Validación falló", "validation_errors": validation_errors}

    if not transactions:
        return {"success": False, "error": "No hay transacciones"}

    checking_accounts = find_account("Checking", category="ACTIVO")
    if not checking_accounts:
        checking_accounts = find_account("Bank", category="ACTIVO")
    if not checking_accounts:
        return {"success": False, "error": "No se encontró cuenta bancaria"}

    bank_account_id = checking_accounts[0]['id']
    income_accounts = find_account("Income", category="INGRESO")
    expense_accounts = find_account("Expense", category="GASTO")

    if not income_accounts or not expense_accounts:
        return {"success": False, "error": "Cuentas contables no encontradas"}

    income_account_id = income_accounts[0]['id']
    expense_account_id = expense_accounts[0]['id']

    results = {"total": len(transactions), "success": 0, "errors": 0, "details": []}

    for txn in transactions:
        try:
            if txn['credit'] > 0:
                amount = txn['credit']
                result = create_deposit(
                    account_id=bank_account_id,
                    line_items=[{"amount": amount, "from_account_id": income_account_id, "description": txn['description']}],
                    txn_date=parse_date(txn['date']),
                    memo=f"Reconciliation - {txn['reference']}" if txn['reference'] else "Bank Reconciliation"
                )
            else:
                amount = txn['debit']
                vendors = search_vendor("Bank Charges")
                if not vendors:
                    results['errors'] += 1
                    continue
                vendor_id = vendors[0]['id']
                result = create_bill(
                    vendor_id=vendor_id,
                    line_items=[{"amount": amount, "account_id": expense_account_id, "description": txn['description']}],
                    txn_date=parse_date(txn['date']),
                    memo=f"Reconciliation - {txn['reference']}" if txn['reference'] else "Bank Reconciliation"
                )

            if result.get('success'):
                results['success'] += 1
            else:
                results['errors'] += 1
        except Exception as e:
            results['errors'] += 1

    log_operation("csv_batches")
    results['success'] = results['success'] > 0
    results['summary'] = {
        'opening_balance': float(opening_balance),
        'ending_balance': float(calculated_ending),
        'total_credits': float(total_credits),
        'total_debits': float(total_debits),
        'mode': balance_mode
    }
SYSTEM_PROMPT = """
Eres Dexter, un asistente de IA experto para QuickBooks. Tu tono es natural, amigable y profesional.
Tu usuario se llama Alfredo, dirígete a él de manera respetuosa pero cercana.

CAPACIDADES:
✅ Clasificación | ✅ Reportes | ✅ Facturas | ✅ Búsquedas | ✅ OCR | ✅ Gestión Multi-empresa

GUÍA INTERACTIVA:
- Si detectas que Alfredo quiere realizar una tarea compleja (OCR, Reconciliación, Reportes Pro), ofrécele guiarlo paso a paso.
- Si Alfredo parece perdido, sugiere el uso de comandos de ayuda como "ayuda ocr" o "ayuda bancos".
- Mantén una actitud proactiva: si necesitas que Alfredo coloque archivos en una carpeta, indícale la ruta exacta (ej: /Pending bills/).
- Siempre consulta el manual de usuario (MANUAL_USUARIO.md) si tienes dudas sobre los procedimientos internos.

Responde SIEMPRE en el IDIOMA SELECCIONADO por el usuario. 
Si el idioma es ES: Responde en español, de manera concisa y profesional.
Si el idioma es EN: Respond in English, concisely and professionally.
Actualmente el idioma seleccionado es: {idioma}"""

def call_llm(user_message: str, tools: List[dict] = None, max_iterations: int = 5) -> str:
    """Llama al LLM con soporte de tools y maneja iteraciones automáticamente"""
    # Agregar contexto del chart of accounts al mensaje del sistema
    chart_summary = f"\\n\\nCHART OF ACCOUNTS EN MEMORIA: {len(session_state.get('chart_of_accounts', {}))} cuentas disponibles."

    # Construir el prompt del sistema local con los detalles necesarios
    current_lang = session_state.get("language", "es").upper()
    local_system_content = SYSTEM_PROMPT.replace("{idioma}", current_lang)
    
    if necesita_chart(user_message):
        local_system_content += chart_summary
    
    recent_hist, context_hint = build_conversation_context(conversation_history)
    local_system_content += "\n" + context_hint

    relevant_tools = get_relevant_tools(user_message) if tools else []

    # Solo agregar mensaje del usuario si no está vacío (para tool calls iterativos)
    if user_message:
        conversation_history.append({
            "role": "user",
            "content": user_message
        })

    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Construir mensajes incluyendo el historial actualizado en cada iteración
        messages = [
            {"role": "system", "content": local_system_content},
            *conversation_history[-(max_iterations*4+10):] # Ventana de contexto amplia
        ]

        # Seleccionar modelo basado en complejidad
        # Si ya estamos en una iteración avanzada (tool calls), mantenemos el modelo original
        if iteration == 1:
            msg_lower = user_message.lower()
            complejo = any(kw in msg_lower for kw in [
                "analiza", "porque", "compara", "explica", "clasifica", "extrae", 
                "informe", "reporte", "balance", "p&l", "asiento", "journal", "ocr"
            ])
            selected_model = LLM_MODEL_HEAVY if complejo else LLM_MODEL_LIGHT
            self_model = selected_model # Tracking interno
        else:
            selected_model = self_model

        payload = {
            "model": selected_model,
            "messages": messages,
            "temperature": 0.3
        }

        if tools:
            payload["tools"] = relevant_tools
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/alfredo-qbo-assistant",
            "X-Title": "QuickBooks AI Assistant"
        }

        response = requests.post(LLM_API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            error_msg = f"Error LLM ({response.status_code}): {response.text}"
            print(f"❌ {error_msg}")
            return error_msg

        result = response.json()

        # Actualizar tokens y costo
        usage = result.get("usage", {})
        update_token_usage(
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
            selected_model
        )

        assistant_message = result["choices"][0]["message"]
        conversation_history.append(assistant_message)

        # Si no hay tool calls, retornar contenido
        if not assistant_message.get("tool_calls"):
            return assistant_message.get("content", "")

        # Procesar tool calls
        for tool_call in assistant_message["tool_calls"]:
            function_name = tool_call["function"]["name"]

            try:
                arguments = json.loads(tool_call["function"]["arguments"])
            except json.JSONDecodeError:
                arguments = {}

            # Ejecutar tool
            if function_name in TOOL_FUNCTIONS:
                try:
                    result_data = TOOL_FUNCTIONS[function_name](**arguments)
                    result_str = json.dumps(result_data, ensure_ascii=False)
                except Exception as e:
                    result_str = json.dumps({"error": str(e)})
            else:
                result_str = json.dumps({"error": f"Tool '{function_name}' no encontrado"})

            # Agregar resultado al historial
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result_str
            })

        # Continuar iteración (el LLM procesará los resultados de los tools)

    # Si llegamos aquí, se alcanzó el máximo de iteraciones
    return "Se alcanzó el límite de iteraciones. Por favor, reformula tu pregunta."

# ==================== TOOLS PARA EL LLM ====================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_cliente",
            "description": "Busca clientes en QuickBooks por nombre (fuzzy search). Retorna lista de clientes con ID, nombre, balance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre o parte del nombre del cliente a buscar"
                    },
                    "exacto": {
                        "type": "boolean",
                        "description": "Si es true, busca coincidencia exacta. Por defecto false (fuzzy).",
                        "default": False
                    }
                },
                "required": ["nombre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_vendor",
            "description": "Busca vendors/proveedores en QuickBooks por nombre.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre del vendor a buscar"
                    }
                },
                "required": ["nombre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_cuenta",
            "description": "Busca cuenta contable por nombre o número en el Chart of Accounts. Usa fuzzy matching.",
            "parameters": {
                "type": "object",
                "properties": {
                    "termino": {
                        "type": "string",
                        "description": "Nombre o número de cuenta a buscar"
                    },
                    "categoria": {
                        "type": "string",
                        "enum": ["ACTIVO", "PASIVO", "INGRESO", "GASTO"],
                        "description": "Filtrar por categoría de cuenta (opcional)"
                    }
                },
                "required": ["termino"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_item",
            "description": "Busca items/servicios en QuickBooks por nombre.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre del item/servicio"
                    }
                },
                "required": ["nombre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crear_invoice",
            "description": "Crea un invoice/factura en QuickBooks. Requiere customer_id y líneas con items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "ID del cliente (obtener con buscar_cliente)"
                    },
                    "lineas": {
                        "type": "array",
                        "description": "Lista de líneas del invoice",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_id": {"type": "string"},
                                "amount": {"type": "number"},
                                "quantity": {"type": "number", "default": 1},
                                "description": {"type": "string"}
                            },
                            "required": ["item_id", "amount"]
                        }
                    },
                    "fecha": {
                        "type": "string",
                        "description": "Fecha en formato YYYY-MM-DD (opcional, usa hoy por defecto)"
                    },
                    "memo": {
                        "type": "string",
                        "description": "Nota privada (opcional)"
                    }
                },
                "required": ["customer_id", "lineas"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crear_bill",
            "description": "Crea un bill/cuenta por pagar en QuickBooks. Requiere vendor_id y líneas con cuentas de gasto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {
                        "type": "string",
                        "description": "ID del vendor (obtener con buscar_vendor)"
                    },
                    "lineas": {
                        "type": "array",
                        "description": "Lista de líneas del bill con cuentas de gasto",
                        "items": {
                            "type": "object",
                            "properties": {
                                "account_id": {"type": "string", "description": "ID de cuenta de gasto"},
                                "amount": {"type": "number"},
                                "description": {"type": "string"}
                            },
                            "required": ["account_id", "amount"]
                        }
                    },
                    "fecha": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                    "fecha_vencimiento": {"type": "string", "description": "Fecha vencimiento YYYY-MM-DD"},
                    "memo": {"type": "string"}
                },
                "required": ["vendor_id", "lineas"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crear_deposito",
            "description": "Crea un depósito en QuickBooks. Mueve dinero de cuentas origen (ej: Client Retainers) a cuenta destino (ej: Checking).",
            "parameters": {
                "type": "object",
                "properties": {
                    "cuenta_destino_id": {
                        "type": "string",
                        "description": "ID de cuenta bancaria destino (obtener con buscar_cuenta)"
                    },
                    "lineas": {
                        "type": "array",
                        "description": "Lista de líneas del depósito",
                        "items": {
                            "type": "object",
                            "properties": {
                                "cuenta_origen_id": {"type": "string", "description": "ID cuenta origen"},
                                "amount": {"type": "number"},
                                "customer_id": {"type": "string", "description": "ID cliente (opcional)"},
                                "description": {"type": "string"}
                            },
                            "required": ["cuenta_origen_id", "amount"]
                        }
                    },
                    "fecha": {"type": "string"},
                    "memo": {"type": "string"}
                },
                "required": ["cuenta_destino_id", "lineas"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crear_pago",
            "description": "Registra un pago recibido de un cliente en QuickBooks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "amount": {"type": "number"},
                    "cuenta_id": {"type": "string", "description": "Cuenta donde se deposita el pago"},
                    "fecha": {"type": "string"},
                    "aplicar_a_invoices": {
                        "type": "array",
                        "description": "Lista de invoices a los que aplicar el pago",
                        "items": {
                            "type": "object",
                            "properties": {
                                "invoice_id": {"type": "string"},
                                "amount": {"type": "number"}
                            }
                        }
                    }
                },
                "required": ["customer_id", "amount", "cuenta_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generar_reporte_pl",
            "description": "Genera reporte de Profit & Loss (P&L / Estado de Resultados).",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_inicio": {"type": "string", "description": "Fecha inicio YYYY-MM-DD"},
                    "fecha_fin": {"type": "string", "description": "Fecha fin YYYY-MM-DD"},
                    "metodo": {"type": "string", "enum": ["Accrual", "Cash"], "default": "Accrual"}
                },
                "required": ["fecha_inicio", "fecha_fin"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generar_balance_sheet",
            "description": "Genera reporte de Balance Sheet (Balance General).",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha": {"type": "string", "description": "Fecha del balance YYYY-MM-DD"},
                    "metodo": {"type": "string", "enum": ["Accrual", "Cash"], "default": "Accrual"}
                },
                "required": ["fecha"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "guardar_reporte",
            "description": "Guarda configuración de un reporte para uso futuro.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre para identificar el reporte"},
                    "config": {"type": "object", "description": "Configuración del reporte"}
                },
                "required": ["nombre", "config"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cargar_reporte",
            "description": "Carga configuración de un reporte guardado previamente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string"}
                },
                "required": ["nombre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_reportes_guardados",
            "description": "Lista todos los reportes guardados por el usuario.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "procesar_csv_depositos",
            "description": "Procesa archivo CSV con múltiples depósitos y los crea en batch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ruta_archivo": {"type": "string", "description": "Ruta del archivo CSV"}
                },
                "required": ["ruta_archivo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crear_template_csv",
            "description": "Crea archivo CSV template para depósitos batch.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_estadisticas_tokens",
            "description": "Muestra estadísticas de consumo de tokens del LLM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "periodo": {
                        "type": "string",
                        "enum": ["sesion", "hoy", "mes"],
                        "description": "Periodo a consultar"
                    }
                },
                "required": ["periodo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generar_informe_tokens",
            "description": "Genera informe Excel con estadísticas detalladas de consumo (sobrescribe archivo).",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "refrescar_chart_accounts",
            "description": "Refresca el Chart of Accounts desde QuickBooks Online (fuerza actualización del caché).",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "procesar_bank_feed_csv",
            "description": "Procesa archivo CSV de Bank Feed y clasifica depósitos con splits múltiples (income + fees). Formato CSV: bank_feed_date,bank_feed_amount,deposit_id,line_type,customer_name,amount,account,memo",
            "parameters": {
                "type": "object",
                "properties": {
                    "archivo_csv": {
                        "type": "string",
                        "description": "Ruta del archivo CSV de Bank Feed"
                    }
                },
                "required": ["archivo_csv"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "procesar_reconciliacion_bancaria",
            "description": "Procesa CSV de reconciliación bancaria y crea transacciones en QuickBooks. Soporta dos formatos: CON balance (6 columnas con validación completa) o SIN balance (5 columnas con cálculo automático). Columnas obligatorias: date, description, debit, credit. Columnas opcionales: balance, reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "archivo_csv": {
                        "type": "string",
                        "description": "Ruta del archivo CSV de reconciliación bancaria"
                    }
                },
                "required": ["archivo_csv"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "taggear_reconciliacion",
            "description": "BNK-RECON tagger: marca transactions existentes en QBO (Deposit.Memo, Bill.PrivateNote, Purchase.PrivateNote) con el tag BNK-RECON-YYYY-MM-xxxxx. NO crea transactions nuevas, solo agrega tags visibles. Útil para reconciliación en QBO UI. Columnas requeridas del CSV: date, description, amount.",
            "parameters": {
                "type": "object",
                "properties": {
                    "archivo_csv": {
                        "type": "string",
                        "description": "Ruta del archivo CSV del bank statement (columnas: date, description, amount)"
                    },
                    "cuenta_id": {
                        "type": "string",
                        "description": "ID de la cuenta bancaria en QBO (opcional; se auto-detecta por categoría BANK si se omite)"
                    },
                    "fecha_inicio": {
                        "type": "string",
                        "description": "Fecha de inicio del período en formato YYYY-MM-DD (opcional; default: primer día del mes actual)"
                    },
                    "fecha_fin": {
                        "type": "string",
                        "description": "Fecha de fin del período en formato YYYY-MM-DD (opcional; default: último día del mes actual)"
                    },
                    "dias_fuzzy": {
                        "type": "integer",
                        "description": "Tolerancia en días para fuzzy match (default 2)",
                        "default": 2
                    },
                    "monto_fuzzy": {
                        "type": "number",
                        "description": "Tolerancia en USD para diferencia de monto (default 0.50)",
                        "default": 0.50
                    }
                },
                "required": ["archivo_csv"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "limpiar_tags_reconciliacion",
            "description": "Limpia los tags BNK-RECON aplicados por un batch previo. Lee el reporte del batch y borra los Memo/PrivateNote. Útil para deshacer una reconciliación de prueba.",
            "parameters": {
                "type": "object",
                "properties": {
                    "batch_id": {
                        "type": "string",
                        "description": "ID del batch cuyos tags se quieren limpiar"
                    }
                },
                "required": ["batch_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "depositar_lote_csv",
            "description": "Procesa CSV de deposits multi-cliente usando el motor batch con state machine, disambiguación interactiva y dry-run obligatorio. Columnas requeridas: date, client_name, amount. Si un cliente no existe, pregunta si crearlo. Si confirmar=false, solo hace dry-run sin crear nada en QBO.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ruta_archivo": {
                        "type": "string",
                        "description": "Ruta al CSV de líneas de deposit (date, client_name, amount)"
                    },
                    "cuenta_banco_id": {
                        "type": "string",
                        "description": "ID de la cuenta bancaria destino (opcional; se auto-detecta)"
                    },
                    "cuenta_ingreso_id": {
                        "type": "string",
                        "description": "ID de la cuenta de ingreso (opcional; se auto-detecta)"
                    },
                    "confirmar": {
                        "type": "boolean",
                        "description": "Si False, solo corre dry-run sin crear (default True)",
                        "default": True
                    }
                },
                "required": ["ruta_archivo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "procesar_lote_bills",
            "description": (
                "Procesa un lote de bills/invoices desde un PDF usando OCR con Gemini. "
                "Busca automáticamente en la carpeta 'Pending bills'. "
                "Si hay un solo PDF, lo procesa automáticamente. "
                "Si hay múltiples, lista los disponibles para que el usuario elija. "
                "Extrae: vendor, customer, invoice#, date, total, tax. "
                "Genera CSV preview para revisión antes de crear Bills en QuickBooks."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_archivo": {
                        "type": "string",
                        "description": (
                            "Nombre del archivo PDF a procesar (opcional). "
                            "Si no se especifica y hay solo 1 PDF en 'Pending bills', "
                            "se procesa automáticamente. Puede ser nombre parcial "
                            "(ej: 'okna' encontrará 'DONE-Okna-Invoices-dated1.8.26.pdf')"
                        )
                    }
                },
                "required": []
            }
        }
    },
    # ========== TOOLS DE AUTONOMÍA ==========
    {
        "type": "function",
        "function": {
            "name": "buscarenweb",
            "description": "Busca información actualizada en internet (vía DuckDuckGo).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Consulta de búsqueda"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscardocsqbo",
            "description": "Busca específicamente en la documentación oficial de QuickBooks Online API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Consulta técnica sobre la API"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crearasientodiario",
            "description": "Crea un Journal Entry (asiento contable) complejo en QuickBooks. Los débitos deben ser iguales a los créditos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lines": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "account_id": {"type": "string"},
                                "amount": {"type": "number"},
                                "posting_type": {"type": "string", "enum": ["Debit", "Credit"]},
                                "description": {"type": "string"}
                            },
                            "required": ["account_id", "amount", "posting_type"]
                        }
                    },
                    "txn_date": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                    "memo": {"type": "string"}
                },
                "required": ["lines", "txn_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "creartransferencia",
            "description": "Crea una transferencia de fondos entre dos cuentas bancarias en QuickBooks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_account_id": {"type": "string"},
                    "to_account_id": {"type": "string"},
                    "amount": {"type": "number"},
                    "txn_date": {"type": "string"},
                    "memo": {"type": "string"}
                },
                "required": ["from_account_id", "to_account_id", "amount", "txn_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "qborequestgenerico",
            "description": "Realiza una petición genérica a cualquier endpoint de la API de QuickBooks v3.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "enum": ["GET", "POST", "UPDATE"]},
                    "endpoint": {"type": "string", "description": "Nombre del recurso (ej: Purchase, PaymentMethod)"},
                    "data": {"type": "object", "description": "Cuerpo del JSON para POST/UPDATE"},
                    "entity_id": {"type": "string", "description": "ID del recurso para GET/UPDATE específico"}
                },
                "required": ["method", "endpoint"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listarendpointsqbo",
            "description": "Lista los endpoints más comunes disponibles en la API de QuickBooks.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "infoendpointqbo",
            "description": "Obtiene información detallada sobre cómo usar un endpoint específico de la API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "endpoint_name": {"type": "string"}
                },
                "required": ["endpoint_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ejecutarcodigo",
            "description": "Ejecuta fragmentos de código Python para análisis de datos avanzados o cálculos complejos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código Python a ejecutar"}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analizarbankfeed",
            "description": "Analiza una lista de transacciones bancarias para sugerir clasificaciones contables basadas en aprendizaje previo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {"type": "string"},
                    "transactions": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "min_confidence": {"type": "number", "default": 0.7}
                },
                "required": ["account_name", "transactions"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registrarclasificacion",
            "description": "Registra el aprendizaje de una clasificación manual hecha por el usuario.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "account_id": {"type": "string"},
                    "account_name": {"type": "string"},
                    "amount": {"type": "number"},
                    "date": {"type": "string"},
                    "vendor": {"type": "string"},
                    "qb_suggestion": {"type": "string"}
                },
                "required": ["description", "account_id", "account_name", "amount", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "estadisticasclasificacion",
            "description": "Obtiene estadísticas sobre el aprendizaje del sistema de clasificación bancaria.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscarpatron",
            "description": "Busca si existe un patrón de clasificación previo para una descripción dada.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"}
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "aprenderinteraccion",
            "description": "Aprende de las preferencias del usuario basadas en sus interacciones.",
            "parameters": {
                "type": "object",
                "properties": {
                    "interaction_type": {"type": "string", "enum": ["account_use", "vendor_use", "report_use"]},
                    "details": {"type": "object"},
                    "context": {"type": "string"}
                },
                "required": ["interaction_type", "details"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtenersugerencias",
            "description": "Obtiene sugerencias de acciones basadas en el comportamiento histórico del usuario.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registrarcorreccion",
            "description": "Registra una corrección del usuario cuando el sistema comete un error.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wrong": {"type": "string"},
                    "correct": {"type": "string"},
                    "context": {"type": "string"}
                },
                "required": ["wrong", "correct", "context"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtenercontexto",
            "description": "Obtiene un resumen del contexto reciente de la conversación y tareas activas.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generarreportecustom",
            "description": "Genera reportes personalizados interpretando peticiones en lenguaje natural.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_request": {"type": "string"},
                    "filters": {"type": "object"}
                },
                "required": ["user_request"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "parsearfecha",
            "description": "Convierte expresiones temporales (ej: 'el mes pasado') en fechas específicas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "gestionar_empresas",
            "description": "Permite registrar una nueva empresa (vía link QBO o ID), listar las registradas o cambiar entre ellas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "accion": {
                        "type": "string", 
                        "enum": ["registrar", "listar", "cambiar"],
                        "description": "Acción a realizar: 'registrar' una nueva, 'listar' todas, o 'cambiar' a una existente."
                    },
                    "nombre": {
                        "type": "string",
                        "description": "Nombre de la empresa (requerido para 'registrar' y 'cambiar')."
                    },
                    "link_o_id": {
                        "type": "string",
                        "description": "URL de QuickBooks o Realm ID de la empresa (requerido para 'registrar')."
                    }
                },
                "required": ["accion"]
            }
        }
    }
]

# ==================== FUNCIONES DE LOS TOOLS ====================

def tool_buscar_cliente(nombre: str, exacto: bool = False) -> dict:
    """Tool: Busca cliente por nombre"""
    results = search_customer(nombre, exact=exacto)

    # Guardar en session state para referencia rápida
    session_state["last_search_results"]["customers"] = results

    return {
        "encontrados": len(results),
        "clientes": results[:5]  # Máximo 5 resultados
    }

def tool_buscar_vendor(nombre: str) -> dict:
    """Tool: Busca vendor por nombre"""
    results = search_vendor(nombre)
    session_state["last_search_results"]["vendors"] = results

    return {
        "encontrados": len(results),
        "vendors": results[:5]
    }

def tool_buscar_cuenta(termino: str, categoria: str = None) -> dict:
    """Tool: Busca cuenta contable"""
    results = find_account(termino, category=categoria)
    session_state["last_search_results"]["accounts"] = results

    return {
        "encontradas": len(results),
        "cuentas": [{
            "id": acc["id"],
            "numero": acc["number"],
            "nombre": acc["name"],
            "tipo": acc["type"],
            "categoria": acc["category"],
            "balance": acc["balance"],
            "similitud": round(acc.get("match_score", 1.0) * 100, 1)
        } for acc in results[:5]]
    }

def tool_buscar_item(nombre: str) -> dict:
    """Tool: Busca item/servicio"""
    results = search_item(nombre)

    return {
        "encontrados": len(results),
        "items": results[:5]
    }

def tool_crear_invoice(customer_id: str, lineas: List[dict], fecha: str = None, memo: str = None) -> dict:
    """Tool: Crea invoice"""
    return create_invoice(customer_id, lineas, fecha, memo)

def tool_crear_bill(vendor_id: str, lineas: List[dict], fecha: str = None, 
                   fecha_vencimiento: str = None, memo: str = None) -> dict:
    """Tool: Crea bill"""
    return create_bill(vendor_id, lineas, fecha, fecha_vencimiento, memo)

def tool_crear_deposito(cuenta_destino_id: str, lineas: List[dict], fecha: str = None, memo: str = None) -> dict:
    """Tool: Crea depósito"""
    return create_deposit(cuenta_destino_id, lineas, fecha, memo)

def tool_crear_pago(customer_id: str, amount: float, cuenta_id: str, fecha: str = None,
                   aplicar_a_invoices: List[dict] = None) -> dict:
    """Tool: Crea payment"""
    return create_payment(customer_id, amount, cuenta_id, fecha, aplicar_a_invoices)

def tool_generar_reporte_pl(fecha_inicio: str, fecha_fin: str, metodo: str = "Accrual") -> dict:
    """Tool: Genera P&L"""
    df = generate_pl_report(fecha_inicio, fecha_fin, metodo)

    if df.empty:
        return {"success": False, "error": "No se pudo generar el reporte"}

    # Calcular totales por categoría
    summary = df.groupby('categoria')['monto'].sum().to_dict()

    return {
        "success": True,
        "periodo": f"{fecha_inicio} a {fecha_fin}",
        "registros": len(df),
        "resumen": summary,
        "data_preview": df.head(10).to_dict(orient='records')
    }

def tool_generar_balance_sheet(fecha: str, metodo: str = "Accrual") -> dict:
    """Tool: Genera Balance Sheet"""
    df = generate_balance_sheet(fecha, metodo)

    if df.empty:
        return {"success": False, "error": "No se pudo generar el reporte"}

    summary = df.groupby('categoria')['monto'].sum().to_dict()

    return {
        "success": True,
        "fecha": fecha,
        "registros": len(df),
        "resumen": summary,
        "data_preview": df.head(10).to_dict(orient='records')
    }

def tool_guardar_reporte(nombre: str, config: dict) -> dict:
    """Tool: Guarda reporte"""
    save_report_config(nombre, config)
    return {"success": True, "mensaje": f"Reporte '{nombre}' guardado exitosamente"}

def tool_cargar_reporte(nombre: str) -> dict:
    """Tool: Carga reporte"""
    config = load_report_config(nombre)

    if config:
        return {"success": True, "config": config}
    else:
        return {"success": False, "error": f"Reporte '{nombre}' no encontrado"}

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

def tool_procesar_csv_depositos(ruta_archivo: str) -> dict:
    """Tool: Procesa CSV de depósitos"""
    return process_deposits_csv(ruta_archivo)

def tool_crear_template_csv() -> dict:
    """Tool: Crea template CSV"""
    create_deposits_template()
    return {"success": True, "archivo": FILE_DEPOSITS_TEMPLATE}

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

def tool_refrescar_chart_accounts() -> dict:
    """Tool: Refresca Chart of Accounts"""
    chart = load_chart_of_accounts(force_refresh=True)
    session_state["chart_of_accounts"] = chart

    return {
        "success": True,
        "cuentas_cargadas": len(chart),
        "mensaje": "Chart of Accounts actualizado exitosamente"
    }

def tool_gestionar_empresas(accion: str, nombre: str = None, link_o_id: str = None) -> dict:
    """
    Tool: Gestiona el registro y cambio de empresas.
    """
    global CURRENT_COMPANY, QB_REALM_ID, QB_BASE_URL, COMPANY_CONTEXT, QB_ACCESS_TOKEN, QB_REFRESH_TOKEN
    
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
        
    elif accion == "cambiar":
        if not nombre:
            return {"success": False, "message": "Falta el nombre de la empresa objetivo."}
        
        companies = list_local_companies()
        target = next((c for c in companies if c['name'].lower() == nombre.lower()), None)
        
        if not target:
            return {"success": False, "message": f"No encontré ninguna empresa registrada como '{nombre}'."}
        
        # Guardar contexto actual
        if CURRENT_COMPANY:
            save_company_context(CURRENT_COMPANY['name'], COMPANY_CONTEXT)
        
        # Cargar meta y tokens de la nueva empresa
        meta = get_company_meta(target['name'])
        CURRENT_COMPANY = target
        QB_REALM_ID = target['realm_id']
        QB_BASE_URL = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{QB_REALM_ID}"
        
        if meta.get("access_token") and meta.get("refresh_token"):
            QB_ACCESS_TOKEN = meta["access_token"]
            QB_REFRESH_TOKEN = meta["refresh_token"]
        
        save_company_selection(CURRENT_COMPANY)
        
        # Recargar contexto
        COMPANY_CONTEXT = load_company_context(target['name'])
        session_state["chart_of_accounts"] = COMPANY_CONTEXT.get("chart_of_accounts", {})
        
        return {
            "success": True, 
            "message": f"🔄 ¡Cambio exitoso! Ahora estoy operando en '{target['name']}'. He cargado sus cuentas y preferencias.",
            "empresa": target['name']
        }
    
    return {"success": False, "message": "Acción no reconocida."}

def tool_procesar_bank_feed_csv(archivo_csv: str) -> dict:
    """Tool: Procesa CSV de Bank Feed con splits"""
    return procesar_csv_bank_feed(archivo_csv)

def tool_procesar_reconciliacion_bancaria(archivo_csv: str) -> dict:
    """Tool: Procesa CSV de reconciliación bancaria"""
    return procesar_reconciliacion_bancaria(archivo_csv)


def tool_taggear_reconciliacion(
    archivo_csv: str,
    cuenta_id: str = None,
    fecha_inicio: str = None,
    fecha_fin: str = None,
    dias_fuzzy: int = 2,
    monto_fuzzy: float = 0.50,
) -> dict:
    """
    Tool: BNK-RECON tagger. Marca transactions existentes en QBO
    con el tag BNK-RECON-YYYY-MM-xxxxx en Memo/PrivateNote.
    NO crea transactions nuevas.

    Args:
        archivo_csv: Ruta al CSV del bank statement
            (columnas requeridas: date, description, amount).
        cuenta_id: ID de la cuenta bancaria en QBO. Si no se da,
            se busca automáticamente por categoría BANK.
        fecha_inicio: ISO date (YYYY-MM-DD). Default: mes actual.
        fecha_fin: ISO date (YYYY-MM-DD). Default: fin de mes.
        dias_fuzzy: Días de tolerancia para fuzzy match (default 2).
        monto_fuzzy: Diferencia máxima de monto en USD (default 0.50).
    """
    from datetime import datetime
    from dexter.core.batch import (
        BatchEngine, BatchStorage, ReconciliationTaggerSkill,
    )
    from dexter.core.qbo_client import make_qbo_client, find_bank_account_id

    if not cuenta_id:
        cuenta_id = find_bank_account_id(find_account)
        if not cuenta_id:
            return {
                "success": False,
                "error": "No se pudo identificar la cuenta bancaria. "
                         "Especifica cuenta_id o refresca el chart.",
            }

    if not fecha_inicio:
        hoy = datetime.now()
        fecha_inicio = f"{hoy.year:04d}-{hoy.month:02d}-01"
    if not fecha_fin:
        hoy = datetime.now()
        if hoy.month == 12:
            fin = f"{hoy.year + 1}-01-01"
        else:
            fin = f"{hoy.year:04d}-{hoy.month + 1:02d}-01"

    storage = BatchStorage("data/dexter.db")
    engine = BatchEngine(storage)
    qbo = make_qbo_client(qbo_query, qbo_request)

    skill = ReconciliationTaggerSkill(
        engine=engine,
        qbo_client=qbo,
        period_start=fecha_inicio,
        period_end=fecha_fin,
        account_id=cuenta_id,
        fuzzy_days=dias_fuzzy,
        fuzzy_amount=monto_fuzzy,
    )
    batch_id = skill.from_csv(archivo_csv)
    summary = skill.run(batch_id)
    return {
        "success": True,
        "batch_id": batch_id,
        "matched": summary["matched"],
        "exact": summary["exact"],
        "fuzzy": summary["fuzzy"],
        "unmatched": summary["unmatched"],
        "errors": summary["errors"],
        "report_path": summary["report_path"],
        "tag_prefix": summary["tag_prefix"],
    }


def tool_limpiar_tags_reconciliacion(batch_id: str) -> dict:
    """
    Tool: Limpia los tags BNK-RECON aplicados por un batch previo.
    Lee el reporte del batch y borra los Memo/PrivateNote.
    Útil para deshacer una reconciliación de prueba.
    """
    from dexter.core.batch import BatchEngine, BatchStorage, ReconciliationTaggerSkill
    from dexter.core.qbo_client import make_qbo_client

    storage = BatchStorage("data/dexter.db")
    engine = BatchEngine(storage)
    qbo = make_qbo_client(qbo_query, qbo_request)

    batch = storage.get_batch(batch_id)
    if not batch:
        return {"success": False, "error": f"Batch {batch_id} no existe"}

    period_start = batch.get("context", {}).get("period", "").split(" a ")[0]
    if not period_start:
        return {
            "success": False,
            "error": "No se puede reconstruir el período del batch.",
        }

    skill = ReconciliationTaggerSkill(
        engine=engine,
        qbo_client=qbo,
        period_start=period_start,
        period_end=period_start,
        account_id="",
    )
    result = skill.cleanup_tags(batch_id)
    return {
        "success": True,
        "removed": result.get("removed", 0),
        "errors": result.get("errors", []),
    }


def tool_depositar_lote_csv(
    ruta_archivo: str,
    cuenta_banco_id: str = None,
    cuenta_ingreso_id: str = None,
    confirmar: bool = True,
) -> dict:
    """
    Tool: Procesa CSV de deposits multi-cliente con el motor batch.
    Usa el Sprint 2 (DepositBatchSkill) con state machine,
    disambiguación interactiva y dry-run obligatorio.

    Args:
        ruta_archivo: Ruta al CSV (columnas: date, client_name, amount).
            Opcionales: terms, memo.
        cuenta_banco_id: ID de la cuenta bancaria. Si no se da, se auto-detecta.
        cuenta_ingreso_id: ID de la cuenta de income default. Si no se da,
            se auto-detecta buscando cuentas tipo INGRESO.
        confirmar: Si True, pide confirmación antes de ejecutar.
            Si False, solo corre el dry-run (no crea nada en QBO).
    """
    from dexter.core.batch import (
        BatchEngine, BatchStorage, Disambiguator, DepositBatchSkill,
    )
    from dexter.core.qbo_client import make_deposit_qbo_client

    if not os.path.exists(ruta_archivo):
        return {"success": False, "error": f"Archivo no encontrado: {ruta_archivo}"}

    if not cuenta_banco_id:
        cuenta_banco_id = find_bank_account_id(find_account)
        if not cuenta_banco_id:
            return {
                "success": False,
                "error": "No se pudo identificar la cuenta bancaria. "
                         "Especifica cuenta_banco_id o refresca el chart.",
            }

    if not cuenta_ingreso_id:
        results = find_account("sales", exact=False, category="INGRESO")
        if not results:
            results = find_account("income", exact=False, category="INGRESO")
        if not results:
            return {
                "success": False,
                "error": "No se pudo identificar la cuenta de income. "
                         "Especifica cuenta_ingreso_id.",
            }
        cuenta_ingreso_id = results[0]["id"]

    storage = BatchStorage("data/dexter.db")
    engine = BatchEngine(storage)
    disambiguator = Disambiguator(input_func=input, output_func=print)
    qbo = make_deposit_qbo_client(search_customer, qbo_request)

    skill = DepositBatchSkill(
        engine=engine,
        disambiguator=disambiguator,
        qbo_client=qbo,
        bank_account_id=cuenta_banco_id,
        income_account_id=cuenta_ingreso_id,
    )
    batch_id = skill.from_csv(ruta_archivo)

    # Dry-run: validar sin crear
    print(f"\n📋 BATCH {batch_id} CREADO")
    print(f"   Items: {len(storage.get_items(batch_id))}")
    print(f"   Cuenta banco: {cuenta_banco_id}")
    print(f"   Cuenta income: {cuenta_ingreso_id}")

    if not confirmar:
        return {
            "success": True,
            "batch_id": batch_id,
            "dry_run": True,
            "message": "Batch creado. Revisa con 'listar batches' antes de confirmar.",
        }

    # Confirmar y ejecutar
    if not disambiguator.confirm_batch(batch_id):
        return {
            "success": False,
            "batch_id": batch_id,
            "message": "Operación cancelada por el usuario.",
        }

    summary = skill.execute(batch_id)
    return {
        "success": summary.get("executed", 0) > 0,
        "batch_id": batch_id,
        "executed": summary.get("executed", 0),
        "failed": summary.get("failed", 0),
        "errors": summary.get("errors", []),
    }

    skill = ReconciliationTaggerSkill(
        engine=engine,
        qbo_client=qbo,
        period_start=period_start,
        period_end=period_start,
        account_id="",
    )
    result = skill.cleanup_tags(batch_id)
    return {
        "success": True,
        "removed": result.get("removed", 0),
        "errors": result.get("errors", []),
    }

# Mapeo de nombres de tools a funciones


def buscar_pdf_en_pending_bills(nombre_archivo: str = None) -> str:
    """Busca PDFs en la carpeta 'Pending bills'."""

    rutas_posibles = [
        "Pending bills",
        "./Pending bills",
        "../Pending bills",
        os.path.expanduser("~/Pending bills"),
        os.path.expanduser("~/Documents/Pending bills"),
        os.path.expanduser("~/Documentos/Pending bills")
    ]

    carpeta_pending = None

    for ruta in rutas_posibles:
        if os.path.exists(ruta) and os.path.isdir(ruta):
            carpeta_pending = ruta
            break

    if not carpeta_pending:
        raise FileNotFoundError(
            "❌ No se encontró la carpeta 'Pending bills'. "
            "Créala con: mkdir 'Pending bills'"
        )

    print(f"📂 Buscando en: {os.path.abspath(carpeta_pending)}")

    pdfs = glob.glob(os.path.join(carpeta_pending, "*.pdf"))
    pdfs.extend(glob.glob(os.path.join(carpeta_pending, "*.PDF")))

    if not pdfs:
        raise FileNotFoundError(
            f"❌ No hay archivos PDF en '{carpeta_pending}'\n"
            f"   Coloca los PDFs de bills ahí y vuelve a intentar."
        )

    if nombre_archivo:
        nombre_lower = nombre_archivo.lower()

        for pdf in pdfs:
            pdf_nombre = os.path.basename(pdf).lower()
            if nombre_lower in pdf_nombre or pdf_nombre in nombre_lower:
                print(f"✓ Archivo encontrado: {os.path.basename(pdf)}")
                return pdf

        raise FileNotFoundError(
            f"❌ No se encontró '{nombre_archivo}' en '{carpeta_pending}'\n"
            f"   Archivos disponibles:\n" +
            "\n".join(f"   - {os.path.basename(p)}" for p in pdfs)
        )

    if len(pdfs) == 1:
        print(f"✓ 1 PDF encontrado (auto-seleccionado): {os.path.basename(pdfs[0])}")
        return pdfs[0]

    raise ValueError(
        f"📋 Hay {len(pdfs)} PDFs en '{carpeta_pending}':\n" +
        "\n".join(f"   {i+1}. {os.path.basename(p)}" for i, p in enumerate(pdfs)) +
        "\n\n¿Cuál quieres procesar? (especifica el nombre o número)"
    )


def mover_a_processed(pdf_path: str) -> str:
    """Mueve PDF procesado a carpeta 'Processed bills'."""

    processed_dir = "Processed bills"
    os.makedirs(processed_dir, exist_ok=True)

    filename = os.path.basename(pdf_path)
    new_path = os.path.join(processed_dir, filename)

    if os.path.exists(new_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        new_path = os.path.join(processed_dir, filename)

    shutil.move(pdf_path, new_path)
    print(f"✓ PDF movido a: {new_path}")

    return new_path


def procesar_lote_bills(nombre_archivo: str = None) -> dict:
    """Procesa lote de bills desde PDF en carpeta 'Pending bills'."""
    try:
        pdf_path = buscar_pdf_en_pending_bills(nombre_archivo)
        bills = extraer_bills_de_pdf(pdf_path)

        if not bills:
            return {
                "status": "error",
                "message": "No se pudieron extraer invoices del PDF. Verifica el formato."
            }

        csv_path = generar_csv_preview(bills)
        total_general = sum(b.get('total_amount', 0) for b in bills)

        return {
            "status": "success",
            "pdf_procesado": os.path.basename(pdf_path),
            "pdf_path": pdf_path,
            "invoices_count": len(bills),
            "total_general": f"${total_general:,.2f}",
            "csv_preview": csv_path,
            "bills_data": bills,
            "next_steps": [
                f"✓ Revisar CSV: {csv_path}",
                "✓ Verificar matches de customers/vendors",
                "✓ Editar montos o cuentas si necesario",
                "✓ Decir 'aprobar' para crear Bills en QuickBooks"
            ]
        }

    except FileNotFoundError as e:
        return {"status": "error", "message": str(e)}
    except ValueError as e:
        return {"status": "info", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Error inesperado: {str(e)}"}


TOOL_FUNCTIONS = {
    "buscar_cliente": tool_buscar_cliente,
    "buscar_vendor": tool_buscar_vendor,
    "buscar_cuenta": tool_buscar_cuenta,
    "buscar_item": tool_buscar_item,
    "crear_invoice": tool_crear_invoice,
    "crear_bill": tool_crear_bill,
    "crear_deposito": tool_crear_deposito,
    "crear_pago": tool_crear_pago,
    "generar_reporte_pl": tool_generar_reporte_pl,
    "generar_balance_sheet": tool_generar_balance_sheet,
    "guardar_reporte": tool_guardar_reporte,
    "cargar_reporte": tool_cargar_reporte,
    "listar_reportes_guardados": tool_listar_reportes_guardados,
    "procesar_csv_depositos": tool_procesar_csv_depositos,
    "crear_template_csv": tool_crear_template_csv,
    "obtener_estadisticas_tokens": tool_obtener_estadisticas_tokens,
    "generar_informe_tokens": tool_generar_informe_tokens,
    "refrescar_chart_accounts": tool_refrescar_chart_accounts,
    "procesar_bank_feed_csv": tool_procesar_bank_feed_csv,
    "procesar_reconciliacion_bancaria": tool_procesar_reconciliacion_bancaria,
    "taggear_reconciliacion": tool_taggear_reconciliacion,
    "limpiar_tags_reconciliacion": tool_limpiar_tags_reconciliacion,
    "depositar_lote_csv": tool_depositar_lote_csv,
    "procesar_lote_bills": procesar_lote_bills,

    # ========== CAPACIDADES DE AUTONOMÍA ==========

    # Nivel 1 - Web Search
    "buscarenweb": tool_search_web,
    "buscardocsqbo": tool_search_qbo_docs,

    # Nivel 2 - API Explorer
    "crearasientodiario": tool_create_journal_entry,
    "creartransferencia": tool_create_transfer,
    "qborequestgenerico": tool_qbo_generic_request,
    "listarendpointsqbo": tool_list_qbo_endpoints,
    "infoendpointqbo": tool_get_endpoint_info,

    # Nivel 3 - Code Executor
    "ejecutarcodigo": tool_execute_python,

    # Bank Feed Intelligence
    "analizarbankfeed": tool_analyze_bank_feed_for_classification,
    "registrarclasificacion": tool_record_bank_feed_classification,
    "estadisticasclasificacion": tool_get_classification_history_stats,
    "buscarpatron": tool_find_pattern_for_transaction,

    # User Behavior Learning
    "aprenderinteraccion": tool_learn_from_interaction,
    "obtenersugerencias": tool_get_user_suggestions,
    "registrarcorreccion": tool_record_user_correction,
    "obtenercontexto": tool_get_conversation_context,

    # Dynamic Report Generator
    "generarreportecustom": tool_generate_custom_report,
    "parsearfecha": tool_parse_date_expression,
    "gestionar_empresas": tool_gestionar_empresas,
}


def process_quick_command(user_input: str) -> Optional[str]:
    """Procesa comandos rápidos del usuario sin necesidad de LLM"""
    input_lower = user_input.lower().strip()

    # Refrescar chart
    if "refrescar" in input_lower and ("chart" in input_lower or "cuentas" in input_lower):
        result = tool_refrescar_chart_accounts()
        return f"{result['mensaje']} ({result['cuentas_cargadas']} cuentas actualizadas)"

    # BNK-RECON tagger (guía rápida)
    if "recon" in input_lower and ("tag" in input_lower or "marcar" in input_lower or "bnk" in input_lower):
        return (
            "🏷️ **BNK-RECON TAGGER**\n"
            "Esta opción solo AGREGA tags a transactions existentes de QBO (no crea nuevas).\n\n"
            "Pasos:\n"
            "1. Descarga el CSV de tu banco (formato: date, description, amount).\n"
            "2. Colócalo en `/Bank Reconciliation/` o en cualquier ruta.\n"
            "3. Dime: 'reconcilia el banco con [ruta al CSV]'.\n"
            "4. Yo agregaré tags `BNK-RECON-YYYY-MM-xxxxx` a las transactions que matcheen.\n"
            "5. Después entras a QBO UI a reconciliar manualmente con esos tags visibles.\n\n"
            "Para limpiar tags de un batch: 'limpia los tags del batch [batch_id]'."
        )

    # Batch deposits (guía rápida)
    if any(kw in input_lower for kw in [
        "lote csv", "lote deposit", "depositar batch", "batch deposit",
        "depositos lote", "depositos csv",
    ]):
        return (
            "📦 **DEPOSITOS BATCH (motor con state machine)**\n"
            "Procesa CSVs de líneas de deposit multi-cliente con:\n"
            "- State machine: PENDING → VALIDATED → DRY-RUN → CONFIRMED → EXECUTED\n"
            "- Disambiguación interactiva: pregunta si un cliente no existe\n"
            "- Dry-run obligatorio antes de crear en QBO\n"
            "- Audit log completo en SQLite\n\n"
            "Pasos:\n"
            "1. Prepara un CSV con columnas: date, client_name, amount.\n"
            "   Opcionales: terms, memo.\n"
            "2. Dime: 'procesa el lote [ruta al CSV]'.\n"
            "3. Yo busco los clientes en QBO. Si falta alguno, te pregunto.\n"
            "4. Te muestro el dry-run. Tú confirmas.\n"
            "5. Creo el deposit en QBO y guardo el batch_id.\n\n"
            "Para dry-run sin crear: 'procesa el lote [ruta] sin confirmar'."
        )

    # Template CSV
    if "template" in input_lower or "plantilla" in input_lower:
        result = tool_crear_template_csv()
        return f"Template CSV creado: {result['archivo']}. Úsalo como base para depósitos batch."

    # Listar reportes guardados
    if "listar" in input_lower and "reporte" in input_lower:
        result = tool_listar_reportes_guardados()
        if result["total"] == 0:
            return "No tienes reportes guardados todavía. Guarda configuraciones de reportes frecuentes para acceso rápido."

        response = f"Reportes Guardados ({result['total']}):\n"
        for rep in result["reportes"]:
            response += f"  • {rep['nombre']} - Creado: {rep['creado'][:10]}, Último uso: {rep['ultimo_uso'][:10]}\n"

        return response

    # Cambiar idioma
    if "cambiar" in input_lower and ("idioma" in input_lower or "language" in input_lower):
        new_lang = "en" if session_state["language"] == "es" else "es"
        session_state["language"] = new_lang
        
        # Guardar en contexto de empresa para persistencia
        if 'COMPANY_CONTEXT' in globals() and 'CURRENT_COMPANY' in globals() and CURRENT_COMPANY:
            COMPANY_CONTEXT["language"] = new_lang
            save_company_context(CURRENT_COMPANY['name'], COMPANY_CONTEXT)
            
        lang_name = "Inglés" if new_lang == "en" else "Español"
        status_msg = f"✅ Idioma cambiado a: **{lang_name}** / Language changed to: **{lang_name}**"
        return status_msg

    # Ayuda Contextual
    if "ayuda" in input_lower or "manual" in input_lower:
        if "ocr" in input_lower or "factura" in input_lower:
            return "📖 **AYUDA OCR:**\n1. Coloca PDFs/imágenes en `/Pending bills/`.\n2. Dime: 'Procesa las facturas'.\n3. Yo extraeré los datos y te preguntaré si tengo dudas.\n4. Los archivos irán a `/Processed bills/`."
        
        if "banco" in input_lower or "reconcilia" in input_lower:
            return (
                "📖 **AYUDA BANCOS:**\n"
                "Tengo 2 modos de reconciliación:\n"
                "1. **Agresivo** (crea transactions nuevas):\n"
                "   'reconcilia el banco con [archivo CSV]'\n"
                "2. **Seguro BNK-RECON** (solo taggea, no crea):\n"
                "   'recon tag [archivo CSV]'\n\n"
                "Usa el modo seguro si solo quieres marcadores visibles en QBO UI."
            )
        
        if "reporte" in input_lower or "analiza" in input_lower:
            return "📖 **AYUDA REPORTES:**\n- Puedes pedir P&L, Balance Sheet o análisis comparativos.\n- Ejemplo: 'Haz un P&L de este mes vs el anterior'.\n- También puedo generar Excels complejos con gráficos."
            
        return "📖 **DEXTER HELP:**\nPuedes pedir ayuda específica:\n- `ayuda ocr`\n- `ayuda bancos`\n- `ayuda reportes`\n- `ayuda recon`"

    return None


# ==================== OPTIMIZACIONES ====================

def get_relevant_tools(user_message: str) -> list:
    """Retorna lista de definiciones de tools (schemas) relevantes."""
    msg = user_message.lower()
    relevant_names = set()

    # Mapeo de keywords a nombres de tools
    if any(kw in msg for kw in ["clasificar", "bank", "banco", "feed"]):
        relevant_names.update(["analizarbankfeed", "registrarclasificacion", "buscarpatron", "procesar_bank_feed_csv"])

    if any(kw in msg for kw in ["recon", "reconcili", "bnk-recon", "tag", "marcar"]):
        relevant_names.update(["taggear_reconciliacion", "limpiar_tags_reconciliacion", "procesar_reconciliacion_bancaria"])

    if any(kw in msg for kw in ["lote", "batch", "depositar csv", "csv depositos", "multiples deposit"]):
        relevant_names.update(["depositar_lote_csv", "crear_template_csv", "procesar_csv_depositos"])

    if any(kw in msg for kw in ["reporte", "p&l", "balance", "estado"]):
        relevant_names.update(["generar_reporte_pl", "generar_balance_sheet", "generarreportecustom", "parsearfecha"])
    
    if any(kw in msg for kw in ["busca", "search", "cliente", "vendor", "cuenta"]):
        relevant_names.update(["buscar_cliente", "buscar_vendor", "buscar_cuenta", "buscar_item"])
    
    if any(kw in msg for kw in ["bill", "factura", "ocr", "pdf"]):
        relevant_names.update(["procesar_lote_bills", "crear_bill"])
    
    if any(kw in msg for kw in ["invoice", "pago", "cobro"]):
        relevant_names.update(["crear_invoice", "crear_pago"])

    if any(kw in msg for kw in ["asiento", "journal", "transferencia", "mover"]):
        relevant_names.update(["crearasientodiario", "creartransferencia"])

    if any(kw in msg for kw in ["web", "internet", "google", "api", "endpoint"]):
        relevant_names.update(["buscarenweb", "buscardocsqbo", "listarendpointsqbo", "infoendpointqbo"])

    if any(kw in msg for kw in ["codigo", "python", "calcula", "analiza"]):
        relevant_names.update(["ejecutarcodigo"])

    # Always include a few basics if no match
    if not relevant_names:
        relevant_names.update(["buscar_cliente", "buscar_cuenta", "generar_reporte_pl"])

    # Multi-company
    if any(k in msg for k in ["empresa", "compañía", "cliente", "registrar", "cambiar", "listar"]):
        relevant_names.add("gestionar_empresas")

    # Refrescar siempre disponible si se pide
    if "refrescar" in msg:
        relevant_names.add("refrescar_chart_accounts")

    # Filtrar la lista global TOOLS
    return [t for t in TOOLS if t["function"]["name"] in relevant_names]

def build_conversation_context(history: list, max_turns: int = 5) -> tuple:
    recent = history[-(max_turns * 2):] if len(history) > max_turns * 2 else history
    if history:
        text = " ".join([m.get("content", "")[:80] for m in history[-4:]])
        hints = []
        if "reporte" in text: hints.append("reportes")
        if "clasifica" in text: hints.append("clasificación")
        context = f"Contexto: {', '.join(hints)}" if hints else "Conversación"
    else:
        context = "Inicio"
    return recent, context

def necesita_chart(msg: str) -> bool:
    kw = ["clasifica", "cuenta", "bill", "journal", "asiento"]
    return any(k in msg.lower() for k in kw)

# ==================== LOOP PRINCIPAL ====================

def main_loop():
    """Loop principal conversacional"""
    print("="*70)
    print("           🤖 DEXTER - QuickBooks AI Assistant")
    print("              Operando para: Alfredo")
    print("="*70)
    print()
    print("Sistema listo 🚀")
    print()
    print("🤖 Hola Alfredo, ¿quieres que te guíe en algún proceso hoy (como OCR o Bancos)\no prefieres ir directo a tus consultas?")
    print()
    print("Comandos rápidos:")
    print("  • 'ayuda ocr' - Guía paso a paso para facturas")
    print("  • '¿cuánto he gastado?' - Estadísticas de tokens")
    print("  • 'informe de tokens' - Genera Excel con estadísticas")
    print("  • 'template csv' - Crea plantilla para depósitos")
    print("  • 'salir' - Termina la sesión")
    print()

    while True:
        try:
            user_input = input("👤 Tú: ").strip()

            if not user_input:
                continue

            # Comando de salida
            if user_input.lower() in ["salir", "exit", "quit", "chao", "adiós"]:
                break

            # Procesar comandos rápidos
            quick_response = process_quick_command(user_input)
            if quick_response:
                print(f"\n{quick_response}\n")
                continue

            # Llamar al LLM con tools
            print("\n🤖 ", end="", flush=True)

            try:
                response = call_llm(user_input, tools=TOOLS)
                print(f"{response}\n")
            except KeyboardInterrupt:
                print("\n[Interrupciódetectada]\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                import traceback
                traceback.print_exc()

        except KeyboardInterrupt:
            print("\n\n[Interrupción detectada]\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()

    # Cerrar sesión
    print("\n" + "="*70)
    print("Cerrando sesión...")

    duration = (datetime.now() - session_state["start_time"]).total_seconds() / 60
    total_tokens = session_state["input_tokens"] + session_state["output_tokens"]
    cost = calculate_session_cost()

    print("\n📊 RESUMEN DE LA SESIÓN")
    print("="*70)
    print(f"  Duración: {duration:.0f} minutos")
    print(f"  Tokens: {total_tokens:,}")
    print(f"    • Input: {session_state['input_tokens']:,}")
    print(f"    • Output: {session_state['output_tokens']:,}")
    print(f"  Costo: ${cost:.4f}")
    print(f"  Operaciones: {sum(session_state['operations'].values())}")

    for op, count in session_state["operations"].items():
        if count > 0:
            print(f"    • {op}: {count}")

    save_session_to_csv()
    print("\n✅ Sesión guardada exitosamente")
    print("="*70)

# ==================== ENTRY POINT ====================


if __name__ == "__main__":

    # ASCII Art Banner
    # Banner
    print("-" * 70)
    print(" " * 20 + "DEXTER - AI Assistant v1.0")
    print("-" * 70)

    # ---------------------------------------------------------------
    # SELECTOR DE EMPRESA (MULTI-COMPANY)
    # ---------------------------------------------------------------


    # Intentar cargar empresa previamente seleccionada
    CURRENT_COMPANY = load_current_company()

    if CURRENT_COMPANY:
        print(f"📁 Empresa activa: {CURRENT_COMPANY['name']}")
        print(f"   Realm ID: {CURRENT_COMPANY['realm_id']}")
        print()
        cambiar = input("¿Deseas cambiar de empresa? (s/N): ").strip().lower()
        if cambiar in ["s", "si", "sí", "y", "yes"]:
            CURRENT_COMPANY = None

    # Si no hay empresa seleccionada, mostrar selector
    if not CURRENT_COMPANY:
        CURRENT_COMPANY = select_company_interactive(QB_REALM_ID)
        if not CURRENT_COMPANY:
            print("❌ No se seleccionó ninguna empresa. Saliendo...")
            exit(0)

    # Guardar selección
    save_company_selection(CURRENT_COMPANY)

    QB_REALM_ID = CURRENT_COMPANY["realm_id"]
    QB_BASE_URL = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{QB_REALM_ID}"

    # Cargar tokens específicos de la empresa si existen
    meta = get_company_meta(CURRENT_COMPANY['name'])
    if meta.get("access_token") and meta.get("refresh_token"):
        QB_ACCESS_TOKEN = meta["access_token"]
        QB_REFRESH_TOKEN = meta["refresh_token"]
        print(f"🔑 Tokens cargados específicamente para {CURRENT_COMPANY['name']}")

    # Cargar contexto de la empresa
    print(f"📊 Cargando contexto de {CURRENT_COMPANY['name']}...")
    COMPANY_CONTEXT = load_company_context(CURRENT_COMPANY['name'])

    # Cargar Chart of Accounts específico de esta empresa
    if COMPANY_CONTEXT.get("chart_of_accounts"):
        session_state["chart_of_accounts"] = COMPANY_CONTEXT["chart_of_accounts"]
        print(f"✅ Chart cargado desde caché ({len(COMPANY_CONTEXT['chart_of_accounts'])} cuentas)")
    else:
        session_state["chart_of_accounts"] = load_chart_of_accounts()
        COMPANY_CONTEXT["chart_of_accounts"] = session_state["chart_of_accounts"]
        save_company_context(CURRENT_COMPANY['name'], COMPANY_CONTEXT)

    # Cargar otros contextos
    if COMPANY_CONTEXT.get("saved_reports"):
        session_state["saved_reports"] = COMPANY_CONTEXT["saved_reports"]

    # Cargar idioma preferido
    if COMPANY_CONTEXT.get("language"):
        session_state["language"] = COMPANY_CONTEXT["language"]

    print("✅ Contexto cargado:")
    print(f"   - {len(COMPANY_CONTEXT['chart_of_accounts'])} cuentas")
    print(f"   - {len(COMPANY_CONTEXT.get('saved_reports', {}))} reportes")
    print(f"   - {len(COMPANY_CONTEXT.get('bank_feed_rules', {}))} reglas")
    print(f"   - Idioma: {session_state['language'].upper()}")
    print()

    # Verificar credenciales mínimas
    missing_creds = []
    if not QB_ACCESS_TOKEN:
        missing_creds.append("QB_ACCESS_TOKEN")
    if not QB_REALM_ID:
        missing_creds.append("QB_REALM_ID")
    if not OPENROUTER_API_KEY:
        missing_creds.append("OPENROUTER_API_KEY")

    if missing_creds:
        print("❌ ERROR: Faltan credenciales en el archivo .env:")
        for cred in missing_creds:
            print(f"   • {cred}")
        print("\nCrea un archivo .env con las credenciales necesarias.")
        exit(1)

    # Verificar conexión a QuickBooks
    print("\n🔄 Verificando conexión a QuickBooks...")
    test_query = qbo_query("SELECT COUNT(*) FROM Account")

    if "error" in test_query:
        print(f"⚠️ Error conectando a QuickBooks: {test_query['error']}")
        print("\n🔄 Intentando refrescar token...")
        if not refresh_qb_token():
            print("\n❌ No se pudo refrescar el token. Verifica tus credenciales.")
            exit(1)

    print("✅ Conexión establecida\n")

    # Asegurar Chart of Accounts cargado en session_state
    if not session_state.get("chart_of_accounts"):
        session_state["chart_of_accounts"] = load_chart_of_accounts()
    
    # Iniciar loop principal
    main_loop()

