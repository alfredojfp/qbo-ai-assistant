# Spec: Refactor main.py → dexter/tools/* + Context Engineering

**Fecha:** 2026-06-04
**Autor:** Proceso de brainstorming con opencode (claude minimax-m3-free)
**Estado:** Diseño aprobado por el usuario
**Versión del proyecto (al inicio):** 4.0.0-dev
**Worktree:** `.worktrees/refactor-main` (rama `refactor/main-2026`)
**Alcance:** Refactor estructural de `main.py` (3,529 líneas) + context engineering.

---

## 🎯 Objetivo

Transformar `main.py` en un shim delgado (~150 líneas) que importa y re-exporta 43 herramientas organizadas por dominio en `dexter/tools/`, y aplicar las prácticas de context engineering aprendidas (system prompt modular, history compaction, tool descriptions optimizadas) para reducir el costo de tokens consumidos por el LLM.

**Beneficios medibles:**
- `main.py` pasa de 3,529 → ~150 líneas (un -96% en tamaño)
- 43 schemas con wiring real (de 24/43 → 43/43) — bug pre-existente resuelto
- Reducción estimada de 20-30% en tokens de TOOLS schemas
- 0 líneas removidas del comportamiento externo (`from main import tool_xxx` sigue funcionando)
- Base para futuros refactors incrementales (cada dominio commiteable por separado)

---

## 📐 Decisiones de diseño acordadas

| Decisión | Valor | Justificación |
|---|---|---|
| **Approach** | Mixto: estructura por dominios + context engineering | Combina organización de archivos con optimización de lo que ve el LLM |
| **Worktree** | `.worktrees/refactor-main` (rama `refactor/main-2026`) | Aísla el refactor del main con 18 commits ahead; rollback trivial |
| **Ritmo** | Incremental: 1 dominio por fase (7 fases) | Bajo riesgo, cada fase es commiteable y reversible |
| **Backward compat** | 100% shim: main.py re-exporta `tool_xxx` | Ningún consumer externo se rompe |
| **Fase 1 piloto** | bank_feed (4 tools) | Motor ya reescrito, 27 tests, balance riesgo/valor |

---

## 🏗️ Arquitectura objetivo

### Estructura de archivos (final, tras 7 fases)

```
dexter/
├── __init__.py                    # 4.0.0-dev (existente)
├── core/                          # Existente — sin cambios
│   ├── batch/                     # engine, storage, disambiguator, deposits, recon_tagger
│   └── qbo_client.py
├── tools/                         # NUEVO — un módulo por dominio
│   ├── __init__.py                # registry agregador
│   ├── _schema_utils.py           # helpers: build_schema(), build_function()
│   ├── search.py                  # 4 tools (cliente, vendor, cuenta, item)
│   ├── transactions.py            # 4 tools (invoice, bill, deposit, pago)
│   ├── reports.py                 # 5 tools (P&L, BS, custom, save, load, list)
│   ├── tokens.py                  # 2 tools (stats, informe)
│   ├── admin.py                   # 2 tools (chart_accounts, empresas)
│   ├── batch.py                   # 3 tools (csv, template, depositar_lote)
│   ├── reconciliation.py          # 3 tools BNK-RECON
│   ├── ocr.py                     # 1 tool (lote_bills) + helpers Gemini
│   ├── bank_feed.py               # 4 tools (Fase 1 — piloto)
│   ├── behavior.py                # 4 tools user_behavior
│   ├── report_custom.py           # 2 tools (custom, parse_fecha)
│   ├── api_explorer.py            # 5 tools (list, info, request, docs, web)
│   ├── journal.py                 # 2 tools (asiento, transferencia)
│   └── web_code.py                # 2 tools (web search, code exec)
└── context/                       # NUEVO — context engineering (Fase 7)
    ├── __init__.py
    ├── prompt.py                  # SYSTEM_PROMPT modular por secciones
    ├── history.py                 # ConversationHistory con compaction
    └── tool_filter.py             # get_relevant_tools() real
main.py                            # SHIM — ~150 líneas: importa + re-exporta
```

### El patrón shim (template replicable por dominio)

