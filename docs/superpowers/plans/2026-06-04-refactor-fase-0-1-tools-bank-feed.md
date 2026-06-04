# Refactor main.py — Fase 0 (infra) + Fase 1 (bank_feed piloto) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear la infraestructura `dexter/tools/` (agregador + schema_utils) y migrar el primer dominio (bank_feed, 4 tools) como piloto, wireando 4 stubs fantasma que existían en `TOOLS` pero no tenían `def tool_xxx()`.

**Architecture:**
- `dexter/tools/_schema_utils.py`: helpers para construir schemas de tool
- `dexter/tools/__init__.py`: agregador que itera módulos y construye `ALL_SCHEMAS` + `ALL_FUNCTIONS`
- `dexter/tools/bank_feed.py`: 4 funciones de `autonomia/bank_feed_intelligence.py` envueltas como tools
- `main.py` (cambios mínimos): 4 re-exports `from dexter.tools.bank_feed import tool_xxx as tool_xxx` para mantener backward compat

**Tech Stack:** Python 3.9+, stdlib (unittest, dataclasses, typing), ningún framework nuevo.

**Working directory:** `/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main` (rama `refactor/main-2026`)

---

## File Structure

**Archivos a crear:**
- `dexter/tools/__init__.py` (~30 líneas) — agregador
- `dexter/tools/_schema_utils.py` (~40 líneas) — helpers
- `dexter/tools/bank_feed.py` (~80 líneas) — 4 tools
- `tests/test_tools_aggregator.py` (~80 líneas) — test del wiring

**Archivos a modificar:**
- `main.py` — agregar 4 re-exports (líneas ~2413+ no cambian, solo se prependen imports)
- `tests/test_main_loop.py` — agregar test que verifique `from main import tool_analizarbankfeed` funciona

**Archivos NO modificados (en esta fase):**
- `autonomia/bank_feed_intelligence.py` — las 4 funciones ya existen
- `dexter/core/*` — no se toca

---

## Task 1: Crear `dexter/tools/_schema_utils.py`

**Files:**
- Create: `dexter/tools/_schema_utils.py`

- [ ] **Step 1: Crear el archivo con helpers**

```python
"""dexter.tools._schema_utils — helpers para construir schemas de tool.

Una tool de OpenAI/Anthropic tiene la forma:
    {"name": str, "description": str, "parameters": {"type": "object", "properties": {...}, "required": [...]}}

Estos helpers reducen boilerplate y mantienen consistencia.
"""
from typing import Any, Dict, List, Optional


def make_schema(
    name: str,
    description: str,
    properties: Dict[str, Any],
    required: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Construye un schema de tool con la forma canónica de OpenRouter.

    Args:
        name: nombre único de la tool (snake_case)
        description: qué hace, cuándo usarla, qué retorna (1-3 frases)
        properties: dict de parámetros con sus tipos
        required: lista de nombres de parámetros obligatorios

    Returns:
        Schema listo para enviar al LLM.
    """
    return {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required or [],
        },
    }


def prop_str(description: str, enum: Optional[List[str]] = None) -> Dict[str, Any]:
    """Helper para propiedad string."""
    out: Dict[str, Any] = {"type": "string", "description": description}
    if enum is not None:
        out["enum"] = enum
    return out


def prop_num(description: str, minimum: Optional[float] = None) -> Dict[str, Any]:
    """Helper para propiedad number."""
    out: Dict[str, Any] = {"type": "number", "description": description}
    if minimum is not None:
        out["minimum"] = minimum
    return out


def prop_bool(description: str) -> Dict[str, Any]:
    """Helper para propiedad boolean."""
    return {"type": "boolean", "description": description}


def prop_list(description: str, items: Dict[str, Any]) -> Dict[str, Any]:
    """Helper para propiedad array."""
    return {
        "type": "array",
        "description": description,
        "items": items,
    }
```

- [ ] **Step 2: Verificar que el módulo es importable**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && python3 -c "from dexter.tools._schema_utils import make_schema, prop_str; s = make_schema('test', 'desc', {'a': prop_str('param a')}); print(s)"
```

Expected: prints a dict with `name=test, description=desc, parameters={type: object, properties: {a: {type: string, description: param a}}, required: []}`

- [ ] **Step 3: No commit todavía** (esperamos al commit final con la registry)

---

## Task 2: Crear `dexter/tools/bank_feed.py` (4 tools)

**Files:**
- Create: `dexter/tools/bank_feed.py`

- [ ] **Step 1: Crear el archivo**

```python
"""dexter.tools.bank_feed — 4 tools para análisis y clasificación de bank feeds.

Delega a autonomia.bank_feed_intelligence (motor de matching en cascada).
"""
from typing import Any, Dict, List

