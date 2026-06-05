# Safeguards — Integridad del Registry de Tools

## El problema

En Sprint 5 (refactor main.py → dexter/tools/) establecimos un patrón:
- Cada tool nuevo sigue TDD con test en `tests/test_tools_aggregator.py`
- Cada módulo en `dexter/tools/` exporta `SCHEMA` + `FUNCTIONS` + `KEYWORDS`
- El agregador `dexter/tools/__init__.py` los une en `ALL_SCHEMAS` y `ALL_FUNCTIONS`
- `main.py` define un wrapper `tool_xxx()` que se registra en el dispatch table

**Bug que esto previene:** agregar un `tool_nuevo()` en main.py pero olvidar registrarlo
en `dexter/tools/<modulo>.py`. El LLM no podría llamarlo aunque el código existe.

## Solución: 3 capas de defensa

### Layer 1 — Detección en runtime (auto-verify on import)

`dexter/tools/__init__.py:verify_tool_integrity(verbose=False)` corre al importar
`dexter.tools`. Si encuentra gaps:
- `verbose=False` (default): solo loggea, no falla
- `verbose=True`: imprime a stderr con detalle de los huérfanos
- `os.environ["DEXTER_STRICT_INTEGRITY"]="1"`: raise RuntimeError (para tests/CI)

```python
from dexter.tools import verify_tool_integrity
result = verify_tool_integrity(verbose=True)
# {
#   "ok": bool,
#   "total_wrappers": int,  # wrappers únicos en main.py
#   "total_registered": int,  # entries en ALL_FUNCTIONS
#   "orphans": ["tool_xxx", ...],  # en main.py, NO en registry
#   "registered_unwired": [...],  # en registry, sin schema
# }
```

### Layer 2 — Script standalone para CI

`scripts/verify_tool_integrity.py` corre la verificación desde línea de comandos:

```bash
python scripts/verify_tool_integrity.py         # exit 0 ok, exit 1 gaps
python scripts/verify_tool_integrity.py --quiet # solo exit code
```

Útil para CI (GitHub Actions, GitLab CI, etc.) y para ejecución manual.

### Layer 3 — Pre-commit hook (bloquea commits con gaps)

El hook vive en `.githooks/pre-commit` (trackeable en git, no en `.git/hooks/`
que es local). Instalación **una sola vez por clone** del repo:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

Una vez configurado, el hook corre antes de cada `git commit`:
- Si pasa: imprime "✓ Integridad OK", permite el commit
- Si falla: imprime detalle de los huérfanos y bloquea el commit (exit 1)

Para saltar el hook en un commit específico:
```bash
git commit --no-verify
```

**Nota:** `.git/hooks/` no se trackea en git, por eso el hook se versiona en
`.githooks/`. El setting `core.hooksPath` apunta git al directorio correcto.

## Tests

6 tests en `tests/test_tools_aggregator.py:TestVerifyToolIntegrity`:
- `test_result_keys_present`: estructura del dict de retorno
- `test_baseline_no_orphans`: estado limpio (100 tools, 0 gaps)
- `test_detects_injected_orphan`: inyección de un `tool_test_xxx` huérfano
- `test_verbose_writes_to_stderr_on_failure`: verbose=True escribe a stderr
- `test_verbose_silent_when_ok`: verbose=True NO escribe si todo OK
- `test_total_wrappers_count`: count de wrappers únicos == count registrados

## Caso de estudio: el bug que cazó

Durante el desarrollo del safeguard, `verify_tool_integrity` detectó que
`tool_procesar_lote_bills` (recién agregado) no estaba en
`dexter/tools/ocr.py` (solo `procesar_lote_bills` sin prefijo `tool_`).
Fix: agregar wrapper `tool_procesar_lote_bills` en main.py + cambiar import
en `dexter/tools/ocr.py` de `procesar_lote_bills` a `tool_procesar_lote_bills`.

Esto demuestra que el safeguard funciona: SIN él, el LLM no habría podido
llamar `procesar_lote_bills` y el bug habría llegado a producción.

## Mantenimiento futuro

- **Agregar un módulo nuevo**: el auto-verify lo detecta automáticamente
- **Agregar un tool nuevo**: las 3 capas lo cazan si olvidas registrarlo
- **Refactorizar wrappers duplicados (es/en)**: el count usa `id(fn)` para
  deduplicar aliases, así que no genera falsos positivos
