# Auditoría Completa del Proyecto Dexter v3.7

**Fecha:** 2026-06-03
**Versión auditada:** v3.7.0
**Alcance:** Inventario de capacidades, detección de stubs, análisis profundo de OCR / conciliación / clasificación, oportunidades de mejora, roadmap revisado.

---

## 1. Inventario de Capacidades Actuales

### 1.1 Estructura general del proyecto

```
Qbo Scripts/
├── main.py                          (3,063 líneas — el monolito)
├── company_manager.py               (190 líneas)
├── ocr_bills.py                     (197 líneas)
├── gitmanager.py                    (449 líneas)
├── test_suite.py                    (396 líneas)
├── install.sh                       (17,264 bytes)
├── chart_of_accounts.json           (20,818 bytes — caché)
├── .env / requirements.txt
├── autonomia/                       (442 líneas totales)
│   ├── __init__.py
│   ├── autonomia_nivel1_websearch.py    (94 líneas)
│   ├── autonomia_nivel2_api_explorer.py (112 líneas)
│   ├── autonomia_nivel3_code_executor.py (34 líneas)
│   ├── bank_feed_intelligence.py        (75 líneas)  ← STUB
│   ├── dynamic_report_generator.py      (55 líneas)  ← STUB
│   └── user_behavior_learning.py        (71 líneas)  ← STUB
├── docs/  (10 documentos markdown)
├── templates/  Backup/  Bank Reconciliation/  Pending bills/  Processed bills/  Test/
└── data/ companies/  outputs/
```

### 1.2 Capacidades que funcionan bien (mantener / complementar)

| Componente | Ubicación | Estado | Calidad |
|---|---|---|---|
| Búsqueda de clientes / vendors / cuentas | `search_customer`, `find_account` (main.py) | Funcional, fuzzy match 60% | Bueno |
| Multi-empresa | `gestionar_empresas`, `company_manager.py` | Funcional, hot-swap, tokens aislados | Bueno |
| Creación de transacciones (invoice, bill, deposit, payment) | `tool_crear_*` (main.py) | Funcional, validación básica | Bueno |
| Generación de reports estándar (P&L, Balance Sheet) | `tool_generar_*` | Funcional, QBO API directa | Bueno |
| Optimización de tokens (57% reducción) | `get_relevant_tools`, `build_conversation_context` | Funcional, sliding window + tools dinámicos | Excelente |
| Búsqueda web / API explorer | `autonomia_nivel1/2_websearch/api_explorer` | Funcional | Bueno |
| Code executor | `autonomia_nivel3_code_executor` | Funcional pero riesgoso (sin sandbox) | Regular |
| Chart of Accounts con caché 24h | `load_chart_of_accounts` | Funcional | Bueno |
| Tracking de tokens con CSV + Excel | `token_usage.csv` + Excel reports | Funcional | Bueno |
| Procesamiento de CSV de depósitos | `process_deposits_csv` (main.py:975) | Básico, sin dry-run, sin rollback | Regular |

### 1.3 Stubs detectados (módulos que existen pero no funcionan)

#### Stub 1 — `autonomia/bank_feed_intelligence.py`

Evidencia textual (líneas 42-49):

```python
def analyze_pending_transactions(self, transactions, min_confidence=0.7):
    return {
        "total": len(transactions),
        "high_confidence": [],
        "medium_confidence": [],
        "low_confidence": [],
        "no_match": []   # ← SIEMPRE VACÍO
    }
```

- `tool_find_pattern_for_transaction` siempre retorna `match_found: False`
- El dict `patterns` nunca se popula; solo `classifications[]` que es un log pasivo
- No hay algoritmo de matching (ni regex, ni fuzzy, ni ML, ni nada)
- El módulo entero es fachada: la "inteligencia" no existe

#### Stub 2 — `autonomia/user_behavior_learning.py`