from autonomia.bank_feed_intelligence import (
    tool_analyze_bankfeed_for_classification,
    tool_find_pattern_for_transaction,
    tool_get_classification_history_stats,
    tool_record_bankfeed_classification,
)
from dexter.tools._schema_utils import (
    make_schema,
    prop_list,
    prop_num,
    prop_str,
)

SCHEMA: List[Dict[str, Any]] = [
    make_schema(
        name="analizarbankfeed",
        description=(
            "Analiza un lote de transacciones bancarias y sugiere clasificaciones "
            "con score de confianza (0-100%) basado en patrones históricos. "
            "Retorna: lista de transacciones con account_id sugerido, "
            "vendor_id, confidence, reasoning."
        ),
        properties={
            "transacciones": prop_list(
                "Lista de transacciones con {id, descripcion, monto, fecha}",
                items={
                    "type": "object",
                    "properties": {
                        "id": prop_str("ID de la transacción en QBO"),
                        "descripcion": prop_str("Texto del banco (ej. 'AMAZON.COM*123')"),
                        "monto": prop_num("Monto en USD (positivo=ingreso, negativo=gasto)"),
                        "fecha": prop_str("Fecha ISO YYYY-MM-DD"),
                    },
                },
            ),
        },
        required=["transacciones"],
    ),
    make_schema(
        name="registrarclasificacion",
        description=(
            "Registra una clasificación manual de transacción para que el motor "
            "aprenda el patrón y la sugiera en el futuro. Aumenta el contador "
            "del patrón (idempotente)."
        ),
        properties={
            "transaccion_id": prop_str("ID de la transacción clasificada"),
            "clasificacion": prop_list(
                "Líneas de clasificación [{account_id, vendor_id, monto}]",
                items={
                    "type": "object",
                    "properties": {
                        "account_id": prop_str("QBO account ID"),
                        "vendor_id": prop_str("QBO vendor ID (opcional)",),
                        "monto": prop_num("Monto en esta línea"),
                    },
                },
            ),
        },
        required=["transaccion_id", "clasificacion"],
    ),
    make_schema(
        name="estadisticasclasificacion",
        description=(
            "Retorna estadísticas del motor: total clasificaciones, accuracy "
            "promedio, top 5 vendors, top 5 accounts, últimas N clasificaciones."
        ),
        properties={},
        required=[],
    ),
    make_schema(
        name="buscarpatron",
        description=(
            "Busca en el historial de clasificaciones el patrón que mejor "
            "matchea una descripción+monto. Retorna la mejor coincidencia con "
            "confidence (0-100) y el patrón matched (exacto, regex, fuzzy)."
        ),
        properties={
            "descripcion": prop_str("Descripción a buscar (ej. 'STARBUCKS #8521')"),
            "monto": prop_num("Monto en USD"),
        },
        required=["descripcion", "monto"],
    ),
]

FUNCTIONS: Dict[str, Any] = {
    "analizarbankfeed": tool_analyze_bankfeed_for_classification,
    "registrarclasificacion": tool_record_bankfeed_classification,
    "estadisticasclasificacion": tool_get_classification_history_stats,
    "buscarpatron": tool_find_pattern_for_transaction,
}
```

- [ ] **Step 2: Verificar import + que las 4 funciones existen**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && python3 -c "from dexter.tools.bank_feed import SCHEMA, FUNCTIONS; assert len(SCHEMA) == 4, len(SCHEMA); assert len(FUNCTIONS) == 4, len(FUNCTIONS); assert set(s['name'] for s in SCHEMA) == set(FUNCTIONS.keys()); print('OK 4/4')"
```

Expected: `OK 4/4`

- [ ] **Step 3: No commit todavía**

---

## Task 3: Crear `dexter/tools/__init__.py` (agregador)

**Files:**
- Create: `dexter/tools/__init__.py`

- [ ] **Step 1: Crear el archivo**

