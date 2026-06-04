# 🏗️ Brief Arquitectónico v4.0: Dexter — Motor de Automatización Batch

**Fecha:** 2026-06-03
**Versión del proyecto al momento del brief:** v3.7.0
**Estado:** Diseño aprobado para implementación incremental
**Alcance:** Automatización batch + Skills + CLI + Memoria (sin RAG)

---

## 🎯 Resumen Ejecutivo (TL;DR)

| # | Característica | Estado hoy | Esfuerzo v4.0 | Valor |
|---|---|---|---|---|
| 1 | **Motor de Automatización Batch** | ❌ Loop simple con `process_deposits_csv` (main.py:975) | 5 sprints | ⭐⭐⭐⭐⭐ |
| 2 | **Arquitectura basada en Skills** | ❌ 21 tools monolíticas en `main.py` | Paralelo a Sprint 1-4 | ⭐⭐⭐⭐ |
| 3 | **Interacción Conversacional (Intent Parsing)** | ⚠️ Detección por keywords (main.py:2807) | Sprint 1-2 | ⭐⭐⭐⭐ |
| 4 | **CLI Avanzada estilo Claude Code** | ❌ `input()` + `print()` (main.py:2891) | Sprint 5 | ⭐⭐⭐ |
| 5 | **Memoria Persistente (audit + prefs)** | ❌ JSON files + estado en memoria | Sprint 1 + 4 | ⭐⭐⭐ |

**Pivote estratégico:** Se descartó RAG/NotebookLM por no ser necesario. El proyecto saltará entre empresas y el foco es automatización de procesos batch, no knowledge management empresarial.

---

## 1️⃣ Evaluación de Factibilidad (5 puntos)

### 1.1 Motor de Automatización Batch (PRIMARIO)

**Factibilidad: ✅ ALTA — Esfuerzo alto — Valor crítico**

El estado actual es un loop simple (`process_deposits_csv` en main.py:975-1036) que falla silenciosamente cuando un cliente no existe. Lo que se necesita es un **workflow engine** con fases explícitas:

```
INPUT → VALIDATE → DISAMBIGUATE → DRY-RUN → EXECUTE → AUDIT
```

| Componente | Estado hoy | v4.0 |
|---|---|---|
| Parsers (CSV / NL) | Solo CSV hardcoded | CSV + NL (1 llamada al LLM para extraer estructura) |
| Validación QBO | `search_customer` con fuzzy 60% | Igual + validación de integridad (montos, fechas, cuentas) |
| Disambiguation | ❌ No existe | Interactiva pregunta-por-pregunta |
| Dry-run | ❌ No existe | Obligatorio antes de ejecutar |
| Ejecución atómica-ish | Best-effort, sin rollback | Por item con checkpoint, log por item |
| Audit | ❌ No existe (errores solo en variable) | SQLite con `batches` + `batch_items` tables |
| Re-ejecutable | ❌ No | Sí: "reintentá los que fallaron" |

**5 operaciones batch que el motor debe soportar:**

| Skill | Input típico | Casos de ambigüedad |
|---|---|---|
| `skill_batch_deposits` | CSV o NL con N clientes | Cliente no existe, cuenta ambigua |
| `skill_batch_bills` | CSV/PDF con N facturas de proveedor | Vendor no existe, account no existe |
| `skill_batch_recon` | CSV banco | Match ambiguo, transacción sin par |
| `skill_batch_reclassify` | CSV con `txn_id, new_account` | Cuenta destino ambigua |
| `skill_scheduled_reports` | NL: "P&L cada 1° del mes" | Hora, output (local/email) |

### 1.2 Arquitectura basada en Skills

**Factibilidad: ✅ ALTA — Esfuerzo medio**

Hoy hay 21 funciones `tool_*` en `main.py` filtradas por keywords. Una **Skill** agrupa tools cohesionadas y solo se inyecta la skill activa:

```python
class Skill:
    name: str
    description: str      # Para el LLM entienda cuándo usar esta skill
    tools: List[Callable] # Tools que pertenecen a esta skill
    examples: List[str]   # Few-shot para clasificar intención
```

**Ahorro esperado de tokens:** de 21 tools (~5KB de schema) a 1-2 skills activas (~500 bytes) por turno.

### 1.3 Interacción Conversacional (Intent Parsing)

**Factibilidad: ✅ ALTA — Sin latencia extra**

Hoy: `if "clasificar" in msg.lower()` (main.py:2813). Falla con frases coloquiales.

**Decisión de diseño: NO agregar llamada extra al LLM.** En vez de eso:

- **Opción A (inmediata):** Mejorar `SYSTEM_PROMPT` para que el LLM clasifique solo como primer paso. Sin latencia.
- **Opción B (v4.0):** Embedding local pequeño (all-MiniLM-L6-v2, 80MB) → clasificador cosine. +10ms. Solo si A no basta.

El usuario quiere **lenguaje natural, fluido, coloquial**, sin keywords rígidas. La Opción A resuelve el 80% sin cambios de arquitectura.

### 1.4 CLI Avanzada (estilo Claude Code / Cursor)

**Factibilidad: ✅ ALTA — Esfuerzo bajo (Sprint 5)**

Loop actual: `input()` + `print()` (main.py:2889-2913). Reemplazable sin tocar lógica de negocio.

| Feature | Librería | Esfuerzo |
|---|---|---|
| Autocompletado, historial | `prompt_toolkit` | 1 día |
| Tablas/paneles | `rich` | 1 día |
| Multi-linea, syntax highlight | `prompt_toolkit` | 0.5 día |
| Streaming de tokens | `httpx` con SSE | 0.5 día |

**No se recomienda `textual`** (TUI VSCode-like) para v4.0: scope creep.

### 1.5 Memoria Persistente (NO RAG)

**Factibilidad: ✅ ALTA — Esfuerzo bajo**

Lo que SÍ se guarda en SQLite (`~/.dexter/dexter.db`):

| Tabla | Qué guarda | Riesgo |
|---|---|---|
| `preferences` | Idioma, empresa default, formato fechas | Bajo |
| `batches` | Historial de batches ejecutados | Bajo |
| `batch_items` | Cada item con status, qbo_txn_id, error | Bajo |
| `scheduled_reports` | Cron expressions, próxima ejecución | Bajo |
| `user_corrections` | "Cuando corrijo X, el agente aprende Y" | **MEDIO** ⚠️ |

**Lo que NO se guarda** (eliminado del scope): knowledge base vectorial, embeddings de documentos, retrieval semántico de SOPs.

**⚠️ Punto crítico de compliance:** En contabilidad, la "memoria de aprendizaje" del usuario debe tener **validación humana antes de ejecutar**. Toda corrección nueva requiere confirmación explícita.

---

## 2️⃣ Librerías Recomendadas

### Stack final

```text
# CLI
prompt_toolkit>=3.0.43
rich>=13.7

# Validación y modelos
pydantic>=2.5

# HTTP moderno (opcional, para streaming)
httpx>=0.25

# Scheduling (Sprint 4)
schedule>=1.2

# Stack actual (mantener)
google-genai>=1.0.0
intuitlib>=1.3.0
requests>=2.28.0
pdf2image>=1.16.0
Pillow>=10.0.0
python-dotenv>=1.0.0

# Testing
pytest>=7.4
pytest-asyncio>=23.0
```

### Lo que **NO** se agrega

- ❌ ChromaDB (sin vector store)
- ❌ sentence-transformers (sin embeddings)
- ❌ LangChain / LlamaIndex (overkill, oculta control)
- ❌ anything-llm (sin RAG framework)

**Reducción de dependencias vs propuesta inicial:** 4 librerías menos. ~80MB menos en disco. Menos superficie de seguridad.

---

## 3️⃣ Propuesta de Refactorización

### Árbol v4.0 final