- `tool_record_user_correction` retorna success sin hacer nada
- `tool_get_user_suggestions` siempre retorna `suggestion: None`
- Solo cuenta interacciones; no aprende nada
- El "learning" es solo un contador

#### Stub 3 — `autonomia/dynamic_report_generator.py`

```python
def generate_custom_report(self, user_request, filters=None):
    # ... parsea fecha ...
    return {
        "success": True,
        "report_type": "Profit & Loss",   # ← SIEMPRE P&L
        "message": "Reporte generado (versión simplificada)"  # ← NO GENERA NADA
    }
```

- Solo parsea fechas (`parse_date_expression` sí funciona)
- `QB_BASE_URL` está definido pero nunca se usa
- El parámetro `filters` se ignora completamente
- No llama a QBO API; retorna mensaje fake
- Hardcodeado a "Profit & Loss" en todos los casos

### 1.4 Catálogo completo de tools (21 + autonomía)

| # | Tool | Categoría | Ubicación |
|---|---|---|---|
| 1 | `buscar_cliente` | Búsqueda | main.py:2327 |
| 2 | `buscar_vendor` | Búsqueda | main.py:2339 |
| 3 | `buscar_cuenta` | Búsqueda | main.py:2349 |
| 4 | `buscar_item` | Búsqueda | main.py:2367 |
| 5 | `crear_invoice` | Transacción | main.py:2376 |
| 6 | `crear_bill` | Transacción | main.py:2380 |
| 7 | `crear_deposito` | Transacción | main.py:2385 |
| 8 | `crear_pago` | Transacción | main.py:2389 |
| 9 | `generar_reporte_pl` | Reporte | main.py:2394 |
| 10 | `generar_balance_sheet` | Reporte | main.py:2412 |
| 11 | `guardar_reporte` | Reporte | main.py:2429 |
| 12 | `cargar_reporte` | Reporte | main.py:2434 |
| 13 | `listar_reportes_guardados` | Reporte | main.py:2443 |
| 14 | `procesar_csv_depositos` | Batch | main.py:2456 |
| 15 | `crear_template_csv` | Utilidad | main.py:2460 |
| 16 | `obtener_estadisticas_tokens` | Métricas | main.py:2465 |
| 17 | `generar_informe_tokens` | Métricas | main.py:2479 |
| 18 | `refrescar_chart_accounts` | Utilidad | main.py:2484 |
| 19 | `gestionar_empresas` | Multi-empresa | main.py:2495 |
| 20 | `procesar_bank_feed_csv` | Batch | main.py:2558 |
| 21 | `procesar_reconciliacion_bancaria` | Batch | main.py:2562 |
| 22 | `procesar_lote_bills` | OCR | main.py:2652 (wrapper) |
| 23-24 | `buscarenweb`, `buscardocsqbo` | Autonomía L1 | websearch |
| 25-29 | `crearasientodiario`, `creartransferencia`, `qborequestgenerico`, `listarendpointsqbo`, `infoendpointqbo` | Autonomía L2 | api_explorer |
| 30 | `ejecutarcodigo` | Autonomía L3 | code_executor |
| 31-34 | `analizarbankfeed`, `registrarclasificacion`, `estadisticasclasificacion`, `buscarpatron` | Bank Feed ML | STUB |
| 35-38 | `aprenderinteraccion`, `obtenersugerencias`, `registrarcorreccion`, `obtenercontexto` | User Learning | STUB |
| 39-40 | `generarreportecustom`, `parsearfecha` | Reports | STUB parcial |

---

## 2. Auditoría Profunda: Conciliación Bancaria

### 2.1 Análisis de `procesar_reconciliacion_bancaria` (main.py:1312-1466)

Lo que hace bien:
- Lee CSV con detección automática de modo (CON / SIN balance)
- Valida suma matemática (opening + credits − debits = ending)
- Tolerancia de $0.01 para redondeos
- Crea deposits para créditos, bills para débitos
- Identifica filas de opening / ending balance
- Usa `Decimal` para precisión (no float)

