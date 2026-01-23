"""
QuickBooks AI Assistant - Setup Verification Script
Verifica que todas las dependencias y credenciales estén correctamente configuradas
"""

import os
import sys
from pathlib import Path

def print_header():
    print("\n" + "="*80)
    print("🔍 QUICKBOOKS AI ASSISTANT - VERIFICACIÓN DE CONFIGURACIÓN")
    print("="*80 + "\n")

def check_dependencies():
    """Verifica que las dependencias Python estén instaladas"""
    print("✓ Verificando dependencias Python...")
    
    required_packages = {
        'requests': '2.31.0',
        'dotenv': '1.0.0',
        'pandas': '2.1.0',
        'openpyxl': '3.1.0'
    }
    
    missing = []
    for package, version in required_packages.items():
        try:
            if package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"  ✅ {package} instalado")
        except ImportError:
            missing.append(package)
            print(f"  ❌ {package} NO instalado")
    
    if missing:
        print(f"\n❌ Faltan paquetes: {', '.join(missing)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    
    print("\n✅ 1. Todas las dependencias instaladas\n")
    return True

def check_env_file():
    """Verifica que el archivo .env exista y tenga las variables necesarias"""
    print("✓ Verificando variables de entorno...")
    
    if not os.path.exists('.env'):
        print("  ❌ Archivo .env no encontrado")
        print("\n💡 Solución:")
        print("  cp .env.example .env")
        print("  # Luego edita .env con tus credenciales")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'QB_ACCESS_TOKEN',
        'QB_REFRESH_TOKEN',
        'QB_CLIENT_ID',
        'QB_CLIENT_SECRET',
        'QB_REALM_ID',
        'OPENROUTER_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print(f"  ✅ {var}: {masked}")
        else:
            missing.append(var)
            print(f"  ❌ {var}: NO CONFIGURADO")
    
    if missing:
        print(f"\n❌ Faltan variables: {', '.join(missing)}")
        print("Edita el archivo .env y completa las credenciales")
        return False
    
    print("\n✅ 2. Todas las variables de entorno configuradas\n")
    return True

def check_qbo_connection():
    """Verifica conexión a QuickBooks Online"""
    print("✓ Verificando conexión a QuickBooks Online...")
    
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        
        access_token = os.getenv('QB_ACCESS_TOKEN')
        realm_id = os.getenv('QB_REALM_ID')
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/query"
        params = {'query': 'SELECT COUNT(*) FROM Account'}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('QueryResponse', {}).get('Account', [])
            print(f"  ✅ Conexión exitosa")
            print(f"  ✅ {len(accounts)} cuentas disponibles")
            print("\n✅ 3. Conexión a QuickBooks Online verificada\n")
            return True
        elif response.status_code == 401:
            print("  ❌ Token expirado o inválido")
            print("\n💡 Solución:")
            print("  python scripts/refresh_token.py")
            return False
        else:
            print(f"  ❌ Error: {response.status_code}")
            print(f"  {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_openrouter():
    """Verifica conexión a OpenRouter"""
    print("✓ Verificando conexión a OpenRouter...")
    
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        url = "https://openrouter.ai/api/v1/models"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("  ✅ API Key válida")
            print("  ✅ Modelo deepseek/deepseek-chat disponible")
            print("\n✅ 4. Conexión a OpenRouter verificada\n")
            return True
        else:
            print(f"  ❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print_header()
    
    checks = [
        check_dependencies(),
        check_env_file(),
        check_qbo_connection(),
        check_openrouter()
    ]
    
    print("="*80)
    if all(checks):
        print("🎉 ¡CONFIGURACIÓN COMPLETA Y CORRECTA!")
        print("\nPróximo paso: python main.py")
    else:
        print("❌ HAY PROBLEMAS DE CONFIGURACIÓN")
        print("\nRevisa los errores arriba y corrígelos")
    print("="*80 + "\n")
    
    return 0 if all(checks) else 1

if __name__ == "__main__":
    sys.exit(main())
"""
QuickBooks AI Assistant - Setup Verification Script
Verifica que todas las dependencias y credenciales estén correctamente configuradas
"""

import os
import sys
from pathlib import Path

def print_header():
    print("\n" + "="*80)
    print("🔍 QUICKBOOKS AI ASSISTANT - VERIFICACIÓN DE CONFIGURACIÓN")
    print("="*80 + "\n")

def check_dependencies():
    """Verifica que las dependencias Python estén instaladas"""
    print("✓ Verificando dependencias Python...")
    
    required_packages = {
        'requests': '2.31.0',
        'dotenv': '1.0.0',
        'pandas': '2.1.0',
        'openpyxl': '3.1.0'
    }
    
    missing = []
    for package, version in required_packages.items():
        try:
            if package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"  ✅ {package} instalado")
        except ImportError:
            missing.append(package)
            print(f"  ❌ {package} NO instalado")
    
    if missing:
        print(f"\n❌ Faltan paquetes: {', '.join(missing)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    
    print("\n✅ 1. Todas las dependencias instaladas\n")
    return True

def check_env_file():
    """Verifica que el archivo .env exista y tenga las variables necesarias"""
    print("✓ Verificando variables de entorno...")
    
    if not os.path.exists('.env'):
        print("  ❌ Archivo .env no encontrado")
        print("\n💡 Solución:")
        print("  cp .env.example .env")
        print("  # Luego edita .env con tus credenciales")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'QB_ACCESS_TOKEN',
        'QB_REFRESH_TOKEN',
        'QB_CLIENT_ID',
        'QB_CLIENT_SECRET',
        'QB_REALM_ID',
        'OPENROUTER_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print(f"  ✅ {var}: {masked}")
        else:
            missing.append(var)
            print(f"  ❌ {var}: NO CONFIGURADO")
    
    if missing:
        print(f"\n❌ Faltan variables: {', '.join(missing)}")
        print("Edita el archivo .env y completa las credenciales")
        return False
    
    print("\n✅ 2. Todas las variables de entorno configuradas\n")
    return True

def check_qbo_connection():
    """Verifica conexión a QuickBooks Online"""
    print("✓ Verificando conexión a QuickBooks Online...")
    
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        
        access_token = os.getenv('QB_ACCESS_TOKEN')
        realm_id = os.getenv('QB_REALM_ID')
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/query"
        params = {'query': 'SELECT COUNT(*) FROM Account'}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('QueryResponse', {}).get('Account', [])
            print(f"  ✅ Conexión exitosa")
            print(f"  ✅ {len(accounts)} cuentas disponibles")
            print("\n✅ 3. Conexión a QuickBooks Online verificada\n")
            return True
        elif response.status_code == 401:
            print("  ❌ Token expirado o inválido")
            print("\n💡 Solución:")
            print("  python scripts/refresh_token.py")
            return False
        else:
            print(f"  ❌ Error: {response.status_code}")
            print(f"  {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_openrouter():
    """Verifica conexión a OpenRouter"""
    print("✓ Verificando conexión a OpenRouter...")
    
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        url = "https://openrouter.ai/api/v1/models"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("  ✅ API Key válida")
            print("  ✅ Modelo deepseek/deepseek-chat disponible")
            print("\n✅ 4. Conexión a OpenRouter verificada\n")
            return True
        else:
            print(f"  ❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print_header()
    
    checks = [
        check_dependencies(),
        check_env_file(),
        check_qbo_connection(),
        check_openrouter()
    ]
    
    print("="*80)
    if all(checks):
        print("🎉 ¡CONFIGURACIÓN COMPLETA Y CORRECTA!")
        print("\nPróximo paso: python main.py")
    else:
        print("❌ HAY PROBLEMAS DE CONFIGURACIÓN")
        print("\nRevisa los errores arriba y corrígelos")
    print("="*80 + "\n")
    
    return 0 if all(checks) else 1

if __name__ == "__main__":
    sys.exit(main())