```python
"""dexter.tools — registry agregador de todas las herramientas.

Cada módulo (bank_feed, search, transactions, etc.) exporta:
    SCHEMA: List[dict]  — schemas para el LLM
    FUNCTIONS: Dict[str, Callable]  — name → callable

Este agregador los itera y construye:
    ALL_SCHEMAS: List[dict]  — para inyectar a OpenRouter
    ALL_FUNCTIONS: Dict[str, Callable]  — para dispatch del function calling
"""
from typing import Any, Callable, Dict, List

from dexter.tools import bank_feed
# Los siguientes módulos se irán agregando en fases posteriores:
# from dexter.tools import search, transactions, reports, tokens, admin,
#     batch, reconciliation, ocr, behavior, report_custom,
#     api_explorer, journal, web_code

ALL_SCHEMAS: List[Dict[str, Any]] = []
ALL_FUNCTIONS: Dict[str, Callable[..., Any]] = {}

_MODULES = [bank_feed]

for _module in _MODULES:
    for _schema in _module.SCHEMA:
        _name = _schema["name"]
        if _name in ALL_FUNCTIONS:
            raise ValueError(
                f"Duplicate tool name '{_name}' in {_module.__name__}"
            )
        ALL_SCHEMAS.append(_schema)
        ALL_FUNCTIONS[_name] = _module.FUNCTIONS[_name]


__all__ = ["ALL_SCHEMAS", "ALL_FUNCTIONS", "bank_feed"]
```

- [ ] **Step 2: Verificar el agregador**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && python3 -c "from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS; print(f'schemas={len(ALL_SCHEMAS)}, functions={len(ALL_FUNCTIONS)}'); print('names:', sorted(s[\"name\"] for s in ALL_SCHEMAS))"
```

Expected:
```
schemas=4, functions=4
names: ['analizarbankfeed', 'buscarpatron', 'estadisticasclasificacion', 'registrarclasificacion']
```

---

## Task 4: Crear `tests/test_tools_aggregator.py` (test del wiring)

**Files:**
- Create: `tests/test_tools_aggregator.py`

- [ ] **Step 1: Escribir los tests**

```python
"""Tests para dexter.tools — registry agregador y módulos individuales."""
import unittest


class TestBankFeedModule(unittest.TestCase):
    """Tests para dexter.tools.bank_feed (4 tools del bank feed intelligence)."""

    def test_module_imports(self):
        from dexter.tools import bank_feed
        self.assertTrue(hasattr(bank_feed, "SCHEMA"))
        self.assertTrue(hasattr(bank_feed, "FUNCTIONS"))

    def test_schema_count_matches_functions_count(self):
        from dexter.tools.bank_feed import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 4)
        self.assertEqual(len(FUNCTIONS), 4)

    def test_schema_function_names_match(self):
        from dexter.tools.bank_feed import SCHEMA, FUNCTIONS
        schema_names = {s["name"] for s in SCHEMA}
        function_names = set(FUNCTIONS.keys())
        self.assertEqual(schema_names, function_names)

    def test_expected_tool_names(self):
        from dexter.tools.bank_feed import SCHEMA
        names = {s["name"] for s in SCHEMA}
        self.assertEqual(
            names,
            {
                "analizarbankfeed",
                "registrarclasificacion",
                "estadisticasclasificacion",
                "buscarpatron",
            },
        )

    def test_each_function_is_callable(self):
        from dexter.tools.bank_feed import FUNCTIONS
        for name, fn in FUNCTIONS.items():
            self.assertTrue(callable(fn), f"{name} is not callable")

    def test_each_schema_has_required_fields(self):
        from dexter.tools.bank_feed import SCHEMA
        for s in SCHEMA:
            self.assertIn("name", s)
            self.assertIn("description", s)
            self.assertIn("parameters", s)
            self.assertEqual(s["parameters"]["type"], "object")
            self.assertIn("properties", s["parameters"])

    def test_descriptions_are_substantive(self):
        """Una description <30 chars probablemente no explica qué retorna."""
        from dexter.tools.bank_feed import SCHEMA
        for s in SCHEMA:
            self.assertGreater(
                len(s["description"]),
                30,
                f"Tool '{s['name']}' description too short: {s['description']!r}",
            )