### 2.2 Problemas críticos detectados

| # | Problema | Impacto | Solución propuesta |
|---|---|---|---|
| 1 | NO matchea contra transacciones existentes en QBO | Crea duplicados si ya cargaste el mes | Agregar paso de matching contra QBO API `/banktransactions` |
| 2 | No detecta duplicados en el CSV mismo | Si la misma fila aparece 2x, crea 2 transacciones | Hash de fila (date + amount + description) |
| 3 | Categorización hardcodeada | Todo crédito → "Income" genérico, todo débito → "Bank Charges" | Usar `bank_feed_intelligence` (que es stub) o implementar matching real |
| 4 | Vendor "Bank Charges" hardcodeado (línea 1439) | Si no existe, falla silenciosamente | Buscar vendor real por descripción con fuzzy match |
| 5 | No maneja múltiples cuentas bancarias en un CSV | Asume 1 sola cuenta | Detectar cuenta por descripción o columna dedicada |
| 6 | No genera reporte de reconciliación | Usuario no ve qué se creó vs qué se omitió | Generar PDF / HTML con tabla final |
| 7 | No hay rollback | Si falla a mitad, quedan items sueltos en QBO | Audit log + idempotencia por item |
| 8 | No distingue tipos de transacción | Transferencias, fees, intereses, reversals van todos al mismo lugar | Clasificar por patrón de descripción |
| 9 | Falta integración con `bank_feed_intelligence` | El stub existe pero no se usa | Conectar al motor de matching cuando se reescriba |
| 10 | Balance final calculado no se muestra al usuario | Está en `results['summary']` pero no se renderiza | Mostrar tabla rica con `rich` |
| 11 | Mensajes en español mezclan términos en inglés | "bank_feed_amount", "deposit_id" | Estandarizar a español en mensajes user-facing |
| 12 | No considera fechas ya pasadas | Reconcilia enero en marzo sin advertir | Advertir si la fecha del CSV es > 30 días atrás |

### 2.3 Análisis de `procesar_csv_bank_feed` (main.py:1212-1308)

Mejor implementada que reconciliación: tiene agrupación por `deposit_id` y validación de suma.

Problemas menores:
- Mensajes mezclan español / inglés
- Asume que todos los `customer_id` ya existen en QBO (sin fallback)
- No aprovecha `bank_feed_classification_history.json` para sugerir categorías

### 2.4 Comparación con QBO Bank Feed real

| Feature | QBO Bank Feed | Dexter actual |
|---|---|---|
| Reglas manuales del usuario | Sí | No |
| Auto-categorización con ML | Sí (QuickBooks AI) | No |
| Sugerencia de matches históricos | Sí | No (stub) |
| Confidence score | Sí | No |
| Vendor recognition | Sí | No |
| Aprende de correcciones | Sí | No (stub) |
| Matching contra transacciones existentes | Sí | No |
| Multi-cuenta | Sí | No |

---

## 3. Auditoría Profunda: Clasificación de Transacciones

### 3.1 Estado real del módulo de "inteligencia"

El archivo `bank_feed_intelligence.py` tiene la estructura de un motor de clasificación pero NO tiene el motor. Es un esqueleto:

```
Estructura ✓:  class, history, save/load
Algoritmo ✗:    cómo matchear una transacción contra patrones históricos
Persistencia ✓: JSON file
Aprendizaje ✗:   no extrae patrones, solo guarda filas crudas
```

Lo que necesitaría un motor real:

```python
def find_pattern(description: str) -> Optional[dict]:
    """Match description against history using regex/fuzzy/semantic."""
    # 1. Normalizar (lowercase, sin punctuation, sin números)
    # 2. Buscar regex exactos
    # 3. Buscar substring matches
    # 4. Buscar fuzzy match (SequenceMatcher)
    # 5. Buscar por monto similar
    # 6. Retornar mejor match con confidence score
```

