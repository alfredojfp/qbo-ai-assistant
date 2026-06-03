# Plan de Implementación: Corrección de Hallazgos de Auditoría v3.7

> **Para implementadores:** Este plan documenta TODOS los hallazgos de la auditoría y marca cuáles se abordan en esta sesión vs cuáles quedan pendientes.

**Goal:** Corregir los 3 stubs detectados en la auditoría + hacer OCR verdaderamente batch + mejorar la conciliación bancaria, manteniendo el proyecto organizado y documentado.

**Architecture:** Módulo nuevo `dexter/core/batch/` para operaciones batch reutilizables, con motor de matching real, persistencia SQLite, dry-run, y audit log. Migración gradual de las funciones monolíticas en `main.py` a este motor.

**Tech Stack:** Python 3.10+, `sqlite3` (stdlib), `pdf2image`, `google-genai` (Gemini 2.5 Flash), `pytest` (nuevo), `unittest` (fallback), `rich` (UI futura).

---

## Hallazgos de la Auditoría y Status

### 🔴 PRIORIDAD CRÍTICA — Stubs a reescribir

| # | Hallazgo | Archivo | Status | Sesión |
|---|---|---|---|---|
| 1 | `analyze_pending_transactions` retorna listas vacías hardcodeadas | `autonomia/bank_feed_intelligence.py:42-49` | ✅ **REESCRITO** | Esta sesión |
| 2 | `tool_find_pattern_for_transaction` siempre retorna `match_found: False` | `autonomia/bank_feed_intelligence.py:74-75` | ✅ **REESCRITO** | Esta sesión |
| 3 | `tool_record_user_correction` no hace nada | `autonomia/user_behavior_learning.py:65-66` | ⏳ Pendiente | Sesión 2 |
| 4 | `tool_get_user_suggestions` siempre retorna `None` | `autonomia/user_behavior_learning.py:60-63` | ⏳ Pendiente | Sesión 2 |
| 5 | `generate_custom_report` retorna P&L fake sin llamar a QBO | `autonomia/dynamic_report_generator.py:36-44` | ⏳ Pendiente | Sesión 3 |
| 6 | `QB_BASE_URL` definido pero nunca usado | `autonomia/dynamic_report_generator.py:14` | ⏳ Pendiente | Sesión 3 |

### 🟡 PRIORIDAD ALTA — Mejoras a código existente

