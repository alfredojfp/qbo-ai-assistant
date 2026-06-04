# dexter/tools/ — Registry de Function Tools

> **Versión:** 4.0.0-dev
> **Última actualización:** 2026-06-04 (46 tools)
> **Total:** 46 function tools en 14 módulos de dominio

## 📋 Overview

`dexter/tools/` es la **capa de abstracción sobre los function tools** que Dexter expone al LLM. Reemplaza el monolito de `main.py` (3,608 líneas) por una **registry modular orientada a dominios** donde cada módulo declara:

- `SCHEMA`: schemas en formato OpenAI (`{type:"function", function:{name, description, parameters}}`)
- `FUNCTIONS`: dict `name → callable` para function calling dispatch
- `KEYWORDS`: lista de keywords que activan el módulo (usado por `get_relevant_tools()`)

El registry agregador (`__init__.py`) itera los 14 módulos y construye:
- `ALL_SCHEMAS`: lista de 46 schemas para inyectar al LLM
- `ALL_FUNCTIONS`: dict de 46 funciones para dispatch
- `KEYWORDS_BY_MODULE`: dict módulo → keywords (routing metadata)

## 🗂️ Estructura

```
dexter/tools/
├── __init__.py             # Registry agregador (66 líneas)
├── _schema_utils.py        # Helpers: make_schema(), prop_str/num/bool/list
│
├── bank_feed.py            # 5 tools — clasificación bank feed + CSV
├── search.py               # 4 tools — buscar cliente/vendor/cuenta/item
├── transactions.py         # 5 tools — crear invoice/bill/deposito/pago/cliente
├── reports.py              # 5 tools — P&L, BS, guardar/cargar/listar
├── tokens.py               # 2 tools — estadísticas + informe Excel
├── admin.py                # 4 tools — refrescar chart, gestionar empresas, ver/limpiar log errores
├── batch.py                # 3 tools — CSV depósitos, template, lote
├── reconciliation.py       # 3 tools — BNK-RECON tag-only
├── ocr.py                  # 1 tool  — procesar lote de PDFs
├── behavior.py             # 4 tools — aprender, sugerencias, correcciones
├── report_custom.py        # 2 tools — reportes dinámicos, parsear fechas
├── api_explorer.py         # 5 tools — 26 endpoints QBO + web search
├── journal.py              # 2 tools — journal entry, transferencia
└── web_code.py             # 1 tool  — ejecutar Python
```

**Total:** 16 archivos (14 módulos + 1 infra + 1 `__init__.py`).

## 🧩 Distribución de Tools

| Módulo | # | Dominio | Casos de uso |
|---|---:|---|---|
| `bank_feed` | 5 | Clasificación bancaria | Analizar/registrar clasificaciones, CSV con splits |
| `search` | 4 | Búsqueda en QBO | Fuzzy match de clientes, vendors, cuentas, items |
| `transactions` | 4 | Crear transacciones | Invoice, bill, deposit, payment |
| `reports` | 5 | Reportes predefinidos | P&L, Balance Sheet, guardar/cargar configs |
| `tokens` | 2 | Tracking de costos | Estadísticas por período, Excel de informe |
| `admin` | 4 | Administración | Refrescar chart, multi-empresa, ver/limpiar log errores |
| `batch` | 3 | Procesamiento en lote | CSV depósitos con state machine |
| `reconciliation` | 3 | Reconciliación | BNK-RECON tag-only (no crea txns) |
| `ocr` | 1 | OCR de PDFs | Extraer bills de carpeta `Pending bills/` |
| `behavior` | 4 | Learning engine | Aprender de correcciones, sugerencias |
| `report_custom` | 2 | Reportes dinámicos | "ventas del último trimestre" |
| `api_explorer` | 5 | Exploración QBO | 26 endpoints catalogados, web search, docs QBO |
| `journal` | 2 | Asientos contables | Crear journal entry, transferencia |
| `web_code` | 1 | Ejecución Python | Análisis ad-hoc, cálculos |
| **TOTAL** | **43** | | |

## 🔌 API Pública

### Importar el registry completo

```python
from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS, KEYWORDS_BY_MODULE

# Para inyectar al LLM (formato OpenAI)
response = openrouter.chat(
    messages=[...],
    tools=ALL_SCHEMAS,  # 43 schemas
)

# Para dispatch del function calling
function_name = response.choices[0].message.tool_calls[0].function.name
result = ALL_FUNCTIONS[function_name](**json.loads(arguments))

# Para routing data-driven (data-driven context engineering)
relevant_tools = get_relevant_tools(user_message)
```