### 3.2 Análisis de `autonomia/user_behavior_learning.py`

| Función | Comportamiento real | Comportamiento esperado |
|---|---|---|
| `learn_account_preference` | Cuenta frecuencia | OK, funciona |
| `update_conversation_context` | Append + trim a 20 | OK, funciona |
| `tool_learn_from_interaction` | Llama a las dos anteriores | OK |
| `tool_get_user_suggestions` | Retorna None siempre | Debería rankear preferencias |
| `tool_record_user_correction` | No-op | Debería guardar el mapping para aprender |
| `tool_get_conversation_context` | Retorna últimos 10 topics | OK |

### 3.3 Análisis de `autonomia/dynamic_report_generator.py`

| Función | Comportamiento real | Comportamiento esperado |
|---|---|---|
| `parse_date_expression` | Funciona para "este mes", "mes pasado", "este año" | OK |
| `generate_custom_report` | Retorna P&L fake sin llamar a QBO | Debería llamar a QBO reports API |
| `QB_BASE_URL` definido | Nunca usado | Debería usarse para todos los reports |
| `filters` param | Ignorado | Debería soportar agrupación por customer / vendor / class |

Reportes que QBO API ofrece y Dexter podría generar pero no genera:
- Cash Flow Statement
- AR Aging (cuentas por cobrar vencidas)
- AP Aging (cuentas por pagar vencidas)
- Trial Balance
- Sales by Customer
- Expenses by Vendor
- General Ledger

---

## 4. Auditoría del Módulo OCR (`ocr_bills.py`)

### 4.1 Lo que hace bien

- Usa Gemini 2.5 Flash (rápido, multimodal, gratis hasta 500 RPD)
- Convierte PDF a imágenes con `pdf2image` (DPI 300, buena calidad)
- Prompt estructurado pidiendo JSON con campos obligatorios + opcionales
- Maneja PDFs multi-página y multi-invoice por página
- Codificación robusta (base64 inlining, sin URL temporales)
- Genera CSV preview con timestamp único
- Configuración con `temperature: 0.1` (determinístico)
- `response_mime_type: "application/json"` (fuerza JSON válido)
- Logging visual durante el proceso
- Maneja archivos en múltiples rutas posibles (`Pending bills/`, `~/Documents/...`)

### 4.2 Problemas y oportunidades

| # | Gap | Impacto | Solución propuesta |
|---|---|---|---|
| 1 | No procesa PDFs en lote automáticamente | Hoy hay que invocar `extraer_bills_de_pdf()` por cada PDF uno por uno | Loop sobre carpeta `Pending bills/` con barra de progreso |
| 2 | No persiste resultados a SQLite | Cada ejecución genera un CSV nuevo, no hay historial | Tabla `ocr_extractions` en `data/dexter.db` |
| 3 | No valida que el vendor exista en QBO | El CSV dice "Acme Corp" pero el agente no sabe si existe en QBO | Paso de validación: `search_vendor` después de OCR |
| 4 | No detecta facturas duplicadas | Si el mismo PDF se procesa 2 veces, genera 2 CSVs | Hash del PDF o invoice_number |
| 5 | No tiene confidence score | El LLM responde con JSON sin certeza de cada campo | Pedirle a Gemini que retorne `confidence` por campo |
| 6 | No maneja imágenes directamente | Solo PDFs (con poppler instalado) | Agregar soporte JPG / PNG directo |
| 7 | Account hardcodeado a "Prepaid Material" (línea 158) | Todos los bills van a la misma cuenta | Detectar account por categoría del vendor o por palabras clave |
| 8 | No extrae line items | Solo el total, no las líneas individuales | Mejorar prompt para extraer líneas |
| 9 | No soporta facturas en otros idiomas | El prompt está en español; inglés podría fallar | Prompt bilingüe con detección |
| 10 | No hay retry en caso de fallo de Gemini | Si la API falla, se pierde el trabajo | Reintentar 3 veces con backoff exponencial |
| 11 | `procesar_lote_bills` solo procesa UN PDF | El wrapper existe pero la lógica OCR está desconectada del loop | Conectar: debe iterar sobre todos los PDFs de la carpeta |
| 12 | No hay validación de totales | Si el PDF dice $1,250.00 pero las líneas suman $1,240, no se detecta | Validación matemática (subtotal + tax = total) |
| 13 | No hay tests | El módulo crítico no tiene cobertura | Tests unitarios con PDFs de ejemplo + mocks de Gemini |
| 14 | No maneja facturas con descuentos | Descuentos, retenciones, notas de crédito no se capturan | Agregar campos al schema |
| 15 | No detecta tipo de documento | Bill, Invoice, Credit Note, Quote se tratan igual | Clasificar el tipo de documento en el prompt |