```
dexter/
├── __init__.py
├── __main__.py                      ← Entry point (`python -m dexter`)
│
├── core/                            ← Núcleo del agente
│   ├── agent.py                     ← Clase Agent (orquesta skills + batch)
│   ├── intent_router.py             ← Clasificador de intención (s/ keywords)
│   ├── skill_registry.py            ← Registro dinámico de skills
│   ├── llm_client.py                ← Wrapper LLM (DeepSeek/Llama, con streaming)
│   │
│   └── batch/                       ← 🆕 CORAZÓN DEL V4.0: motor batch
│       ├── __init__.py
│       ├── engine.py                ← BatchEngine (orquesta las 5 fases)
│       ├── plan.py                  ← BatchPlan, BatchItem, Ambiguity
│       ├── result.py                ← BatchResult (éxito/error por item)
│       ├── disambiguator.py         ← InteractiveDisambiguator (pregunta x item)
│       ├── dryrun.py                ← DryRunReport (render con rich)
│       ├── audit.py                 ← AuditLog (SQLite: batches, batch_items)
│       └── parsers/
│           ├── csv_parser.py        ← CSV → BatchPlan
│           └── nl_parser.py         ← NL → BatchPlan (1 call al LLM)
│
├── skills/                          ← Skills modulares
│   ├── __init__.py
│   ├── base.py                      ← Clase Skill abstracta
│   ├── skill_search.py              ← buscar_cliente, vendor, cuenta, item
│   ├── skill_transactions.py        ← crear_invoice, bill, deposit, payment
│   ├── skill_reports.py             ← P&L, balance, custom
│   ├── skill_multi_company.py       ← gestionar_empresas
│   ├── skill_ocr.py                 ← procesar PDFs, Gemini
│   ├── skill_bank_feed.py           ← matching, clasificación
│   ├── skill_autonomy.py            ← web search, API explorer, code exec
│   ├── skill_user_insights.py       ← aprender, sugerir, clasificar
│   │
│   └── batch/                       ← 🆕 5 skills de automatización
│       ├── __init__.py
│       ├── skill_batch_deposits.py
│       ├── skill_batch_bills.py
│       ├── skill_batch_recon.py
│       ├── skill_batch_reclassify.py
│       └── skill_scheduled_reports.py
│
├── cli/                             ← Capa de presentación
│   ├── __init__.py
│   ├── app.py                       ← App de prompt_toolkit
│   ├── completer.py                 ← Autocompletado contextual (/batch, /skills)
│   ├── renderer.py                  ← Renderizado con rich
│   └── commands.py                  ← Comandos rápidos
│
├── integrations/                    ← Capa externa
│   ├── quickbooks.py                ← OAuth + QBO API (extraído de main.py)
│   ├── gemini_ocr.py                ← De ocr_bills.py
│   └── token_tracker.py             ← De main.py
│
└── memory/                          ← Memoria persistente
    ├── __init__.py
    ├── preferences.py               ← SQLite: idioma, default company
    └── corrections.py               ← SQLite: user_corrections (con validación)

data/
├── dexter.db                        ← SQLite (NUEVO: batches, prefs, schedules)
├── companies/                       ← Ya existe
├── chart_of_accounts.json           ← Ya existe
└── saved_reports.json               ← Ya existe

tests/                               ← NUEVO
├── test_batch_engine.py
├── test_batch_deposits.py
├── test_intent_router.py
├── test_skill_registry.py
├── test_audit.py
└── test_cli.py

main.py                              ← Legacy shim (1 línea)
```

### Estrategia de migración (sin romper v3.7)

**Regla de oro:** En cada fase, `python main.py` debe seguir funcionando idéntico. Las nuevas skills viven en `dexter/` y se activan cuando se invocan explícitamente.

```
Fase 0 (Sprint 1): crear dexter/ vacío. main.py intacto. Tests del nuevo motor.
Fase 1 (Sprint 2): skill_batch_deposits opcional. main.py llama al nuevo si existe.
Fase 2 (Sprint 3): migrar las otras 4 batch skills.
Fase 3 (Sprint 4): mover tools básicas de main.py a skills/.
Fase 4 (Sprint 5): main.py = 1 línea (shim). CLI nueva.
```

### Diseño técnico clave del motor batch

#### 3.1 Modelo de datos: BatchPlan

```python
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class BatchOperation(Enum):
    DEPOSITS = "deposits"
    BILLS = "bills"
    RECONCILIATION = "reconciliation"
    RECLASSIFY = "reclassify"
    SCHEDULED_REPORT = "scheduled_report"

@dataclass
class BatchItem:
    id: str                          # UUID del item
    intent: dict                     # Datos crudos: {customer, amount, ...}
    qbo_resolution: dict = field(default_factory=dict)
    status: str = "pending"          # pending | dryrun_ok | confirmed | done | error | skipped
    error: Optional[str] = None
    qbo_txn_id: Optional[str] = None
    user_decisions: dict = field(default_factory=dict)

@dataclass
class BatchPlan:
    operation: BatchOperation
    company_id: str
    items: List[BatchItem]
    ambiguities: List['Ambiguity']
    metadata: dict = field(default_factory=dict)

@dataclass
class Ambiguity:
    item_id: str
    field: str                       # "customer", "from_account", etc.
    attempted_value: str
    candidates: List[dict]
    question: str
```

#### 3.2 Patrón "plan then execute" para disambiguation

El truco crítico: **separar `plan` de `execute` en dos tools** para que el LLM pueda pausar y preguntar.