### Importar un módulo específico

```python
from dexter.tools.bank_feed import SCHEMA, FUNCTIONS, KEYWORDS

# SCHEMA tiene 5 schemas (los de bank_feed)
# FUNCTIONS tiene 5 funciones callable
# KEYWORDS = ["clasificar", "bank", "banco", "feed"]
```

## 🛠️ Helpers de Schema

`_schema_utils.py` reduce el boilerplate de declarar schemas:

```python
from dexter.tools._schema_utils import make_schema, prop_str, prop_num, prop_list

# Antes (verbose):
schema = {
    "type": "function",
    "function": {
        "name": "mi_tool",
        "description": "Hace algo",
        "parameters": {
            "type": "object",
            "properties": {
                "nombre": {"type": "string", "description": "..."},
                "cantidad": {"type": "number", "description": "..."},
            },
            "required": ["nombre", "cantidad"],
        },
    },
}

# Ahora (concisos):
schema = make_schema(
    name="mi_tool",
    description="Hace algo",
    properties={
        "nombre": prop_str("..."),
        "cantidad": prop_num("..."),
    },
    required=["nombre", "cantidad"],
)
```

## 🔄 Data-Driven Tool Routing

Cada módulo declara `KEYWORDS` para que `get_relevant_tools()` sepa cuándo activar sus tools:

```python
# dexter/tools/bank_feed.py
KEYWORDS: List[str] = ["clasificar", "bank", "banco", "feed"]
```

```python
# main.py — get_relevant_tools() simplificado (data-driven):
def get_relevant_tools(user_message: str) -> list:
    from dexter.tools import KEYWORDS_BY_MODULE
    import dexter.tools as dexter_tools

    msg = user_message.lower()
    relevant_names = set()

    for module_name, keywords in KEYWORDS_BY_MODULE.items():
        module = getattr(dexter_tools, module_name.split(".")[-1], None)
        if module and any(kw in msg for kw in keywords):
            relevant_names.update(module.FUNCTIONS.keys())

    if not relevant_names:  # safe defaults
        relevant_names.update(["buscar_cliente", "buscar_cuenta", "generar_reporte_pl"])

    return [t for t in TOOLS if t["function"]["name"] in relevant_names]
```

**Beneficio:** agregar un tool nuevo requiere solo (1) declararlo en su módulo, (2) declarar sus keywords. El routing se actualiza automáticamente.

## ↔️ Backward Compatibility

`main.py` sigue siendo la API legacy. Los siguientes imports siguen funcionando:

```python
# Tool aliases Fase 1 (4 bank_feed intelligence)
from main import (
    tool_analizarbankfeed,
    tool_registrarclasificacion,
    tool_estadisticasclasificacion,
    tool_buscarpatron,
)

# Core API (sin cambios)
from main import TOOLS, TOOL_FUNCTIONS, main_loop, call_llm
from main import SYSTEM_PROMPT, get_relevant_tools, build_conversation_context
from main import search_customer, create_invoice, generate_pl_report  # funciones core

# Function calling dispatch (sin cambios)
result = TOOL_FUNCTIONS["ejecutarcodigo"](code="print(1+1)")
```

Además, `main.py` expone aliases al registry:
```python
from main import ALL_SCHEMAS_DEXTER, ALL_FUNCTIONS_DEXTER
# Equivalentes a dexter.tools.ALL_SCHEMAS, ALL_FUNCTIONS
```

## 🧪 Testing

`tests/test_tools_aggregator.py` valida la integridad del registry:

- `test_count_is_43` — 43/43 schemas y funciones
- `test_no_duplicate_names` — sin colisiones
- `test_every_schema_has_matching_function` — 1:1 schema↔function
- `test_each_domain_has_expected_count` — los 14 dominios tienen su count esperado
- `test_descriptions_are_substantive` — cada description > 30 chars
- `test_each_function_is_callable` — todas las funciones son callable

**Total tests del agregador:** 14 (11 originales + 3 parametrizados para los 14 dominios).

## 📜 Changelog

- **2026-06-04** — Creación del registry (Fases 0-7 del refactor main.py)
  - 14 módulos de dominio
  - Registry agregador con data-driven routing
  - Backward compat: 0 líneas removidas de main.py
  - 287/287 tests pasando

---

**Mantenedor:** Alfredo
**Relacionado:** `docs/CHANGELOG.md` (entrada Unreleased 2026-06-04)