### 4.3 Observación importante sobre la integración

Hay DOS puntos de entrada para OCR que no están completamente integrados:
- `ocr_bills.py` → función `extraer_bills_de_pdf()`
- `main.py:2652` → `procesar_lote_bills()` que llama al primero pero solo procesa UN PDF (no itera sobre la carpeta)

La conexión existe (`from ocr_bills import extraer_bills_de_pdf` en main.py:17), pero `procesar_lote_bills` no procesa en lote real.

---

## 5. Mejoras Propuestas (organizadas por prioridad)

### 5.1 Prioridad Crítica — Reescribir stubs (sin valor funcional hoy)

#### Mejora 1 — `autonomia/bank_feed_intelligence.py` — Motor de clasificación real

- Líneas actuales: 75
- Acción: reescritura 90%
- Valor: 5/5

Implementar de verdad:
- Algoritmo de matching con 3 estrategias combinadas (regex → fuzzy → histórico)
- Normalización de descripciones (`"AMAZON.COM*MK4J2"` → `"amazon"`)
- Confidence score 0-100% por sugerencia
- Patrones aprendidos por usuario (no solo por defecto)
- Detección de "siempre clasifiqué AMAZON como Office Supplies"

```python
def classify(description: str, amount: float, history: dict) -> dict:
    """Retorna {account_id, account_name, confidence, reasoning}"""
    # Paso 1: Match exacto en histórico
    # Paso 2: Regex patterns del usuario
    # Paso 3: Fuzzy match (SequenceMatcher 80%+)
    # Paso 4: Match por monto similar
    # Paso 5: Default sugerido
```

#### Mejora 2 — `autonomia/dynamic_report_generator.py` — Llamar de verdad a QBO

- Líneas actuales: 55
- Acción: reescritura 60%
- Valor: 4/5

- Implementar `qbo_request("GET", "reports/CashFlow", ...)` que ya está disponible
- Agregar reportes: Cash Flow, AR Aging, AP Aging, Trial Balance, Sales by Customer
- Usar el parámetro `filters` ignorado actualmente
- Soportar agrupación por customer, vendor, class, location
- Exportar a Excel con formato (.xlsx con `openpyxl`)

#### Mejora 3 — `autonomia/user_behavior_learning.py` — Aprendizaje real

- Líneas actuales: 71
- Acción: reescritura 70%
- Valor: 3/5

- `record_user_correction` debe guardar el mapping (wrong → correct)
- `get_user_suggestions` debe usar las correcciones guardadas para rankear
- Implementar "preferred accounts": si Alfredo usa 80% de las veces "Office Supplies", sugerirlo primero
- Conectar con `bank_feed_intelligence` (las correcciones alimentan el motor de clasificación)

### 5.2 Prioridad Alta — Mejorar capacidades existentes

#### Mejora 4 — `procesar_reconciliacion_bancaria` — Reconciliación real vs QBO