**`dexter/tools/bank_feed.py`** (la plantilla):
```python
"""Tools: bank_feed (4) — análisis y clasificación de transacciones bancarias."""
from typing import Any
from autonomia.bank_feed_intelligence import (
    tool_analyze_bankfeed_for_classification,
    tool_record_bankfeed_classification,
    tool_get_classification_history_stats,
    tool_find_pattern_for_transaction,
)

SCHEMA = [
    {"name": "analizarbankfeed", "description": "...", "parameters": {...}},
    {"name": "registrarclasificacion", "description": "...", "parameters": {...}},
    {"name": "estadisticasclasificacion", "description": "...", "parameters": {...}},
    {"name": "buscarpatron", "description": "...", "parameters": {...}},
]

FUNCTIONS = {
    "analizarbankfeed": tool_analyze_bankfeed_for_classification,
    "registrarclasificacion": tool_record_bankfeed_classification,
    "estadisticasclasificacion": tool_get_classification_history_stats,
    "buscarpatron": tool_find_pattern_for_transaction,
}
```

**`dexter/tools/__init__.py`** (agregador):
```python
"""dexter.tools — registry agregador de todas las herramientas."""
from dexter.tools import (
    bank_feed, search, transactions, reports, tokens, admin,
    batch, reconciliation, ocr, behavior, report_custom,
    api_explorer, journal, web_code,
)

ALL_SCHEMAS = []
ALL_FUNCTIONS = {}
for module in [bank_feed, search, transactions, ...]:
    for schema in module.SCHEMA:
        ALL_SCHEMAS.append(schema)
        ALL_FUNCTIONS[schema["name"]] = module.FUNCTIONS[schema["name"]]
```

**`main.py`** (después del refactor):
```python
# ~150 líneas
from dexter.tools import ALL_SCHEMAS as TOOLS, ALL_FUNCTIONS as _TOOL_FUNCTIONS
from dexter.tools.bank_feed import (
    tool_analyze_bankfeed_for_classification as tool_analizarbankfeed,
    ...
)
# ... ~40 re-exports

def main_loop():
    ...

def _dispatch_tool_call(name: str, args: dict) -> Any:
    return _TOOL_FUNCTIONS[name](**args)
```

---

## 🔍 Diagnóstico: el bug pre-existente de los stubs

**Hallazgo:** 43 schemas existen en `TOOLS` (lo que el LLM ve) pero solo 24 tienen `def tool_xxx()` real. Los 19 schemas restantes (todos en `autonomia/*.py`) NO están wireados — el LLM los llama y obtiene `KeyError: 'tool not found'`.

**Fase 0 resuelve esto:** crea el patrón de wiring para que el 100% de los schemas sean funcionales.

---

## 📅 Plan de fases

| Fase | Dominio | # tools | Esfuerzo estimado | Sesión |
|---|---|---|---|---|
| **0** | Pre-fase: arreglar `TOOL_FUNCTIONS` + auditar stubs | 19 fixes | 1h | HOY |
| **1** | bank_feed (piloto, valida patrón) | 4 | 2h | HOY |
| **2** | search (4) + transactions (4) | 8 | 2h | Siguiente |
| **3** | reports (5) + tokens (2) + admin (2) | 9 | 2h | Siguiente |
| **4** | batch (3) + reconciliation (3) | 6 | 1.5h | +1 |
| **5** | ocr (1) + behavior (4) + report_custom (2) | 7 | 2h | +1 |
| **6** | api_explorer (5) + journal (2) + web_code (2) | 9 | 2h | +1 |
| **7** | Context engineering (prompt, history, tool_filter) | — | 3h | +1 |

**Total estimado:** 15.5 horas distribuidas en 5-7 sesiones.

### Detalle Fase 0 (HOY)

1. Crear `dexter/tools/_schema_utils.py` con helpers
2. Crear `dexter/tools/__init__.py` con agregador
3. Mover los 19 schemas stubs a sus respectivos módulos en `dexter/tools/`
4. Verificar: `len(TOOLS) == 43` y `set(s["name"] for s in TOOLS) == set(ALL_FUNCTIONS.keys())`
5. Test: nuevo test que verifica el wiring completo
6. Commit atómico

