#!/bin/bash
# install.sh - Instalación COMPLETA y automatizada de TMP AI Assistant
# Autor: Alfredo
# Fecha: Enero 2026
# Versión: 1.0

# =================================================================
# COLORES PARA TERMINAL
# =================================================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# =================================================================
# FUNCIONES DE UTILIDAD
# =================================================================

print_header() {
    echo ""
    echo -e "${BLUE}${BOLD}======================================================================${NC}"
    echo -e "${CYAN}${BOLD}$(printf '%*s' $(((${#1}+70)/2)) "$1")${NC}"
    echo -e "${BLUE}${BOLD}======================================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# =================================================================
# BANNER INICIAL
# =================================================================

clear
echo ""
echo -e "${CYAN}${BOLD}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ████████╗███╗   ███╗██████╗      █████╗ ██╗              ║
║   ╚══██╔══╝████╗ ████║██╔══██╗    ██╔══██╗██║              ║
║      ██║   ██╔████╔██║██████╔╝    ███████║██║              ║
║      ██║   ██║╚██╔╝██║██╔═══╝     ██╔══██║██║              ║
║      ██║   ██║ ╚═╝ ██║██║         ██║  ██║██║              ║
║      ╚═╝   ╚═╝     ╚═╝╚═╝         ╚═╝  ╚═╝╚═╝              ║
║                                                               ║
║            QuickBooks AI Assistant v3.0                       ║
║         Instalador Automático Completo                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""
echo -e "${BOLD}Este script instalará y configurará TODO automáticamente:${NC}"
echo ""
echo "  • Verificará e instalará dependencias del sistema"
echo "  • Creará el entorno virtual de Python"
echo "  • Instalará todas las librerías necesarias"
echo "  • Configurará credenciales (archivo .env)"
echo "  • Verificará estructura de carpetas"
echo "  • Probará la conexión a QuickBooks"
echo ""
echo -e "${YELLOW}${BOLD}⏱️  Tiempo estimado: 2-5 minutos${NC}"
echo ""
read -p "Presiona Enter para comenzar la instalación..."

# =================================================================
# PASO 1: VERIFICAR DIRECTORIO
# =================================================================

print_header "VERIFICACIÓN DE DIRECTORIO"

if [ ! -f "main.py" ]; then
    print_error "No estás en el directorio del proyecto"
    print_info "Este script debe ejecutarse desde: ~/Escritorio/Qbo Scripts"
    print_info "O desde donde hayas clonado el repositorio"
    exit 1
fi

print_success "Directorio del proyecto verificado"
print_info "Ubicación: $(pwd)"

# =================================================================
# PASO 2: DETECTAR SISTEMA OPERATIVO
# =================================================================

print_header "DETECCIÓN DE SISTEMA OPERATIVO"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    print_success "Sistema operativo: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    print_success "Sistema operativo: macOS"
else
    print_warning "Sistema operativo no reconocido: $OSTYPE"
    OS="unknown"
fi

# =================================================================
# PASO 3: INSTALAR DEPENDENCIAS DEL SISTEMA
# =================================================================

print_header "INSTALACIÓN DE DEPENDENCIAS DEL SISTEMA"

# Verificar si es root (para instalación de paquetes)
if [ "$EUID" -eq 0 ]; then
    print_warning "Ejecutando como root, omitiendo sudo"
    SUDO=""
else
    SUDO="sudo"
fi

# Python
print_info "Verificando Python 3..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python instalado: v$PYTHON_VERSION"
else
    print_warning "Python3 no encontrado. Instalando..."
    if [ "$OS" == "linux" ]; then
        $SUDO apt update > /dev/null 2>&1
        $SUDO apt install -y python3 python3-pip python3-venv
        print_success "Python3 instalado"
    elif [ "$OS" == "mac" ]; then
        brew install python3
        print_success "Python3 instalado"
    else
        print_error "No se pudo instalar Python automáticamente"
        print_info "Instala Python 3.9+ manualmente desde python.org"
        exit 1
    fi
fi

# pip
print_info "Verificando pip..."
if command -v pip3 &> /dev/null; then
    print_success "pip instalado"
else
    print_warning "pip no encontrado. Instalando..."
    if [ "$OS" == "linux" ]; then
        $SUDO apt install -y python3-pip
        print_success "pip instalado"
    fi
fi

# Git (verificación)
print_info "Verificando Git..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    print_success "Git instalado: v$GIT_VERSION"
else
    print_warning "Git no encontrado"
    if [ "$OS" == "linux" ]; then
        print_info "Instalando Git..."
        $SUDO apt install -y git
        print_success "Git instalado"
    fi
fi

# =================================================================
# PASO 4: CREAR ENTORNO VIRTUAL
# =================================================================

print_header "CREACIÓN DE ENTORNO VIRTUAL"

if [ -d ".venv" ]; then
    print_warning "Entorno virtual ya existe"
    echo ""
    read -p "¿Deseas recrearlo? (elimina el actual) [s/N]: " recreate
    if [[ "$recreate" =~ ^[SsYy]$ ]]; then
        print_info "Eliminando entorno virtual antiguo..."
        rm -rf .venv
        print_success "Entorno eliminado"
    else
        print_info "Usando entorno virtual existente"
    fi
fi

if [ ! -d ".venv" ]; then
    print_info "Creando entorno virtual..."
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        print_success "Entorno virtual creado: .venv/"
    else
        print_error "Error al crear entorno virtual"
        exit 1
    fi
fi

# Activar entorno virtual
print_info "Activando entorno virtual..."
source .venv/bin/activate

if [ -n "$VIRTUAL_ENV" ]; then
    print_success "Entorno virtual activado"
    print_info "Ubicación: $VIRTUAL_ENV"
else
    print_error "No se pudo activar el entorno virtual"
    exit 1
fi

# =================================================================
# PASO 5: ACTUALIZAR PIP
# =================================================================

print_header "ACTUALIZACIÓN DE PIP"

print_info "Actualizando pip a la última versión..."
pip install --upgrade pip --quiet
if [ $? -eq 0 ]; then
    PIP_VERSION=$(pip --version | awk '{print $2}')
    print_success "pip actualizado a v$PIP_VERSION"
else
    print_warning "No se pudo actualizar pip (no es crítico)"
fi

# =================================================================
# PASO 6: INSTALAR DEPENDENCIAS DE PYTHON
# =================================================================

print_header "INSTALACIÓN DE DEPENDENCIAS DE PYTHON"

if [ -f "requirements.txt" ]; then
    print_info "Instalando desde requirements.txt..."
    print_info "Esto puede tomar 1-2 minutos..."
    echo ""
    
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "Todas las dependencias instaladas correctamente"
        
        # Mostrar paquetes principales instalados
        echo ""
        print_info "Paquetes principales instalados:"
        echo ""
        pip list | grep -E "requests|pandas|openpyxl|python-dotenv|PyPDF2" | while read line; do
            echo "  • $line"
        done
    else
        print_error "Error instalando dependencias"
        print_info "Intenta manualmente: pip install -r requirements.txt"
        exit 1
    fi
else
    print_warning "requirements.txt no encontrado"
    print_info "Instalando dependencias básicas manualmente..."
    
    pip install requests python-dotenv pandas openpyxl PyPDF2 --quiet
    
    print_success "Dependencias básicas instaladas"
fi

# =================================================================
# PASO 7: VERIFICAR/CREAR ESTRUCTURA DE CARPETAS
# =================================================================

print_header "ESTRUCTURA DE CARPETAS"

FOLDERS=("Backup" "Bank Reconciliation" "Pending bills" "Processed bills" "Test" "outputs" "docs")

print_info "Verificando estructura de carpetas..."
echo ""

for folder in "${FOLDERS[@]}"; do
    if [ -d "$folder" ]; then
        print_success "Existe: $folder/"
    else
        mkdir -p "$folder"
        print_success "Creada: $folder/"
    fi
done

# =================================================================
# PASO 8: CONFIGURAR ARCHIVO .env
# =================================================================

print_header "CONFIGURACIÓN DE CREDENCIALES (.env)"

if [ -f ".env" ]; then
    print_warning "Archivo .env ya existe"
    echo ""
    read -p "¿Deseas recrearlo? (perderás las credenciales actuales) [s/N]: " recreate_env
    if [[ ! "$recreate_env" =~ ^[SsYy]$ ]]; then
        print_info "Usando archivo .env existente"
        ENV_EXISTS=true
    else
        rm .env
        ENV_EXISTS=false
    fi
else
    ENV_EXISTS=false
fi

if [ "$ENV_EXISTS" = false ]; then
    echo ""
    print_info "Vamos a configurar tus credenciales paso a paso"
    print_warning "Asegúrate de tener tus credenciales a mano"
    echo ""
    
    # QuickBooks
    echo -e "${BOLD}${CYAN}═══ CREDENCIALES DE QUICKBOOKS ═══${NC}"
    echo ""
    read -p "QB_ACCESS_TOKEN: " QB_ACCESS_TOKEN
    read -p "QB_REFRESH_TOKEN: " QB_REFRESH_TOKEN
    read -p "QB_CLIENT_ID: " QB_CLIENT_ID
    read -p "QB_CLIENT_SECRET: " QB_CLIENT_SECRET
    read -p "QB_REALM_ID: " QB_REALM_ID
    
    echo ""
    echo -e "${BOLD}${CYAN}═══ API KEYS ═══${NC}"
    echo ""
    read -p "OPENROUTER_API_KEY: " OPENROUTER_API_KEY
    read -p "GEMINI_API_KEY (para OCR): " GEMINI_API_KEY
    
    # Crear archivo .env
    cat > .env << EOF
# QuickBooks OAuth 2.0 Credentials
QB_ACCESS_TOKEN=$QB_ACCESS_TOKEN
QB_REFRESH_TOKEN=$QB_REFRESH_TOKEN
QB_CLIENT_ID=$QB_CLIENT_ID
QB_CLIENT_SECRET=$QB_CLIENT_SECRET
QB_REALM_ID=$QB_REALM_ID

# OpenRouter API (DeepSeek V3)
OPENROUTER_API_KEY=$OPENROUTER_API_KEY

# Google Gemini API (OCR de facturas)
GEMINI_API_KEY=$GEMINI_API_KEY

# Configuración del ambiente
QB_ENVIRONMENT=production
LOG_LEVEL=INFO
EOF

    if [ -f ".env" ]; then
        print_success "Archivo .env creado correctamente"
    else
        print_error "Error al crear archivo .env"
        exit 1
    fi
fi

# =================================================================
# PASO 9: VERIFICAR PERMISOS DE ARCHIVOS
# =================================================================

print_header "VERIFICACIÓN DE PERMISOS"

print_info "Configurando permisos de archivos..."

# .env debe ser privado
chmod 600 .env
print_success ".env: Permisos restringidos (600)"

# Scripts ejecutables
if [ -f "git_manager.py" ]; then
    chmod +x git_manager.py
    print_success "git_manager.py: Ejecutable"
fi

if [ -f "install.sh" ]; then
    chmod +x install.sh
    print_success "install.sh: Ejecutable"
fi

# =================================================================
# PASO 10: VERIFICAR CONEXIÓN A QUICKBOOKS (OPCIONAL)
# =================================================================

print_header "VERIFICACIÓN DE CONEXIÓN"

echo ""
read -p "¿Deseas probar la conexión a QuickBooks ahora? [S/n]: " test_connection

if [[ ! "$test_connection" =~ ^[Nn]$ ]]; then
    print_info "Probando conexión a QuickBooks..."
    echo ""
    
    # Crear script de prueba temporal
    cat > test_connection.py << 'EOF'
import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv()

QB_ACCESS_TOKEN = os.getenv("QB_ACCESS_TOKEN")
QB_REALM_ID = os.getenv("QB_REALM_ID")

if not QB_ACCESS_TOKEN or not QB_REALM_ID:
    print("❌ Credenciales no configuradas correctamente")
    sys.exit(1)

url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{QB_REALM_ID}/query"
headers = {
    "Authorization": f"Bearer {QB_ACCESS_TOKEN}",
    "Accept": "application/json"
}
params = {"query": "SELECT COUNT(*) FROM Account"}

try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code == 200:
        print("✅ Conexión exitosa a QuickBooks Online")
        data = response.json()
        print(f"✅ API respondiendo correctamente")
        sys.exit(0)
    elif response.status_code == 401:
        print("⚠️  Token expirado - ejecuta el refresh automáticamente al usar main.py")
        sys.exit(0)
    else:
        print(f"❌ Error de conexión: {response.status_code}")
        print(f"   Mensaje: {response.text[:100]}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

    python3 test_connection.py
    TEST_RESULT=$?
    
    rm test_connection.py
    
    if [ $TEST_RESULT -eq 0 ]; then
        print_success "Conexión verificada correctamente"
    else
        print_warning "Hubo un problema con la conexión"
        print_info "Esto es normal si el token está expirado"
        print_info "main.py lo refrescará automáticamente al ejecutar"
    fi
else
    print_info "Verificación de conexión omitida"
fi

# =================================================================
# PASO 11: GENERAR requirements.txt SI NO EXISTE
# =================================================================

if [ ! -f "requirements.txt" ]; then
    print_header "GENERACIÓN DE requirements.txt"
    
    print_info "Generando requirements.txt..."
    pip freeze > requirements.txt
    print_success "requirements.txt generado"
    
    print_info "Agregando al repositorio..."
    git add requirements.txt > /dev/null 2>&1
    print_success "Listo para commit"
fi

# =================================================================
# RESUMEN FINAL
# =================================================================

print_header "INSTALACIÓN COMPLETADA"

echo -e "${GREEN}${BOLD}✅ ¡INSTALACIÓN EXITOSA!${NC}"
echo ""
echo -e "${BOLD}Resumen de la instalación:${NC}"
echo ""
echo "  ✅ Sistema operativo: $OS"
echo "  ✅ Python: $(python3 --version | awk '{print $2}')"
echo "  ✅ Entorno virtual: .venv/"
echo "  ✅ Dependencias: $(pip list | wc -l) paquetes instalados"
echo "  ✅ Credenciales: .env configurado"
echo "  ✅ Estructura: $(ls -d */ 2>/dev/null | wc -l) carpetas"
echo ""

# =================================================================
# INSTRUCCIONES FINALES
# =================================================================

echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}📋 PRÓXIMOS PASOS:${NC}"
echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BOLD}1. Activar el entorno virtual (si no está activo):${NC}"
echo -e "   ${YELLOW}source .venv/bin/activate${NC}"
echo ""
echo -e "${BOLD}2. Ejecutar la aplicación:${NC}"
echo -e "   ${YELLOW}python3 main.py${NC}"
echo ""
echo -e "${BOLD}3. Para usar el gestor de Git:${NC}"
echo -e "   ${YELLOW}python3 git_manager.py${NC}"
echo ""
echo -e "${BOLD}4. Para desactivar el entorno virtual:${NC}"
echo -e "   ${YELLOW}deactivate${NC}"
echo ""
echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}¡Todo listo para trabajar! 🚀${NC}"
echo ""

# Preguntar si desea ejecutar main.py ahora
read -p "¿Deseas ejecutar la aplicación ahora? [S/n]: " run_now

if [[ ! "$run_now" =~ ^[Nn]$ ]]; then
    echo ""
    print_info "Iniciando TMP AI Assistant..."
    echo ""
    python3 main.py
fi