- Líneas: 154
- Acción: agregar 3 pasos
- Valor: 5/5

- Paso nuevo 1: Antes de crear nada, descargar transacciones del banco desde QBO API (`/banktransactions` o `/purchase` / `/deposit`)
- Paso nuevo 2: Matching engine: por cada fila del CSV, buscar match exacto (date + amount) o fuzzy (date ±2 días + amount ±$0.50)
- Paso nuevo 3: Tres estados por fila: `matched_existing` (no crear), `new_income` (crear deposit), `new_expense` (crear bill)
- Generar reporte HTML / PDF con: matched / created / unmatched
- Soporte para múltiples cuentas bancarias (detectar por descripción o columna)

#### Mejora 5 — `ocr_bills.py` — Procesamiento en lote + persistencia

- Líneas: 197
- Acción: agregar 4 features
- Valor: 4/5

- Loop sobre todos los PDFs en `Pending bills/`
- SQLite para historial de extracciones
- Confidence score por campo (Gemini puede retornarlo si se le pide)
- Validación: subtotal + tax = total, líneas suman al subtotal
- Re-procesamiento de PDFs fallidos (retry con backoff)
- Tests con PDFs de ejemplo

#### Mejora 6 — `procesar_csv_depositos` (main.py:975) — Convertir a BatchEngine

- Líneas: 70
- Acción: refactor al motor batch
- Valor: 4/5

- Migrar al `BatchEngine` del Sprint 1
- Agregar disambiguation interactiva
- Dry-run obligatorio
- Audit log persistente

### 5.3 Prioridad Media — Nuevas capacidades que amplían alcance

#### Mejora 7 — Detección de anomalías contables
- Transacciones fuera de patrón histórico (monto inusual, vendor nuevo, hora rara)
- Vendor con cambios de cuenta frecuentes (posible fraude)
- Depósitos redondos sospechosos

#### Mejora 8 — Reportes programados con notificación
- Email automático del P&L mensual
- Webhook a Slack / Discord con resumen
- Excel programado con comparativa mes a mes

#### Mejora 9 — Búsqueda full-text en transacciones históricas
- "¿Cuánto le pagamos a Acme Corp en 2024?"
- "¿Cuáles fueron todos los gastos de Amazon el Q4?"
- Búsqueda con filtros combinados (fecha + monto + vendor + cuenta)

#### Mejora 10 — Soporte multi-moneda
- Conversión automática USD ↔ EUR ↔ COP
- Tipo de cambio del día desde API gratuita
- Manejo de ganancia / pérdida por diferencia cambiaria

#### Mejora 11 — Cierre mensual guiado
- Wizard paso a paso: revisión de cuentas por cobrar, depreciaciones, ajustes
- Validaciones automáticas (deudas sin factura, facturas sin pago > 90 días)
- Generación del paquete de cierre para el contador

#### Mejora 12 — Plantillas de transacciones recurrentes
- "Cada mes cobrar retainer a Acme Corp por $5,000"
- "Cada viernes pagar nóminas"
- Ejecución automática con confirmación previa

### 5.4 Prioridad Baja — Nice to have

#### Mejora 13 — UI web con Streamlit (paralela a la CLI)
- Dashboard de métricas
- Visualización de batches en ejecución
- Aprobación visual de dry-runs

#### Mejora 14 — Integración con bancos (Plaid, etc.)
- Descarga automática de CSVs
- Sync de balances en tiempo real
- (Requiere partnerships bancarios)

#### Mejora 15 — Multi-tenant SaaS
- Múltiples usuarios con sus empresas
- Roles (admin, contador, viewer)
- Billing

---

## 6. Roadmap Revisado (incorporando todo lo anterior)

### Sprint 1 — Motor batch + reemplazar stub #1 (bank_feed_intelligence)
- `dexter/core/batch/` skeleton
- SQLite schema
- Tests del motor
- Reescribir `bank_feed_intelligence.py` con algoritmo real de clasificación
- Entregable: Clasificación funcional + motor batch testeable