### Detalle Fase 1 (HOY, después de Fase 0)

1. Crear `dexter/tools/bank_feed.py` con 4 tools (los de `autonomia/bank_feed_intelligence.py`)
2. Agregar al agregador `dexter/tools/__init__.py`
3. Remover definiciones inline de main.py (Fase 0 ya lo hizo por estos stubs)
4. Agregar re-exports en main.py: `from dexter.tools.bank_feed import tool_xxx as tool_xxx`
5. Test: test que verifica `from main import tool_analizarbankfeed` y que dispatch funciona
6. Commit atómico

---

## 🧪 Estrategia de testing

- **Tests existentes:** 271 tests en 13 archivos. Ninguno debe romperse.
- **Por fase:** agregar 1 test de wiring que verifique `tool_xxx in ALL_FUNCTIONS`.
- **Fase 0:** test que verifica `len(TOOLS) == 43 AND all schemas in ALL_FUNCTIONS`.
- **Fase 7 (context engineering):** test que mide tokens antes/después (con `tiktoken` o equivalente).
- **Smoke test final:** `python3 -c "from main import *; assert callable(tool_buscar_cliente)"` + 271+ tests.

---

## ↩️ Rollback strategy

- Cada fase = 1 commit atómico en `refactor/main-2026`
- Si una fase falla: `git revert <commit>` (rollback limpio)
- Si la decisión de shim falla: cambiar `dexter/tools/__init__.py` para no re-exportar; main.py vuelve a tener las defs inline
- El worktree se mantiene hasta que el usuario apruebe el merge final a main

---

## ✅ Criterios de éxito

- [ ] `main.py` < 200 líneas (era 3,529)
- [ ] `dexter/tools/` con 13 módulos, ninguno > 250 líneas
- [ ] `from main import tool_xxx` funciona para los 43 nombres
- [ ] 43/43 schemas tienen implementación real (0 stubs fantasma)
- [ ] 271+ tests pasando, +1 test de shim/wiring por fase
- [ ] 0 líneas removidas del comportamiento externo
- [ ] Cada fase commiteada independientemente, fusionable a main sin conflictos
- [ ] Al terminar las 7 fases: context engineering aplicado (SYSTEM_PROMPT modular, history compaction, tool_filter optimizado)

---

## 📚 Documentación a actualizar

Por fase:
- `docs/CHANGELOG.md` — entrada por cada fase completada
- `docs/ARCHITECTURE.md` — diagrama de `dexter/tools/*` después de cada fase mayor

Al cerrar todas las fases:
- `docs/CONTEXT.md` — sincronizar a v4.0.0 (refactor completo)
- `docs/CAPACIDADES.md` — reflejar nueva estructura

---

## ⚠️ Riesgos identificados

1. **Imports circulares:** main.py importa de `dexter.tools` que importa de `autonomia.*` que puede importar de `main`. Mitigación: imports lazy dentro de funciones cuando sea necesario.
2. **Tests de main_loop rompen:** porque `tool_xxx` cambia de fuente. Mitigación: 100% shim mantiene los nombres globales.
3. **Sesiones de los tools (e.g. `session_state`):** main.py tiene estado global que los tools van a necesitar. Mitigación: pasar `session_state` explícito o usar contextvars.
4. **Fase 0 + Fase 1 son grandes para una sola sesión:** si el tiempo escasea, dividir. Mitigación: commits atómicos permiten parar en cualquier momento.

---

## 🚀 Plan de deployment (al cerrar todas las fases)

1. **Debugging** (per requerimiento del usuario): ejecutar la app, smoke test, verificar 43 tools funcionan, validar context engineering.
2. **Merge** `refactor/main-2026` → `main` (fast-forward o merge commit, según prefieras).
3. **Push** a `origin/main` (con los 18 commits previos de la sesión + los del refactor).
4. **Actualizar carpeta local** del proyecto (que está en el mismo path) — el worktree se elimina y la rama se consolida.

---

**Próximo paso:** invocar `writing-plans` skill para crear el plan de implementación detallado de Fase 0 + Fase 1.
