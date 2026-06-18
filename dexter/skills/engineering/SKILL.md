# Dexter Engineering Manual
**Versión:** 1.0.0 | **Audiencia:** Senior Developers | **Última actualización:** Junio 2026

> Punto de partida obligatorio antes de implementar cualquier feature nueva en Dexter.
> Este documento es vinculante — no empezar código sin haberlo leído completo.

---

## 1. Filosofía de Arquitectura

Dexter sigue una **arquitectura de skills auto-descubribles** con separación estricta de responsabilidades. Cada feature nueva DEBE vivir en el módulo que le corresponde sin contaminar el core.

### 1.1 Jerarquía de Módulos (de más estable a más volátil)

```
main.py                          ← Core loop, auth, QBO client, wrappers de backward-compat (~6K líneas, encogiendo)
dexter/core/                     ← Infraestructura shared: memory, batch engine, qbo_client, disambiguator, console
dexter/skills/{skill}/            ← ⭐ LÓGICA DE DOMINIO — toda feature nueva va aquí
dexter/tools/{skill}.py           ← Schemas OpenAI + FUNCTIONS dict (declarativo, sin lógica)
tests/                            ← Espejo de la estructura, 1 test file por feature
```

### 1.2 Principio Fundamental

> **main.py NUNCA recibe lógica nueva.** Solo wrappers finos que delegan a skills vía lazy import.

Cada línea nueva de lógica de negocio en `main.py` es deuda técnica. El objetivo es que `main.py` siga encogiendo, no creciendo.

---

## 2. Anatomía de una Skill

Cada skill es un directorio con esta estructura:

```
dexter/skills/{nombre}/
├── __init__.py      ← Re-exporta desde dexter/tools/{nombre}.py (SCHEMA, FUNCTIONS, KEYWORDS)
├── SKILL.md         ← Documentación: propósito, cuándo usar, ejemplos
├── tools.py         ← Implementaciones reales de los tools (lógica de negocio)
└── fuzzy.py          ← (opcional) Módulos de soporte con lógica compartida
```

### 2.1 `__init__.py` — El Contrato

```python
"""dexter.skills.{nombre} — breve descripción."""
from dexter.tools.{nombre} import SCHEMA, FUNCTIONS, KEYWORDS
```

**Regla:** `__init__.py` NUNCA contiene lógica. Solo re-exports. El auto-descubrimiento (`dexter/skills/__init__.py::_discover_skills()`) lo escanea y extrae SCHEMA + FUNCTIONS + KEYWORDS para el registry global.

Si el skill tiene módulos de soporte (como `fuzzy.py`), se exportan desde aquí también.

### 2.2 `dexter/tools/{nombre}.py` — Los Schemas

```python
"""dexter.tools.{nombre} — N tools."""
from typing import Any, Dict, List
from main import tool_xxx, tool_yyy  # backward-compat shims

SCHEMA: List[Dict[str, Any]] = [
    {'type': 'function', 'function': {
        'name': 'nombre_del_tool',
        'description': 'Qué hace y cuándo usarlo.',
        'parameters': {
            'type': 'object',
            'properties': {
                'param1': {'type': 'string', 'description': '...'},
            },
            'required': ['param1']
        }
    }},
]

KEYWORDS: List[str] = ["keyword1", "keyword2", ...]
FUNCTIONS: Dict[str, Any] = {
    "nombre_del_tool": tool_xxx,
}
```

**Reglas:**
- SCHEMA es la interfaz que ve el LLM. Descripciones en español, claras, con ejemplos implícitos.
- FUNCTIONS mapea nombre → callable. El callable puede vivir en `tools.py` (implementación real) o en `main.py` (shim backward-compat).
- KEYWORDS son para `get_relevant_tools()` — sinónimos y palabras clave que activan esta skill.

### 2.3 `tools.py` — Las Implementaciones