class TestToolsAggregator(unittest.TestCase):
    """Tests para dexter.tools.__init__ (registry agregador)."""

    def test_all_schemas_imports(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        self.assertIsInstance(ALL_SCHEMAS, list)
        self.assertIsInstance(ALL_FUNCTIONS, dict)

    def test_no_duplicate_names(self):
        from dexter.tools import ALL_SCHEMAS
        names = [s["name"] for s in ALL_SCHEMAS]
        self.assertEqual(len(names), len(set(names)), "Duplicate tool names")

    def test_every_schema_has_matching_function(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        for s in ALL_SCHEMAS:
            self.assertIn(
                s["name"],
                ALL_FUNCTIONS,
                f"Schema '{s['name']}' has no matching function",
            )
            self.assertTrue(callable(ALL_FUNCTIONS[s["name"]]))

    def test_every_function_has_matching_schema(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        schema_names = {s["name"] for s in ALL_SCHEMAS}
        for fn_name in ALL_FUNCTIONS:
            self.assertIn(
                fn_name,
                schema_names,
                f"Function '{fn_name}' has no matching schema",
            )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Ejecutar los tests**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && python3 -m unittest tests.test_tools_aggregator -v 2>&1 | tail -20
```

Expected: 11 tests, all OK

- [ ] **Step 3: Verificar que no rompí los 271 tests existentes**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && python3 -m unittest discover tests 2>&1 | grep -E "^Ran|^OK$"
```

Expected: `Ran 282 tests in ...` (271 + 11 nuevos) `OK`

---

## Task 5: Agregar re-exports en `main.py` (4 imports)

**Files:**
- Modify: `main.py` (prepend after existing imports, around line 100-200)

- [ ] **Step 1: Localizar la zona de imports en main.py**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && grep -n "^import \|^from " main.py | head -20
```

Expected: lista de imports. Buscar el último bloque de imports antes de las definiciones de tools.

- [ ] **Step 2: Agregar los 4 re-exports**

Insertar después del último `from ... import ...` existente (típicamente después de imports de stdlib), el siguiente bloque:

```python
# === dexter.tools re-exports (refactor main.py → shim, Fase 1) ===
# Bank feed intelligence (4 tools): delegan a autonomia.bank_feed_intelligence
from dexter.tools.bank_feed import (
    tool_analyze_bankfeed_for_classification as tool_analizarbankfeed,
    tool_record_bankfeed_classification as tool_registrarclasificacion,
    tool_get_classification_history_stats as tool_estadisticasclasificacion,
    tool_find_pattern_for_transaction as tool_buscarpatron,
)
```

- [ ] **Step 3: Verificar backward compat**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && python3 -c "from main import tool_analizarbankfeed, tool_registrarclasificacion, tool_estadisticasclasificacion, tool_buscarpatron; print('All 4 re-exports OK:', [tool_analizarbankfeed.__name__, tool_registrarclasificacion.__name__, tool_estadisticasclasificacion.__name__, tool_buscarpatron.__name__])"
```

Expected: `All 4 re-exports OK: ['tool_analyze_bankfeed_for_classification', 'tool_record_bankfeed_classification', 'tool_get_classification_history_stats', 'tool_find_pattern_for_transaction']`

- [ ] **Step 4: Verificar que los 282 tests siguen pasando**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && python3 -m unittest discover tests 2>&1 | grep -E "^Ran|^OK$|^FAILED"
```

Expected: `Ran 282 tests in ...` `OK`

---

## Task 6: Agregar test de backward compat en `test_main_loop.py`

**Files:**
- Modify: `tests/test_main_loop.py` (append new test class)

- [ ] **Step 1: Append el test al final de `tests/test_main_loop.py`**

```python


class TestBankFeedReExports(unittest.TestCase):
    """Verifica que los 4 tools de bank_feed re-exportados desde main.py
    siguen siendo importables y callables (Fase 1 del refactor)."""

    def test_all_four_reexports_importable(self):
        from main import (
            tool_analizarbankfeed,
            tool_registrarclasificacion,
            tool_estadisticasclasificacion,
            tool_buscarpatron,
        )
        for fn in [
            tool_analizarbankfeed,
            tool_registrarclasificacion,
            tool_estadisticasclasificacion,
            tool_buscarpatron,
        ]:
            self.assertTrue(callable(fn))

    def test_reexports_point_to_autonomia_implementations(self):
        """Sanity: los re-exports NO son stubs vacíos."""
        from main import tool_analizarbankfeed, tool_buscarpatron
        # Cada tool debería tener un __module__ apuntando a autonomia.bank_feed_intelligence
        self.assertEqual(
            tool_analizarbankfeed.__module__,
            "autonomia.bank_feed_intelligence",
        )
        self.assertEqual(
            tool_buscarpatron.__module__,
            "autonomia.bank_feed_intelligence",
        )
```

- [ ] **Step 2: Ejecutar el test**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && python3 -m unittest tests.test_main_loop -v 2>&1 | tail -20
```

Expected: 9 tests anteriores + 2 nuevos = 11 tests, all OK

- [ ] **Step 3: Verificar suite completa**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && python3 -m unittest discover tests 2>&1 | grep -E "^Ran|^OK$"
```

Expected: `Ran 284 tests in ...` `OK`

---

## Task 7: Commit Fase 0 + Fase 1

**Files:** (all changes)

- [ ] **Step 1: Verificar git status**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && git status --short
```

Expected: 4 archivos nuevos (2 .py + 1 test) + 1 modificado (main.py + test_main_loop.py)

- [ ] **Step 2: Stage all + commit**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/.worktrees/refactor-main" && git add dexter/tools/ tests/test_tools_aggregator.py tests/test_main_loop.py main.py && git commit -m "feat(refactor): Fase 0+1 — dexter/tools/ infra + bank_feed piloto

Fase 0 — infraestructura:
- dexter/tools/_schema_utils.py: helpers make_schema/prop_str/...
- dexter/tools/__init__.py: registry agregador ALL_SCHEMAS+ALL_FUNCTIONS
- 11 tests nuevos (test_tools_aggregator.py): wiring, no-duplicates,
  callable, schema fields, description length

Fase 1 — bank_feed (4 tools) como piloto:
- dexter/tools/bank_feed.py: schemas + delegating functions para los
  4 stubs que existían en TOOLS pero NO tenían def tool_xxx (bug
  pre-existente, ahora arreglado).
- main.py: 4 re-exports al inicio del archivo, 100% backward compat.
- 2 tests nuevos en test_main_loop.py: verifica que from main
  import tool_analizarbankfeed etc. funciona y apunta a
  autonomia.bank_feed_intelligence.

Resultado:
- 4 stubs fantasma → 4 tools funcionales (de 24/43 a 28/43 wired)
- main.py solo creció en 4 líneas de re-exports (no removimos nada)
- 271 → 284 tests pasando (13 nuevos, 0 rotos)
- Patrón establecido para Fases 2-6 (6 fases restantes para migrar
  los 15 stubs + refactor main.py como shim completo)"
```

Expected: 1 commit on `refactor/main-2026`

---

## Self-Review

✅ **Spec coverage:** this plan covers:
- Spec section "Fase 0": infraestructura (Task 1, 3) + tests (Task 4) ✓
- Spec section "Fase 1": bank_feed (Task 2) + re-exports (Task 5) + tests (Task 6) ✓
- Spec criterion "271+ tests pasando": verified en Task 4.3, 5.4, 6.3 ✓
- Spec criterion "0 líneas removidas del comportamiento externo": only added, never removed ✓
- Spec criterion "+1 test de shim/wiring por fase": Task 4 (11) + Task 6 (2) ✓

✅ **Placeholder scan:** no TODOs, no "implement later", every step has exact code or command.

✅ **Type consistency:** `SCHEMA`, `FUNCTIONS`, `ALL_SCHEMAS`, `ALL_FUNCTIONS` consistently used. Re-export names (`tool_analizarbankfeed`) match the existing names in main.py `TOOLS` list.

---

## Next Phases (NOT in this plan, pero en spec)

- **Fase 2:** search + transactions (8 tools reales)
- **Fase 3:** reports + tokens + admin (9 tools reales)
- **Fase 4:** batch + reconciliation (6 tools reales)
- **Fase 5:** ocr + behavior + report_custom (7 stubs)
- **Fase 6:** api_explorer + journal + web_code (9 stubs)
- **Fase 7:** main.py como shim completo (reemplazar defs inline por re-exports)
- **Fase 8:** Context engineering (prompt modular + history compaction + tool_filter)