| # | Hallazgo | Ubicación | Status | Sesión |
|---|---|---|---|---|
| 7 | OCR solo procesa UN PDF por invocación | `ocr_bills.py` + `main.py:2652` | ✅ **HECHO** | Esta sesión |
| 8 | No hay retry en OCR con backoff | `ocr_bills.py:102-103` | ⏳ Pendiente | Sesión 2 |
| 9 | No persiste extracciones a SQLite | `ocr_bills.py` | ⏳ Pendiente | Sesión 2 |
| 10 | No valida vendor existe en QBO post-OCR | `ocr_bills.py` | ⏳ Pendiente | Sesión 2 |
| 11 | No detecta PDFs duplicados | `ocr_bills.py` | ⏳ Pendiente | Sesión 2 |
| 12 | `Account_Name` hardcodeado a "Prepaid Material" | `ocr_bills.py:158` | ⏳ Pendiente | Sesión 2 |
| 13 | Reconciliación no matchea contra QBO | `main.py:1312-1466` | ⏳ Pendiente | Sesión 3 |
| 14 | Vendor "Bank Charges" hardcodeado | `main.py:1439` | ⏳ Pendiente (depende de #1) | Sesión 3 |
| 15 | `procesar_csv_depositos` sin dry-run ni rollback | `main.py:975` | ⏳ Pendiente | Sesión 4 |

### 🟢 PRIORIDAD MEDIA — Nuevas capacidades (diferidas a v4.1+)

| # | Feature | Valor | Sprint propuesto |
|---|---|---|---|
| 16 | Detección de anomalías contables | Medio | v4.1 |
| 17 | Reportes programados con email/Slack | Alto | v4.1 |
| 18 | Búsqueda full-text histórica | Alto | v4.1 |
| 19 | Multi-moneda con tipo de cambio | Bajo (firma USA) | v4.2 |
| 20 | Cierre mensual guiado | Alto | v4.1 |
| 21 | Plantillas recurrentes | Medio | v4.2 |

### ⚪ FUERA DE ALCANCE

- UI web (Streamlit)
- Multi-tenant SaaS
- Integración bancaria (Plaid)
- Multi-moneda

---

## Sesión Actual — Tareas Ejecutadas

### Tarea 1: Reestructuración del módulo `bank_feed_intelligence.py` con motor real ✅

**Problema:** El motor actual retorna listas vacías hardcodeadas y no hace matching real.

**Solución:** Implementar 3 estrategias de matching combinadas con confidence score.

**Archivos:**
- Modificar: `autonomia/bank_feed_intelligence.py` (75 → ~250 líneas)
- Crear: `tests/test_bank_feed_intelligence.py` (~150 líneas)

**Algoritmo:**

1. **Normalización** de descripción: lowercase, quitar punctuation, quitar números, colapsar espacios
2. **Match exacto** contra histórico (100% confidence)
3. **Regex patterns** aprendidos del usuario (95% confidence)
4. **Fuzzy match** con `difflib.SequenceMatcher` (ratio > 0.7 = match)
5. **Match por monto** similar (±5% del monto) como tiebreaker
6. **Default sugerido** por categoría de monto (gastos < $100 = Office Supplies, etc.)

**Confidence score 0-100%**:
- Exacto: 100
- Regex aprendido: 95
- Fuzzy ≥ 0.85: 80
- Fuzzy ≥ 0.70: 60
- Solo monto: 30
- Default: 15

**API pública (compatible hacia atrás):**
- `tool_analyze_bank_feed_for_classification` (sin cambios en firma)
- `tool_record_bank_feed_classification` (sin cambios en firma)
- `tool_get_classification_history_stats` (sin cambios en firma)
- `tool_find_pattern_for_transaction` (sin cambios en firma) ← ahora SÍ funciona

### Tarea 2: OCR verdaderamente en lote ✅

**Problema:** `extraer_bills_de_pdf()` procesa solo 1 PDF. `procesar_lote_bills` en main.py invoca solo una vez.

**Solución:** Nueva función `procesar_lote_ocr()` en `ocr_bills.py` que itera sobre todos los PDFs de una carpeta, con barra de progreso, manejo de errores, y resumen final.

**Archivos:**
- Modificar: `ocr_bills.py` (197 → ~280 líneas)
- Crear: `tests/test_ocr_bills.py` (~80 líneas)

**Comportamiento:**
- Lista todos los PDFs en `Pending bills/` (configurable)
- Para cada PDF: extrae bills, valida campos mínimos, registra éxito/fallo
- Resumen final: PDFs procesados, bills extraídos, fallos, tiempo total
- Mueve PDFs fallidos a `Pending bills/_failed/` con razón del fallo
- Genera CSV consolidado de todos los bills extraídos

### Tarea 3: Re-evaluación Dexter vs opencode ✅

**Output:** Documento `RE_EVALUACION_v4.md` con matriz caso-por-caso, basada en el uso real del usuario (firma contable, 2-3 empresas, alto volumen).

---

## Tareas Pendientes (Sesiones Futuras)

### Sesión 2: Reclasificaciones + Scheduled + Stub 3
- Reclasificar batch (corregir errores de mes)
- Reportes programados por cliente
- Reescribir `user_behavior_learning.py` (stub 3) con aprendizaje real conectado a bank_feed

### Sesión 3: Conciliación real + Stub 2
- Reescribir `procesar_reconciliacion_bancaria` con matching engine contra QBO API
- Reescribir `dynamic_report_generator.py` (stub 2) con QBO real
- Soporte multi-cuenta bancaria

### Sesión 4: Persistencia y robustez OCR
- SQLite para extracciones OCR
- Retry con backoff
- Validación de vendor en QBO
- Detección de duplicados
- Cuenta dinámica (no hardcodeada)

### Sesión 5: CLI + refactor del monolito
- `main.py` = shim
- prompt_toolkit + rich
- Migrar tools a skills

---

## Estructura de Archivos Resultante

```
Qbo Scripts/
├── autonomia/                      # [existente — 3 archivos mod]
│   ├── bank_feed_intelligence.py   # [REESCRITO — motor real]
│   ├── user_behavior_learning.py   # [pendiente]
│   └── dynamic_report_generator.py # [pendiente]
├── dexter/                         # [NUEVO módulo]
│   ├── __init__.py
│   └── core/
│       ├── __init__.py
│       └── batch/
│           ├── __init__.py
│           ├── engine.py           # [futuro Sprint 1]
│           ├── matching.py         # [importado de bank_feed]
│           └── storage.py          # [futuro]
├── ocr_bills.py                    # [MODIFICADO — lote real]
├── tests/                          # [NUEVO]
│   ├── __init__.py
│   ├── test_bank_feed_intelligence.py
│   └── test_ocr_bills.py
├── docs/
│   ├── ...
│   └── RE_EVALUACION_v4.md         # [NUEVO]
├── AUDITORIA_v3.7.md               # [existente]
├── ANALISIS_IMPLEMENTACION_v4.0.md # [existente]
└── 2026-06-03-corregir-*.md        # [este plan]
```

---

## Criterios de "Hecho" para Esta Sesión

- [x] Plan creado
- [x] `bank_feed_intelligence.py` reescrito con motor real
- [x] `bank_feed_intelligence.py` mantiene API hacia atrás (no rompe main.py)
- [x] `ocr_bills.py` ahora procesa en lote
- [x] Tests escritos para los 2 cambios
- [x] Re-evaluación Dexter vs opencode
- [x] Documentación actualizada
- [x] Commits frecuentes con mensajes claros

---

**Última actualización:** 2026-06-03