```python
"""dexter.skills.{nombre}.tools — N tool implementations."""

# Imports: solo importar lo necesario. Usar lazy imports de main para evitar circular.
from dexter.skills.{nombre}.soporte import logica_compartida

def tool_mi_nuevo_tool(param1: str, param2: int = None) -> dict:
    """Tool: descripción breve."""
    # LÓGICA REAL AQUÍ
    resultado = logica_compartida(param1, param2)
    return {"success": True, "datos": resultado}
```

**Reglas:**
- Cada tool retorna un `dict` con al menos `success: bool`.
- Si el tool necesita `qbo_query` o `qbo_request`, se importan vía lazy import (ver sección 4.2).
- **NUNCA** hacer `from main import ...` a nivel de módulo en `tools.py` si el módulo se carga durante el auto-descubrimiento.
- Si el tool ya existe como shim en `main.py`, `tools.py` PUEDE re-implementarlo con la lógica real y `dexter/tools/{nombre}.py` apuntar FUNCTIONS al nuevo.

---

## 3. Procedimiento de Implementación (Checklist)

Seguir estos pasos en orden. No saltar ninguno.

### Paso 1: Determinar Dónde Va

| Tipo de feature | Destino |
|---|---|
| Nuevo tool de dominio contable | `dexter/skills/{dominio}/tools.py` |
| Nueva skill completa (múltiples tools) | `dexter/skills/{nueva_skill}/` |
| Lógica compartida entre skills | `dexter/core/` (si es infraestructura) o skill específico con `fuzzy.py`/`helpers.py` |
| Nuevo tipo de reporte | `dexter/skills/reports/` o `dexter/skills/report_custom/` |
| OCR / procesamiento de documentos | `dexter/skills/ocr/` |
| Búsqueda / matching | `dexter/skills/search/` (ya tiene `fuzzy.py` para matching) |
| Operaciones batch | `dexter/skills/batch/` + `dexter/core/batch/` |

### Paso 2: Crear los Schemas

1. Crear/editar `dexter/tools/{skill}.py` con el nuevo schema en `SCHEMA`
2. Agregar el callable en `FUNCTIONS`
3. Agregar keywords relevantes en `KEYWORDS`
4. Verificar que el nombre del tool no colisiona con uno existente (`grep -r "name.*tool_nuevo" dexter/tools/`)

### Paso 3: Implementar la Lógica

1. La lógica real va en `dexter/skills/{skill}/tools.py`
2. Si es compleja (>30 líneas), extraer a un módulo de soporte: `dexter/skills/{skill}/helpers.py` o `fuzzy.py`
3. Usar lazy imports para dependencias de `main.py` (ver sección 4.2)
4. Si la feature requiere cache, usar variables de módulo (con `invalidate_*()` públicos)

### Paso 4: El Wrapper en main.py (solo si es necesario)

Solo agregar a main.py si:
- La función DEBE ser accesible como `from main import mi_funcion` (backward compat o uso desde múltiples skills)
- En ese caso: wrapper fino de 3-5 líneas con lazy import:

```python
def mi_funcion(args):
    """Delega a dexter.skills.{skill}.{modulo} (HIGH-N)."""
    from dexter.skills.{skill}.{modulo} import mi_funcion as _impl
    return _impl(args)
```

### Paso 5: Tests

1. Crear `tests/test_{feature}.py`
2. Estructura: `unittest.TestCase`, mocking de `qbo_query`/`qbo_request`, sin network
3. Probar: happy path, edge cases, cache invalidation, fuzzy thresholds, integración con Disambiguator
4. Correr: `python3 -m unittest tests.test_{feature} -v`
5. Correr suite completa: `python3 -m unittest discover -s tests -p "test_*.py" -v`
6. Verificar: 0 nuevas fallas. Las 2 fallas preexistentes (`test_low4_chart_schema`) son flaky conocidas.

### Paso 6: Documentar

1. Actualizar `dexter/skills/{skill}/SKILL.md` con el nuevo tool
2. Si es una skill nueva, crear `SKILL.md` completo
3. Agregar `# HIGH-N:` en el código y en el mensaje de commit para trazabilidad

---

## 4. Reglas de Oro — No Violar

### 4.1 NUNCA Lógica Nueva en main.py