```python
def tool_plan_batch_deposits(csv_path=None, description=None) -> dict:
    """Planifica. NO toca QBO. Retorna ambiguidades y dry-run."""
    items = parse_csv_deposits(csv_path) if csv_path else parse_nl_deposits(description)
    plan = BatchEngine.validate(items, operation=DEPOSITS, company=active_company)
    audit.save_plan(plan)
    return {
        "plan_id": plan.id,
        "summary": f"{len(plan.items)} deposits, ${sum(...)}",
        "ambiguities": [a.to_dict() for a in plan.ambiguities],
        "dryrun_text": DryRunReport(plan).render_text()
    }

def tool_execute_batch_deposits(plan_id, decisions) -> dict:
    """Ejecuta un batch previamente planificado."""
    plan = audit.load_plan(plan_id)
    BatchEngine.apply_user_decisions(plan, decisions)
    if not plan.all_resolved():
        return {"error": "Aún hay ambigüedades", "ambiguities": [...]}
    return BatchEngine.execute(plan)
```

#### 3.3 Schema SQLite para audit

```sql
CREATE TABLE batches (
    id TEXT PRIMARY KEY,           -- bd-2026-06-03-001
    operation TEXT NOT NULL,
    company_id TEXT NOT NULL,
    company_name TEXT,
    created_at TIMESTAMP,
    executed_at TIMESTAMP,
    status TEXT,                    -- planned | dryrun_ok | executed | failed
    total_items INTEGER,
    success_count INTEGER,
    error_count INTEGER,
    plan_json TEXT
);

CREATE TABLE batch_items (
    id TEXT PRIMARY KEY,
    batch_id TEXT REFERENCES batches(id),
    intent_json TEXT,
    qbo_resolution_json TEXT,
    status TEXT,
    error TEXT,
    qbo_txn_id TEXT,
    decided_at TIMESTAMP
);

CREATE TABLE scheduled_reports (
    id TEXT PRIMARY KEY,
    cron_expr TEXT,                -- "0 8 1 * *" = día 1 de cada mes a las 8am
    report_type TEXT,
    params_json TEXT,
    next_run TIMESTAMP,
    last_run TIMESTAMP
);
```

---

## 4️⃣ Riesgos y Consideraciones

### 🚨 Riesgos críticos

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| 1 | **Batch a media ejecución interrumpe y deja datos inconsistentes** | Alta | **ALTO** | Audit log por item + retry de fallidos; nada es "todo o nada" porque QBO no tiene transactions nativas |
| 2 | **Cliente creado "al vuelo" en disambiguation queda con datos incorrectos** | Alta | Alto | Disambiguation pide confirmación caso por caso; nunca crear en silencio |
| 3 | **Dry-run saltado por bug o race condition** | Baja | **CRÍTICO** | Dry-run es precondición en el código, no configurable; tests cubren el path |
| 4 | **CSV mal formado (montos con coma decimal, encoding raro) rompe el batch entero** | Alta | Medio | Parser robusto con `pandas` + detección de encoding + validación por fila |
| 5 | **Concurrency: dos batches al mismo tiempo contra la misma empresa** | Baja | Alto | Lock por `company_id` en SQLite; un batch a la vez por empresa |
| 6 | **user_corrections "aprende" un mapeo contable incorrecto** | Media | **CRÍTICO** | Validación humana obligatoria + dry-run preview de cualquier corrección nueva antes de aplicar |
| 7 | **Scheduler de reportes se cae al cerrar la terminal** | Alta | Bajo | Decisión Sprint 4: ¿in-process o systemd? |
| 8 | **Refactor de 3,000 líneas rompe v3.7 silenciosamente** | Media | Alto | Shims + tests de regresión de las funciones existentes |

### ⚠️ Consideraciones de diseño (no negociables)

- **Idempotencia donde sea posible**: cada item debe ser re-ejecutable sin duplicar. Si el LLM ya creó el deposit, retry no lo crea de nuevo.
- **Auditabilidad**: cada acción de QBO debe loguearse con `qbo_txn_id` para poder reversar manualmente si algo sale mal.
- **Límite de tamaño por batch**: 500 items por batch. Más que eso, dividir. Previene timeouts y facilita retry granular.
- **Timeout por item**: 30s máximo por item. Si un item tarda más, se marca como error y se continúa.
- **Privacidad**: los datos nunca salen de tu máquina (sin APIs de embeddings, sin RAG cloud). SQLite local.

### Comparación antes/después: el ejemplo del deposit CSV

**Antes** (main.py:975):
```python
for idx, row in df.iterrows():
    customers = search_customer(row["customer_name"])
    if not customers:
        results["errors"].append(f"Fila {idx+1}: Cliente '{row['customer_name']}' no encontrado")
        continue  # ❌ Falla silenciosa
    # ... crea deposit sin confirmar nada
```

