#!/usr/bin/env bash
# ============================================================
# run_dexter.sh — Launcher de Dexter (QuickBooks AI Assistant)
# ============================================================
# Se puede ejecutar:
#   - Directo desde terminal: ./run_dexter.sh
#   - Desde acceso directo .desktop (xfce4-terminal)
# ============================================================

set -e

# Desactivar set -e antes de la app — main.py puede retornar exit(1)
# por errores de auth/conexión, y queremos que el usuario vea el mensaje
# de error y el prompt "Presiona Enter" antes de que la terminal se cierre.
set +e

# Resolver el directorio del script (resuelve symlinks)
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")")" && pwd)"

cd "$SCRIPT_DIR"

# Detectar venv local si existe
if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
elif [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
fi

PYTHON="${PYTHON:-python3}"

echo "============================================================"
echo "  DEXTER - QuickBooks AI Assistant"
echo "  v4.1.0-dev (100 tools en 21 dominios)"
echo "============================================================"
echo ""
echo "Directorio: $SCRIPT_DIR"
echo "Python: $($PYTHON --version 2>&1)"
echo ""

# Verificar que main.py existe
if [[ ! -f "main.py" ]]; then
    echo "ERROR: main.py no encontrado en $SCRIPT_DIR"
    echo ""
    read -rp "Presiona Enter para cerrar..."
    exit 1
fi

# Verificar .env (credenciales QBO). Si no existe, lanzar setup wizard.
if [[ ! -f ".env" ]]; then
    echo ""
    echo "🔧 Primera ejecución detectada. Lanzando asistente de configuración..."
    echo ""
    $PYTHON scripts/setup_wizard.py
    EXIT_CODE=$?
    if [[ $EXIT_CODE -ne 0 ]] || [[ ! -f ".env" ]]; then
        echo ""
        echo "❌ Configuración cancelada o incompleta."
        read -rp "Presiona Enter para cerrar..."
        exit 1
    fi
    echo ""
    echo "✅ Configuración completa. Iniciando Dexter..."
    echo ""
fi

# Ejecutar la app
$PYTHON main.py
EXIT_CODE=$?

echo ""
echo "============================================================"
echo "  Dexter terminó con código: $EXIT_CODE"
echo "============================================================"
echo ""
read -rp "Presiona Enter para cerrar esta ventana..."
exit $EXIT_CODE