```python
# ❌ PROHIBIDO — main.py no recibe implementaciones nuevas
def find_similar_customers(name, threshold=0.85):  # 50 líneas en main.py
    ...

# ✅ CORRECTO — lógica en skill, wrapper fino en main
# dexter/skills/search/fuzzy.py:
def find_similar_customers(name, threshold=0.85):
    ...

# main.py (wrapper):
def find_similar_customers(name, threshold=None, max_results=5):
    from dexter.skills.search.fuzzy import find_similar_customers as _fn
    return _fn(name, threshold=threshold, max_results=max_results)
```

### 4.2 NUNCA Importar de main a Nivel de Módulo en Skills

```python
# ❌ PROHIBIDO — causa circular import porque _discover_skills() se dispara
# durante la carga de main.py y los skills intentan importar de main a medio cargar
from main import qbo_query, qbo_request

# ✅ CORRECTO — lazy import dentro de la función
def _qbo():
    from main import qbo_query
    return qbo_query
```

Si la función se llama muchas veces, cachear la referencia:

```python
_qbo_query_cache = None

def _get_qbo_query():
    global _qbo_query_cache
    if _qbo_query_cache is None:
        from main import qbo_query
        _qbo_query_cache = qbo_query
    return _qbo_query_cache
```

### 4.3 Mantener Backward Compat

Cualquier función que antes se importaba como `from main import tool_xxx` debe seguir funcionando. Si movés la implementación a un skill, dejá un wrapper en main.py.

### 4.4 Tests Antes de Commit

Nunca commitear sin correr la suite completa. 705 tests deben pasar (o 703 si las 2 flaky). Si algo falla, arreglalo antes de commitear.

### 4.5 Schema Drift = Bug

El nombre del tool en `SCHEMA` (en `dexter/tools/{skill}.py`) debe coincidir exactamente con la key en `FUNCTIONS` y con el nombre de la función en `tools.py`. Un mismatch causa que el LLM llame un tool que no existe.

---

## 5. Caso de Estudio: HIGH-1 (Fuzzy Matching ≥85%)

Implementación real siguiendo este manual. Resumen de cómo se hizo:

### 5.1 Dónde Va
Feature: búsqueda fuzzy de clientes/vendors con umbral 85%.
Dominio: **search** → `dexter/skills/search/`

### 5.2 Archivos Creados/Modificados

| Archivo | Rol |
|---|---|
| `dexter/skills/search/fuzzy.py` | **CREADO** — ~150 líneas con toda la lógica |
| `dexter/skills/search/__init__.py` | **EDITADO** — exporta funciones fuzzy |
| `dexter/skills/search/tools.py` | **EDITADO** — importa de fuzzy.py en vez de main.py |
| `main.py` | **EDITADO** — ~90 líneas removidas, wrappers finos con lazy import |
| `dexter/core/batch/disambiguator.py` | **EDITADO** — `ask_fuzzy_customer_match()` |
| `dexter/core/batch/deposits.py` | **EDITADO** — detecta `_fuzzy_score` y rutea |
| `tests/test_fuzzy_customer_match.py` | **CREADO** — 13 tests |

### 5.3 Lecciones Aprendidas

1. **Intento #1 (fallido):** Puse la lógica inline en `main.py` (~90 líneas). Violaba la regla 4.1.
2. **Intento #2 (fallido):** Moví a `fuzzy.py` pero hice `from dexter.skills.search.fuzzy import ...` a nivel de módulo en `main.py`. Causó circular import (regla 4.2).
3. **Intento #3 (correcto):** `fuzzy.py` con lazy import de `_qbo()`, `main.py` con wrappers que hacen lazy import en cada llamada. 705 tests, 0 fallas.

### 5.4 El Wrapper Correcto en main.py

```python
def search_customer(search_term, exact=False, fuzzy_fallback=True):
    log_operation("searches")
    from dexter.skills.search.fuzzy import search_customer as _impl
    return _impl(search_term, exact=exact, fuzzy_fallback=fuzzy_fallback)
```

