# Guía del Motor Batch de Dexter

**Versión:** v4.0.0-dev
**Fecha:** 2026-06-03
**Estado:** Sprint 1 + 2 completados, 128 tests pasando

---

## ¿Qué es el Motor Batch?

Un sistema reutilizable para ejecutar operaciones contables de alto volumen con:

- ✅ **Persistencia SQLite** (audit log completo, recuperable)
- ✅ **State machine** validada (no se puede ejecutar sin dry-run + confirmación)
- ✅ **Desambiguación interactiva** (pregunta al usuario solo cuando hace falta)
- ✅ **Idempotencia parcial** (re-ejecutable; items exitosos se saltan)
- ✅ **API testeable** (QBO client inyectable, sin dependencias externas en tests)

---

## Arquitectura

```
dexter/core/batch/
├── __init__.py         # API pública
├── storage.py          # SQLite (batches, items, audit_log)
├── engine.py           # State machine + transiciones validadas
├── disambiguator.py    # Preguntas al usuario (input/output inyectables)
└── deposits.py         # Skill de bank deposits multi-cliente
```

### Capas

```
┌─────────────────────────────────────────┐
│  Skill (deposits, bills, reclassify)    │  ← Lógica de dominio
├─────────────────────────────────────────┤
│  Engine (state machine)                 │  ← Ciclo de vida
├─────────────────────────────────────────┤
│  Storage (SQLite)                       │  ← Persistencia
└─────────────────────────────────────────┘
         ▲
         │  usa
         │
┌─────────────────────────────────────────┐
│  Disambiguator (preguntas)              │  ← I/O con el usuario
└─────────────────────────────────────────┘
```

---

## Uso desde la línea de comandos

### Crear un deposit multi-cliente

**1. Prepara el CSV:**

```csv
date,client_name,amount,terms,memo
2026-06-01,Acme Corp,5000,Net 30,Service payment
2026-06-01,Maria Rodriguez,3000,Net 30,Consulting
2026-06-01,Jose Perez,2000,Net 15,Service payment
```

**2. Ejecuta:**

```bash
python main.py
> "Procesa el deposit multi-cliente de Acme Corp con el archivo pending_deposits.csv"
```

**3. Dexter:**
- Para cada cliente, busca en QBO
- Si no existe, pregunta: email, términos, teléfono
- Te muestra el dry-run con totales
- Confirmas
- Crea los deposits
- Audit log guardado en `data/dexter.db`

---

## Uso programático (skill reutilizable)

```python
from dexter.core.batch import (
    BatchEngine, BatchStorage, Disambiguator, DepositBatchSkill
)
from autonomia.bank_feed_intelligence import classify_transaction

# 1. Setup
storage = BatchStorage("data/dexter.db")
engine = BatchEngine(storage)
disambiguator = Disambiguator()  # usa input() y print() por defecto
qbo_client = MyQBOClient()  # tu implementación del protocolo
classifier = lambda desc, amt: classify_transaction(desc, amt, storage_history)

# 2. Crear skill
skill = DepositBatchSkill(
    engine=engine,
    disambiguator=disambiguator,
    qbo_client=qbo_client,
    classifier=classifier,
    bank_account_id="35",  # tu Checking account
    income_account_id="svc_revenue",
)

# 3. Pipeline
bid = skill.from_csv("pending_deposits.csv")
skill.validate(bid)              # busca/crea clientes
skill.engine.dry_run(bid)        # resumen
disambiguator.confirm_batch(...) # confirmas
skill.engine.confirm(bid)
result = skill.execute(bid)      # crea deposits en QBO
print(f"Ejecutados: {result['executed']}, Fallidos: {result['failed']}")
```

---

## Estados de un Batch

```
PENDING → VALIDATED → DRY_RUN → CONFIRMED → EXECUTING → EXECUTED
   ↓          ↓          ↓          ↓
CANCELLED  CANCELLED  CANCELLED  CANCELLED
   ↓
 FAILED → (retry → PENDING)
```

**Reglas:**
- No puedes ejecutar sin validar, dry-run, y confirmar
- Puedes cancelar en cualquier estado pre-ejecución
- Solo puedes reintentar un batch FAILED (crea uno nuevo con los mismos items)
- Las transiciones inválidas lanzan `InvalidStateTransition`

---

## Auditoría

Cada batch deja un rastro completo en SQLite:

```sql
-- Ver todos los batches
SELECT id, skill, state, created_at FROM batches;

-- Ver el log de un batch específico
SELECT timestamp, event, details_json
FROM audit_log
WHERE batch_id = 'abc-123'
ORDER BY id;

-- Ver items fallidos
SELECT * FROM items
WHERE batch_id = 'abc-123' AND state = 'FAILED';
```

**Eventos registrados automáticamente:**
- `BATCH_CREATED` — al crear
- `BATCH_STATE_CHANGED` — en cada transición
- `BATCH_CONTEXT_UPDATED` — al modificar contexto
- `ITEM_ADDED` — al agregar item
- `ITEM_STATE_CHANGED` — al cambiar estado de item

---

## Testing

Todos los componentes son testeables sin QBO real:

```bash
# Ejecutar todos los tests
python -m unittest discover tests

# Solo batch
python -m unittest tests.test_batch_storage tests.test_batch_engine \
                   tests.test_batch_disambiguator tests.test_batch_deposits

# Verbose
python -m unittest tests.test_batch_deposits -v
```

**Cobertura actual: 128 tests pasando**

| Módulo | Tests |
|---|---|
| `batch_storage` | 27 |
| `batch_engine` | 24 |
| `batch_disambiguator` | 18 |
| `batch_deposits` | 13 |
| `bank_feed_intelligence` | 27 |
| `ocr_bills` | 19 |
| **Total** | **128** |

---

## Próximos Skills (Sprint 3+)

La misma arquitectura soporta:

- **`bills_skill`** — OCR en lote + crear bills en QBO
- **`reconciliation_skill`** — matching engine contra QBO
- **`reclassify_skill`** — mover N transacciones de cuenta X a Y
- **`scheduled_reports_skill`** — ejecutar reportes programados

Cada uno sigue el mismo patrón:
1. `from_X()` crea el batch
2. `validate()` resuelve ambigüedades
3. `engine.dry_run()` muestra preview
4. Usuario confirma
5. `execute()` aplica cambios en QBO
6. Audit log

---

## Convenciones

- **Inyección de dependencias**: `QBOClientProtocol`, `input_func`, `output_func`
- **Errores explícitos**: `InvalidStateTransition`, `FileNotFoundError`, `ValueError`
- **Auditoría automática**: nunca hacer cambios sin `storage.log_event()`
- **Tests primero**: TDD red-green-refactor

---

**Mantenedor:** Alfredo
**Última actualización:** 2026-06-03