**Después** (skill_batch_deposits):
```
1. Parse (CSV o NL)
2. Validate contra QBO
3. Si hay ambigüedades → pregunta interactivamente POR CADA UNA
4. Dry-run visual con rich
5. Espera confirmación explícita
6. Execute con audit log por item
7. Reporte: ✅/❌ por cada item, con qbo_txn_id
8. Re-ejecutable: "reintentá los que fallaron"
```

---

## 5️⃣ Hoja de Ruta: Por dónde arrancar

### 🏆 Sprint 1 — El motor batch skeleton (5 días)

**Razón:** El motor batch es el corazón del v4.0. Sin él, las 5 skills no existen. Las demás features (CLI, Skills, Intent Parsing) se montan encima.

**Entregables:**
- [ ] `dexter/core/batch/{engine,plan,result,disambiguator,dryrun,audit}.py`
- [ ] SQLite con tablas `batches`, `batch_items`, `scheduled_reports`, `preferences`, `user_corrections`
- [ ] 15+ tests unitarios cubriendo `BatchEngine` con QBO mockeado
- [ ] `python -c "from dexter.core.batch import BatchEngine"` funciona
- [ ] `main.py` intacto (legacy shim)

**Criterio de éxito:** Instanciar `BatchEngine`, pasarle un `BatchPlan` simulado, y verificar que audita, dry-runea y "ejecuta" (con mock) correctamente.

### Plan completo de sprints

```
Sprint 1 (esta semana) — "El motor sin skills"
├─ dexter/core/batch/ completo
├─ SQLite schema + migrations
├─ Tests del motor
└─ main.py intacto

Sprint 2 — "skill_batch_deposits funcional"
├─ skill_batch_deposits (CSV + NL)
├─ Parser CSV robusto
├─ Parser NL (1 call al LLM)
├─ Disambiguator interactivo con prompt_toolkit
├─ Dry-run con rich
├─ Reemplaza process_deposits_csv() (sin breaking change)
└─ Audit: cada batch en SQLite

Sprint 3 — "Bills y Reconciliación"
├─ skill_batch_bills (integra ocr_bills.py)
├─ skill_batch_recon (matching engine)
└─ Tests E2E con QBO sandbox

Sprint 4 — "Reclasificaciones y Scheduler"
├─ skill_batch_reclassify
├─ skill_scheduled_reports
├─ Background scheduler (in-process con schedule lib)
└─ Decisión: in-process vs systemd

Sprint 5 — "CLI + refactor final"
├─ CLI con prompt_toolkit + rich
├─ main.py = shim de 1 línea
├─ Migrar tools básicas a skills
├─ Tests de regresión v3.7 al 100%
└─ Documentación: docs/BATCH_OPERATIONS.md
```

### ¿Por qué NO empezar por Skills o CLI?

- **Skills primero**: sin el motor batch no tenés QUÉ skill crear que aporte valor nuevo.
- **CLI primero**: cosmética. Si pintás `input/print` ahora, duplicás el problema y refactorizás dos veces.
- **El motor batch primero**: valor desde el Sprint 2, y el resto se monta encima naturalmente.

---

## 📚 Contexto y decisiones cerradas

### Decisiones arquitectónicas clave

1. **No RAG**: el proyecto salta entre empresas; no necesita knowledge empresarial. Solo automatización.
2. **Single-company per batch**: el batch opera sobre la empresa activa. El hot-swap multi-empresa sigue siendo manual.
3. **Disambiguation interactiva por caso**: cuando algo no existe en QBO, Dexter pregunta antes de crear.
4. **Dual input**: CSV (lo que ya hay) + NL (instrucción en lenguaje natural con lista inline).
5. **Dry-run obligatorio**: precondición en código, no configurable.
6. **Sin dependencia de frameworks pesados**: sin LangChain, sin LlamaIndex. Control total.
7. **SQLite local como memoria**: sin servicios externos, máxima privacidad y portabilidad.

### Stakeholders

- **Alfredo** (desarrollador/owner): busca eficiencia operativa, automatiza trabajo manual repetitivo.
- **Usuarios finales** (contadores): necesitan predictibilidad y confianza en las transacciones creadas.

### Constraints no negociables

- Python 3.9+ (mantener compatibilidad con stack actual).
- Sin romper v3.7 en ningún sprint (legacy shims).
- Sin RAG / embeddings / vector stores.
- Datos contables NO salen de la máquina (privacidad).

---

**Elaborado por:** Proceso de diseño arquitectónico con Dexter
**Próxima revisión:** Al completar Sprint 1
