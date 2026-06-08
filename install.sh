#!/usr/bin/env bash
# ============================================================
# Dexter — One-Command Install
#
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/alfredojfp/qbo-ai-assistant/main/install.sh | bash
#   # o local:
#   bash install.sh
# ============================================================
set -e

SKIP_DEPS=false
REPO_URL="https://github.com/alfredojfp/qbo-ai-assistant.git"
INSTALL_DIR="$HOME/dexter"

echo "============================================================"
echo "  🧠 Dexter — QuickBooks AI Agent"
echo "  Instalación rápida"
echo "============================================================"
echo ""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-deps) SKIP_DEPS=true; shift ;;
        --dir) INSTALL_DIR="$2"; shift 2 ;;
        *) echo "Opción desconocida: $1"; exit 1 ;;
    esac
done

echo "Directorio: $INSTALL_DIR"
echo ""

# Check Python
PYTHON=$(which python3 || which python)
if [[ -z "$PYTHON" ]]; then
    echo "❌ Python 3 no encontrado. Instalalo primero."
    exit 1
fi
echo "✅ $($PYTHON --version)"

# Check Git
if ! command -v git &>/dev/null; then
    echo "❌ Git no encontrado. Instalalo primero."
    exit 1
fi
echo "✅ Git $(git --version | cut -d' ' -f3)"

# Clone or update
if [[ -d "$INSTALL_DIR" ]]; then
    echo "📂 Dexter ya existe en $INSTALL_DIR"
    cd "$INSTALL_DIR"
    git pull --quiet
    echo "   Actualizado a la última versión."
else
    echo "📥 Clonando repositorio..."
    git clone "$REPO_URL" "$INSTALL_DIR" --quiet
    cd "$INSTALL_DIR"
    echo "   Repositorio clonado."
fi

# Install dependencies
if [[ "$SKIP_DEPS" != true ]]; then
    echo "📦 Instalando dependencias Python..."
    $PYTHON -m pip install -r requirements.txt --quiet
    echo "   Dependencias instaladas."
fi

# Make scripts executable
chmod +x run_dexter.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true

# Create launcher symlink
LAUNCHER="$HOME/.local/bin/dexter"
mkdir -p "$(dirname "$LAUNCHER")"
ln -sf "$INSTALL_DIR/run_dexter.sh" "$LAUNCHER" 2>/dev/null || true

echo ""
echo "============================================================"
echo "  ✅ Dexter instalado correctamente"
echo "============================================================"
echo ""
echo "Para iniciar:"
echo "  cd $INSTALL_DIR && ./run_dexter.sh"
echo "  # o desde cualquier lado:"
echo "  dexter"
echo ""
echo "La primera vez se lanzará el asistente de configuración."
echo ""

# Offer to launch setup wizard
read -rp "¿Querés configurar Dexter ahora? (S/n): " -r
if [[ -z "$REPLY" ]] || [[ "$REPLY" =~ ^[Ss]$ ]]; then
    echo ""
    $PYTHON scripts/setup_wizard.py
fi