### Sprint 2 — skill_batch_deposits + reemplazar stub #2 (dynamic_report_generator)
- Skill de depósitos con BatchEngine
- Disambiguator + dry-run
- Reescribir `dynamic_report_generator.py` con QBO API real + 5+ tipos de reporte
- Entregable: Depósitos con UX moderna + 5 reportes custom funcionando

### Sprint 3 — skill_batch_bills (con OCR mejorado) + skill_batch_recon
- Loop de OCR sobre todos los PDFs de `Pending bills/`
- SQLite para extracciones
- Confidence score
- Validación matemática
- Skill de reconciliación con matching engine real
- Entregable: OCR batch + reconciliación vs QBO

### Sprint 4 — Reclasificaciones + Scheduler + reemplazar stub #3 (user_behavior)
- skill_batch_reclassify
- skill_scheduled_reports
- Reescribir `user_behavior_learning.py` con aprendizaje real conectado a bank_feed
- Entregable: 5 skills batch completas + aprendizaje funcional

### Sprint 5 — CLI + refactor de los 3,000 líneas
- `main.py` = shim
- prompt_toolkit + rich
- Migrar tools básicas a skills
- Entregable: v4.0.0 — todas las capacidades existentes mejoradas, todas las nuevas operativas

### Sprint 6 (opcional) — Mejoras de prioridad media
- Detección de anomalías
- Búsqueda full-text histórica
- Multi-moneda
- Cierre mensual guiado

---

## 7. Métricas de Calidad del Código Actual

| Métrica | Valor actual | Valor objetivo v4.0 |
|---|---|---|
| Líneas en `main.py` | 3,063 | < 200 (shim) |
| Tools monolíticas | 21 | 0 (todas en skills) |
| Módulos stub sin funcionalidad | 3 | 0 |
| Cobertura de tests | Desconocida (sin test del OCR) | > 70% |
| Funcionalidades documentadas vs implementadas | ~ 80% | 100% |
| Tiempo promedio de una transacción batch | Best-effort, sin medición | < 2s por item |
| Capacidad de rollback | 0% | 100% (re-ejecutable) |

---

## 8. Conclusiones de la Auditoría

### 8.1 Hallazgos principales

1. Tres módulos de autonomía son stubs: `bank_feed_intelligence`, `user_behavior_learning`, `dynamic_report_generator`. Existen formalmente pero no proveen valor funcional.

2. La conciliación bancaria es básica: `procesar_reconciliacion_bancaria` funciona matemáticamente pero no hace matching contra QBO, no detecta duplicados, y categoriza todo de forma hardcodeada.

3. El OCR es el módulo más sólido pero subutilizado: `ocr_bills.py` está bien implementado con Gemini 2.5 Flash, pero `procesar_lote_bills` no itera sobre toda la carpeta.

4. El monolito `main.py` es el mayor riesgo: 3,063 líneas con 21 tools, optimizaciones, loop principal, y esquema TOOLS. Cualquier cambio tiene alta probabilidad de regresión.

5. El tracking de tokens y la optimización del 57% son亮点: lo mejor del proyecto, mantenible y funcional.

### 8.2 Recomendaciones inmediatas

- Reescribir los 3 stubs en Sprints 1, 2 y 4 (uno por sprint, sin paralizar el desarrollo).
- Migrar `procesar_reconciliacion_bancaria` a un patrón con matching engine real contra QBO API.
- Hacer el OCR verdaderamente "lote" con loop sobre `Pending bills/`.
- Introducir el motor batch genérico que soporte las 5 operaciones.
- Considerar el monolito `main.py` como legacy desde el Sprint 1, no esperar a refactorizar al final.

---

**Elaborado por:** Proceso de auditoría con Dexter
**Próxima revisión:** Al completar Sprint 1