3 líneas de wrapper. La lógica real (150 líneas) en `fuzzy.py`. `log_operation` se preserva.

---

## 6. Anti-Patrones — Lo Que NO Se Debe Hacer

| Anti-Patrón | Por qué es malo | Corrección |
|---|---|---|
| Nueva función de 50 líneas en `main.py` | Viola separación de concerns, hace `main.py` inmantenible | Mover a `dexter/skills/{dominio}/` |
| `from main import algo` a nivel de módulo en un skill | Circular import → `_discover_skills()` explota | Lazy import dentro de la función |
| Tool sin test | Regresión silenciosa en el futuro | `tests/test_{feature}.py` obligatorio |
| Schema en `dexter/tools/` sin función en `FUNCTIONS` | LLM llama tool fantasma → error 500 | Verificar que `FUNCTIONS[name]` existe |
| Cache sin invalidación | Datos stale después de crear/modificar entidades | `invalidate_*_cache()` llamado desde los tools de creación |
| Lógica de dominio en `dexter/core/` | `core/` es infraestructura, no negocio | `core/` solo para batch engine, qbo_client, memory, disambiguator |

---

## 7. Comandos de Verificación

```bash
# Test de la feature nueva
python3 -m unittest tests.test_{feature} -v

# Suite de tests del skill
python3 -m unittest discover -s tests -p "test_{skill}*.py" -v

# Suite completa — DEBE PASAR antes de commit
python3 -m unittest discover -s tests -p "test_*.py" -v

# Verificar que no hay schemas huérfanos
python3 -c "
import dexter.skills as s
s._discover_skills()
for name, fn in s.ALL_FUNCTIONS.items():
    if not callable(fn):
        print(f'HUÉRFANO: {name} → {fn}')
print('OK - 0 huérfanos')
"

# Verificar que main.py no creció (comparar con último tag)
git diff $(git describe --tags --abbrev=0) -- main.py | grep '^+' | wc -l
```

---

## 8. Glosario Rápido

| Término | Significado |
|---|---|
| **Skill** | Módulo auto-descubrible en `dexter/skills/{nombre}/` que agrupa tools relacionados |
| **Schema** | Definición OpenAI de un tool (nombre, descripción, parámetros) en `dexter/tools/` |
| **FUNCTIONS** | Dict que mapea nombre de tool → callable implementación |
| **Shim / Wrapper** | Función en `main.py` que solo delega a un skill (backward compat) |
| **Lazy import** | `from x import y` dentro del cuerpo de una función, no a nivel de módulo |
| **Disambiguator** | Componente interactivo que pregunta al usuario cuando hay ambigüedad |
| **Batch Engine** | State machine para procesamiento por lotes (PENDING → VALIDATED → EXECUTED) |
| **HIGH-N** | Tag en comentarios y commits para trazabilidad de features (ej: `# HIGH-1: fuzzy matching`) |

---

## QBO MCP Backend (HIGH-3)

Dexter soporta dos backends QBO. Para usar el oficial de Intuit:

```bash
# 1. Instalar el MCP server (una sola vez)
bash install.sh

# 2. Activar el backend
export QB_BACKEND=mcp

# 3. Iniciar Dexter normalmente
python3 main.py

# 4. Volver al backend nativo si algo falla
export QB_BACKEND=native
```

**Arquitectura:**
```
Dexter tool → QBOAdapter → MCPBridge (JSON-RPC) → Intuit MCP (Node.js) → QBO API
```

`QBOAdapter` implementa `QBOClientProtocol`, así que el batch engine y el reconciliation tagger
funcionan idénticamente con ambos backends. Si el MCP no está instalado, Dexter hace fallback
automático a native sin error.

**Ventajas del backend MCP:**
- 144 tools mantenidos por Intuit (dueño de QBO)
- 396 tests, 100% code coverage
- Menos bugs de formato API (Entity, SyncToken, minorversions)
- Nuevos endpoints agregados por Intuit se heredan automáticamente

*Este manual reemplaza cualquier procedimiento anterior. Cualquier excepción debe discutirse y documentarse aquí.*
