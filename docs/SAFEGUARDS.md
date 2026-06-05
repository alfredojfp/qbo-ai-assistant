# Safeguards — Integridad del Registry de Tools

## El problema

En Sprint 5 (refactor main.py → dexter/tools/) establecimos un patrón:
- Cada tool nuevo sigue TDD con test en `tests/test_tools_aggregator.py`
- Cada módulo en `dexter/tools/` exporta `SCHEMA` + `FUNCTIONS` + `KEYWORDS`
- El agregador `dexter/tools/__init__.py` los une en `ALL_SCHEMAS` y `ALL_FUNCTIONS`
- `main.py` define un wrapper `tool_xxx()` que se registra en `TOOL_FUNCTIONS` (dispatch table)

**Bugs que esto previene:**
1. agregar un `tool_nuevo()` en main.py pero olvidar registrarlo
   en `dexter/tools/<modulo>.py`. El LLM no podría llamarlo aunque el código existe.
2. agregar el schema y FUNCTIONS a `dexter/tools/<modulo>.py` pero olvidar agregar
   el `tool_xxx` wrapper a `TOOL_FUNCTIONS` en main.py. El LLM ve el schema y llama
   el tool, pero main.py responde "Tool no encontrado" → loop → "límite de iteraciones"
   alcanzado → usuario frustrado. **Este bug es crítico** (afecta el flujo conversacional
   completo) y no se detecta sin el safeguard.
3. la signature de `tool_xxx` no coincide con los parámetros del schema
   (p. ej., schema dice `nombre: str` pero wrapper tiene `name: str`). El LLM pasa
   `nombre` y Python lanza `TypeError: unexpected keyword argument` → loop →
   "límite de iteraciones". **Mismo síntoma que el bug 2, distinta causa raíz.**

## Lo que el safeguard SÍ detecta

| Check | Detecta | Severidad |
|---|---|---|
| `orphans` | `tool_xxx` en main.py que NO está en `ALL_FUNCTIONS` | 🟠 LLM no ve el tool |
| `registered_unwired` | Entrada en `ALL_FUNCTIONS` sin schema | 🟡 Schema falta |
| `not_dispatched` | Schema en `ALL_SCHEMAS` que NO está en `TOOL_FUNCTIONS` | 🔴 **Crítico** (causa "límite de iteraciones") |
| `signature_mismatches` | Signature de `tool_xxx` incompatible con schema | 🔴 **Crítico** (causa TypeError → "límite de iteraciones") |

## Lo que el safeguard NO detecta (limitaciones)

| Bug | Detectable por |
|---|---|
| Tool corre pero `create_X` apunta al endpoint equivocado de QBO | Test de integración con sandbox |
| Tool corre, retorna OK, pero la data es incorrecta | Test de integración con assertions |
| QBO API cambió su schema y el tool ya no funciona | Monitoreo en producción + tests con sandbox actualizado |
| QBO rate limit excedido | Logs + retry logic |
| Auth token expirado | `refresh_qb_token` + auto-refresh (ya implementado) |
| Permisos de OAuth insuficientes | Validar scopes al hacer OAuth flow |

Para esos casos, los **logs persistentes** en `dexter/error_log.py` + tests
de integración manuales con sandbox son la red de seguridad.

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
#   "total_dispatched": int,  # entries en main.TOOL_FUNCTIONS
#   "orphans": ["tool_xxx", ...],  # en main.py, NO en registry
#   "registered_unwired": [...],  # en registry, sin schema
#   "not_dispatched": [...],  # schemas SIN entry en TOOL_FUNCTIONS (LLM los ve pero dispatch falla)
#   "signature_mismatches": [{tool, issue}, ...],  # signature incompatible con schema
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

11 tests en `tests/test_tools_aggregator.py:TestVerifyToolIntegrity`:
- `test_result_keys_present`: estructura del dict de retorno (incluye keys de dispatch + signature)
- `test_baseline_no_orphans`: estado limpio (100 tools, 0 gaps)
- `test_detects_injected_orphan`: inyección de un `tool_test_xxx` huérfano
- `test_verbose_writes_to_stderr_on_failure`: verbose=True escribe a stderr
- `test_verbose_silent_when_ok`: verbose=True NO escribe si todo OK
- `test_total_wrappers_count`: count de wrappers únicos == count registrados
- `test_result_keys_include_dispatch_check`: incluye `not_dispatched` y `total_dispatched`
- `test_all_schemas_are_dispatched`: 100/100 schemas tienen entry en `TOOL_FUNCTIONS`
- `test_verbose_dispatch_failure_mentions_dispatch`: si hay gap de dispatch, el verbose lo menciona
- `test_result_keys_include_signature_check`: incluye `signature_mismatches`
- `test_all_signatures_match_schemas`: 100/100 signatures compatibles con sus schemas

## Caso de estudio: los bugs que cazó

### Bug 1: orphan en registry
Durante el desarrollo inicial del safeguard, `verify_tool_integrity` detectó que
`tool_procesar_lote_bills` (recién agregado) no estaba en
`dexter/tools/ocr.py` (solo `procesar_lote_bills` sin prefijo `tool_`).
Fix: agregar wrapper `tool_procesar_lote_bills` en main.py + cambiar import
en `dexter/tools/ocr.py` de `procesar_lote_bills` a `tool_procesar_lote_bills`.

### Bug 2: schema sin dispatch (CRÍTICO)
Después de implementar el check de `not_dispatched`, el safeguard detectó que
**57 tools** (todos los de Sprints 1+2+3) tenían schema y wrapper pero
**faltaban en `TOOL_FUNCTIONS` en main.py**. Esto significa que el LLM llamaba
el tool (veía el schema) → main.py respondía "Tool no encontrado" → el LLM
intentaba de nuevo → 5 iteraciones → "límite de iteraciones" → usuario frustrado.

**Síntoma reportado por el usuario:**
> 👤 Tú: necesito que crees un nuevo cliente con el nombre Prueba1
> 🤖 Se alcanzó el límite de iteraciones. Por favor, reformula tu pregunta.

**Root cause:** `TOOL_FUNCTIONS` solo tenía 43 entries, pero `ALL_FUNCTIONS`
tenía 100. 57 schemas no estaban conectados al dispatch.

**Fix:** agregar los 57 entries faltantes a `TOOL_FUNCTIONS` en main.py
(organizados por sprint). Después del fix, llamada real a QBO sandbox creó
cliente con ID 62.

Esto demuestra que el safeguard funciona para bugs críticos que
**no se pueden detectar solo con tests unitarios** — el test pasa porque
el wrapper existe, pero la integración end-to-end falla.

## Mantenimiento futuro

- **Agregar un módulo nuevo**: el auto-verify lo detecta automáticamente
- **Agregar un tool nuevo**: las 3 capas lo cazan si olvidas registrarlo
- **Refactorizar wrappers duplicados (es/en)**: el count usa `id(fn)` para
  deduplicar aliases, así que no genera falsos positivos
