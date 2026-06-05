"""
scripts/verify_tool_integrity.py
================================

Standalone CLI para verificar la integridad del registry de tools.

USO:
    python scripts/verify_tool_integrity.py         # exit 0 si ok, 1 si hay gaps
    python scripts/verify_tool_integrity.py --quiet # solo exit code, sin output

USO EN CI / PRE-COMMIT:
    python scripts/verify_tool_integrity.py --quiet || exit 1

USO EN AUTO-VERIFY (raise on failure):
    DEXTER_STRICT_INTEGRITY=1 python -c "import dexter.tools"

QUÉ VERIFICA:
    - Orphans: wrappers `tool_*` en main.py que NO están en ALL_FUNCTIONS
              (estos tools existen pero el LLM no los ve — bug peligroso)
    - Unwired: entradas en ALL_FUNCTIONS sin schema correspondiente
              (estos tools el LLM los ve pero el dispatch falla)
"""
import argparse
import sys
from pathlib import Path

# Permitir import desde el root del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica que todos los tool_* wrappers de main.py estén registrados en dexter.tools.ALL_FUNCTIONS"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Solo retorna exit code (0=ok, 1=gaps), sin output",
    )
    args = parser.parse_args()

    from dexter.tools import verify_tool_integrity

    result = verify_tool_integrity(verbose=not args.quiet)

    if result["ok"]:
        if not args.quiet:
            print(f"OK — {result['total_wrappers']} tools, todas registradas.")
        return 0

    if not args.quiet:
        print(f"\nFAIL — {result['total_wrappers']} wrappers, {result['total_registered']} registradas.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
