import os
import json
import re
from typing import Optional, Dict, List

COMPANIES_DIR = "companies"
COMPANY_FILE = ".current_company"

# ----------------- Utilidades de ID y URL -----------------

def extract_realm_id(input_str: str) -> Optional[str]:
    """
    Extrae el Realm ID de un string que puede ser:
    - Un link de QBO: https://...companyId=934145...
    - Un Realm ID puro: 934145...
    """
    if not input_str:
        return None
    
    # Caso 1: Es una URL con companyId=
    match = re.search(r"companyId=(\d+)", input_str)
    if match:
        return match.group(1)
    
    # Caso 2: Es un número puro (o string numérico)
    id_match = re.search(r"(\d{10,})", input_str) # Realm IDs suelen tener 10+ dígitos
    if id_match:
        return id_match.group(1)
        
    return None

# ----------------- Operaciones de Tokens por Empresa -----------------

def get_company_meta(company_name: str) -> Dict:
    """Obtiene los metadatos (ID y Tokens) de una empresa."""
    company_dir = os.path.join(COMPANIES_DIR, company_name)
    meta_file = os.path.join(company_dir, "meta.json")
    
    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_company_meta(company_name: str, realm_id: str, access_token: str = None, refresh_token: str = None):
    """Guarda metadatos de la empresa incluyendo tokens si se proveen."""
    company_dir = os.path.join(COMPANIES_DIR, company_name)
    os.makedirs(company_dir, exist_ok=True)
    meta_file = os.path.join(company_dir, "meta.json")
    
    # Mantener lo que ya existe si los nuevos son None
    meta = get_company_meta(company_name)
    meta["realm_id"] = realm_id
    if access_token: meta["access_token"] = access_token
    if refresh_token: meta["refresh_token"] = refresh_token
    
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

# ----------------- Utilidades básicas -----------------

def list_local_companies() -> List[Dict]:
    """Lista todas las empresas registradas localmente."""
    companies = []
    if not os.path.exists(COMPANIES_DIR):
        return companies

    for item in os.listdir(COMPANIES_DIR):
        company_path = os.path.join(COMPANIES_DIR, item)
        if os.path.isdir(company_path):
            meta = get_company_meta(item)
            companies.append({
                "name": item, 
                "realm_id": meta.get("realm_id"),
                "has_tokens": "refresh_token" in meta
            })
    companies.sort(key=lambda c: c["name"].lower())
    return companies

def load_current_company() -> Optional[Dict]:
    """Carga la última empresa seleccionada."""
    if not os.path.exists(COMPANY_FILE):
        return None
    try:
        with open(COMPANY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "name" in data:
            return data
    except:
        pass
    return None

def save_company_selection(company: Dict):
    """Guarda la empresa seleccionada en .current_company."""
    if not company: return
    with open(COMPANY_FILE, "w", encoding="utf-8") as f:
        json.dump(company, f, indent=2)

def load_company_context(company_name: str) -> Dict:
    """Carga el contexto (chart, reportes, reglas) de una empresa."""
    company_dir = os.path.join(COMPANIES_DIR, company_name)
    os.makedirs(company_dir, exist_ok=True)
    context_file = os.path.join(company_dir, "context.json")

    base_ctx = {
        "chart_of_accounts": {},
        "saved_reports": {},
        "bank_feed_rules": {},
        "custom_rules": {},
    }

    if not os.path.exists(context_file):
        return base_ctx

    try:
        with open(context_file, "r", encoding="utf-8") as f:
            ctx = json.load(f)
        for key in base_ctx:
            ctx.setdefault(key, base_ctx[key])
        return ctx
    except:
        return base_ctx

def save_company_context(company_name: str, context: Dict):
    """Guarda el contexto de una empresa."""
    company_dir = os.path.join(COMPANIES_DIR, company_name)
    os.makedirs(company_dir, exist_ok=True)
    context_file = os.path.join(company_dir, "context.json")
    with open(context_file, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2)

# ----------------- Selector interactivo -----------------

def select_company_interactive(default_realm_id: str = None) -> Dict:
    """Menú interactivo para seleccionar o crear empresas."""
    existing = list_local_companies()
    last = load_current_company()

    print("\n" + "="*50)
    print(" 🏢 GESTIÓN DE EMPRESAS")
    print("="*50)

    if existing:
        print("\nEmpresas registradas:")
        for idx, c in enumerate(existing, 1):
            status = "✅" if c["has_tokens"] else "🔑"
            mark = " ◀" if last and c["name"] == last["name"] else ""
            print(f"  {idx}. {status} {c['name']} (ID: {c['realm_id']}){mark}")
        print(f"  0. ➕ Registrar nueva empresa")
    else:
        print("\nNo hay empresas registradas.")
        print("0. ➕ Registrar primera empresa")

    while True:
        try:
            op = input("\nSeleccione (Enter para última): ").strip()
            if not op and last:
                return last
            
            n = int(op)
            if n == 0:
                print("\nREGISTRO DE NUEVA EMPRESA")
                name = input("Nombre (ej: Constructora ABC): ").strip()
                if not name: continue
                
                realm_input = input("Realm ID o Link de QBO: ").strip()
                realm_id = extract_realm_id(realm_input)
                
                if not realm_id:
                    print("❌ ID no válido. Intente de nuevo.")
                    continue
                
                save_company_meta(name, realm_id)
                return {"name": name, "realm_id": realm_id}
            
            if 1 <= n <= len(existing):
                target = existing[n-1]
                return {"name": target["name"], "realm_id": target["realm_id"]}
        except:
            print("⚠️ Opción inválida.")

def validate_company_connection(realm_id: str, qbo_query_func) -> bool:
    """Valida conexión haciendo un query simple."""
    try:
        result = qbo_query_func("SELECT CompanyName FROM CompanyInfo")
        return "error" not in result
    except:
        return False
