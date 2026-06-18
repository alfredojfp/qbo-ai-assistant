#!/usr/bin/env bash
# ============================================================
# run_dexter_mcp.sh — Launcher con backend oficial de Intuit
# ============================================================
# Usa el motor QBO de Intuit (144 tools, 396 tests) en vez del
# motor nativo de Dexter. Requiere Node.js >= 20.
# Si el MCP no está instalado, Dexter hace fallback a native.
# ============================================================

set -e
set +e

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
elif [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
fi

export QB_BACKEND=mcp

PYTHON="${PYTHON:-python3}"

echo "============================================================"
echo "  DEXTER - QuickBooks AI Assistant"
echo "  Motor: Intuit MCP (144 tools, 396 tests, 100% coverage)"
echo "============================================================"
echo ""

if [[ ! -f "main.py" ]]; then
    echo "ERROR: main.py no encontrado en $SCRIPT_DIR"
    read -rp "Presiona Enter para cerrar..."
    exit 1
fi

if [[ ! -f ".env" ]]; then
    echo "🔧 Primera ejecución detectada. Lanzando asistente..."
    $PYTHON scripts/setup_wizard.py
    EXIT_CODE=$?
    if [[ $EXIT_CODE -ne 0 ]] || [[ ! -f ".env" ]]; then
        echo "❌ Configuración cancelada o incompleta."
        read -rp "Presiona Enter para cerrar..."
        exit 1
    fi
fi

$PYTHON main.py
EXIT_CODE=$?

echo ""
echo "============================================================"
echo "  Dexter terminó con código: $EXIT_CODE"
echo "============================================================"
read -rp "Presiona Enter para cerrar esta ventana..."
exit $EXIT_CODE
