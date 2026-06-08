# 📜 Changelog — QuickBooks AI Assistant

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased] - 2026-06-04

### 🆕 Agregado — Sprints 1+2+3 QBO API (54 tools nuevos, 45%→93% cobertura)

**Sprint 1A — Master Data (8 tools):**
- `crear_vendor` (proveedor), `crear_cuenta` (Chart of Accounts), `crear_item` (Service/Inventory/NonInventory), `crear_empleado` (nómina), `crear_clase` (segmentación), `crear_departamento` (segmentación), `crear_termino` (plazos Net 30/2/10 Net 30), `crear_paymentmethod` (métodos de pago). Módulo nuevo: `dexter/tools/master_data.py`.

**Sprint 1B — Transacciones faltantes (9 tools):**
- `crear_billpayment` (paga uno o más bills), `crear_estimate` (cotización), `crear_salesreceipt` (venta de mostrador), `crear_creditmemo` (nota de crédito cliente), `crear_purchase` (compra genérica), `crear_purchaseorder` (PO), `crear_refundreceipt` (reembolso), `crear_vendorcredit` (crédito proveedor), `crear_timeactivity` (horas trabajadas). Módulo nuevo: `dexter/tools/transaction_extra.py`.

**Sprint 1C — Update/Void/Delete/Send (10 tools):**
- `actualizar_cliente`, `actualizar_vendor`, `actualizar_factura`, `actualizar_bill` (con auto-sync_token), `eliminar_transaccion` (simplified delete, 12 entidades), `void_transaccion` (preserva historial), `desactivar_cliente`, `desactivar_vendor`, `enviar_factura`, `enviar_orden_compra`. Módulo nuevo: `dexter/tools/operations.py`.

**Sprint 1E — Reportes nativos (10 + 6 P2 = 16 tools):**
- P1: `reporte_trial_balance` (Balance de Comprobación), `reporte_general_ledger` (Libro Mayor), `reporte_cash_flow` (Flujo de Efectivo), `reporte_ar_aging` (antigüedad por cobrar), `reporte_ap_aging` (antigüedad por pagar), `reporte_customer_balance`, `reporte_vendor_balance`, `reporte_pl_detail` (P&L detallado), `reporte_journal` (journal entries), `reporte_account_list`.
- P2: `reporte_inventory_valuation`, `reporte_sales_by_customer`, `reporte_expenses_by_vendor`, `reporte_transaction_list`, `reporte_class_sales`, `reporte_department_sales`. Módulo: `dexter/tools/reports_extra.py` (pasa de 10 → 16 tools).

**Sprint 1F — Lectura directa (3 tools):**
- `leer_companyinfo` (info de empresa), `leer_preferencias` (configuración), `consulta_avanzada` (QBO query language con whitelist SQL — bloquea DROP/DELETE/UPDATE/INSERT/ALTER/CREATE, max 1000 resultados). Módulo nuevo: `dexter/tools/read.py`.

**Sprint 2 — Recurring+Attachments (2 tools):**
- `crear_recurringtransaction` (plantilla automática con intervalos Daily/Weekly/Monthly/Quarterly/Yearly), `adjuntar_archivo` (PDF/imagen vía multipart manual con base64, sin requests-toolbelt). Módulo nuevo: `dexter/tools/recurring.py`.

**Sprint 3 — P2 avanzado (6 tools):**
- `crear_taxcode` (NON/TAX), `crear_taxrate` (tasas de impuesto), `leer_exchange_rate` (multi-moneda), `ejecutar_batch` (max 30 ops/llamada, reduce latencia), `cdc_query` (Change Data Capture para sync incremental), `crear_budget` (presupuestos). Módulo nuevo: `dexter/tools/advanced.py`.

### 🆕 Agregado — Safeguards de integridad del registry (3 capas)

**Problema:** agregar un `tool_xxx()` en `main.py` sin registrarlo en `dexter/tools/<modulo>.py` (SCHEMA + FUNCTIONS) resulta en tools que existen pero el LLM no puede llamar.

**Solución: 3 capas de defensa** (ver [`SAFEGUARDS.md`](SAFEGUARDS.md)):

- **Layer 1 — Runtime:** `verify_tool_integrity(verbose=False)` en `dexter/tools/__init__.py`. Auto-verify on import. Detecta:
  - **Orphans:** `tool_*` wrappers en main.py que NO están en `ALL_FUNCTIONS` (LLM no los ve).
  - **Unwired:** entradas en `ALL_FUNCTIONS` sin schema correspondiente.
  - **Not dispatched:** schemas en `ALL_SCHEMAS` que NO están en `main.TOOL_FUNCTIONS` (LLM los ve pero dispatch falla con 'Tool no encontrado' → 'límite de iteraciones').
  - **Signature mismatches:** signature de `tool_xxx` incompatible con schema (params requeridos en schema no aceptados por signature, o viceversa) — causa `TypeError` en runtime → 'límite de iteraciones'.
  - Opt-in strict via `os.environ["DEXTER_STRICT_INTEGRITY"]="1"` → raise `RuntimeError`.
- **Layer 2 — CLI:** `scripts/verify_tool_integrity.py` standalone. Exit 0 si ok, exit 1 si gaps. Útil para CI.
- **Layer 3 — Pre-commit hook:** `.githooks/pre-commit` (trackeable en git). Bloquea `git commit` si hay gaps. Configurar: `git config core.hooksPath .githooks`. Para forzar: `git commit --no-verify`.

**Bugs reales cazados durante desarrollo:**

1. **`tool_procesar_lote_bills` no estaba en `dexter/tools/ocr.py`** (solo `procesar_lote_bills` sin prefijo `tool_`). Sin el safeguard, el LLM no habría podido llamar este tool. Fix: wrapper en main.py + import fix en ocr.py.
2. **57 tools sin dispatch en `TOOL_FUNCTIONS`** (todos los de Sprints 1+2+3: `crear_cliente`, `crear_vendor`, `actualizar_*`, `reporte_*`, etc.). El LLM llamaba el tool → main.py respondía "Tool no encontrado" → iteración se repetía → "límite de iteraciones" alcanzado. Usuario no podía crear clientes. **Bug crítico detectado por el safeguard extendido**. Fix: agregar 58 entries a `TOOL_FUNCTIONS` en main.py (organizados por sprint 1A/1B/1C/1E/1F/2/3 + admin).

**Tests:** 11 nuevos en `tests/test_tools_aggregator.py:TestVerifyToolIntegrity` (test_result_keys_present, test_baseline_no_orphans, test_detects_injected_orphan, test_verbose_writes_to_stderr_on_failure, test_verbose_silent_when_ok, test_total_wrappers_count, test_result_keys_include_dispatch_check, test_all_schemas_are_dispatched, test_verbose_dispatch_failure_mentions_dispatch, test_result_keys_include_signature_check, test_all_signatures_match_schemas).

### 🔄 Cambiado
- `qbo_request()` pineado con `?minorversion=70` (configurable via env `QB_MINOR_VERSION`) — protege contra breaking changes de QBO API.
- `main.py` ahora tiene ~5,253 líneas (era 3,608) con 100 wrappers `tool_*` y 40+ helpers nuevos. Shim 100% backward compat preservado.
- `dexter/tools/__init__.py` ahora registra 23 archivos (21 módulos + 2 infra) con 100 ALL_SCHEMAS / 100 ALL_FUNCTIONS (era 46).
- `tests/test_tools_aggregator.py` actualizado: `test_total_100_tools` (era `test_count_is_46` → `test_count_is_94` → `test_total_100_tools`).
- `dexter/tools/ocr.py` ahora importa `tool_procesar_lote_bills` (wrapper) en vez de `procesar_lote_bills` (función interna) — consistencia con el patrón wrapper.

### 📊 Métricas
- **Tests:** 311 → 359 pasando (+48 nuevos: 31 Sprints + 6 P2 reports + 11 safeguards + 6 error_log preexisting).
- **Tools:** 46 → 100 (+54 nuevos, 117% más).
- **Módulos:** 14 → 21 (+7 nuevos).
- **main.py:** 3,608 → 5,295 líneas (+1,687) — incluye 100 entries en `TOOL_FUNCTIONS` (era 43) + 58 entries nuevos agregados en este fix.
- **Cobertura QBO API:** 45% → 93% (gap residual: 4 P2 opcionales: `crear_companycurrency`, `actualizar_preferences`, `actualizar_companyinfo`, `webhook_setup`).
- **Bug fix end-to-end:** `crear_cliente` ahora funciona — verificado con llamada real a QBO sandbox (cliente ID 62 creado).
- **4ª capa de safeguard añadida:** signature compatibility check (evita `TypeError` en runtime por mismatch schema↔función).

---

## [Released] - 2026-06-04

### 🆕 Agregado
- **`crear_cliente` (tool)**: crea clientes (Customers) en QBO vía API. Antes el LLM tenía que decir "no tengo esa función" — ahora es first-class. Solo requiere `nombre` (DisplayName); opcionales `email`, `telefono`, `direccion`, `empresa`. Agregado a `dexter/tools/transactions.py` (módulo pasa de 4 → 5 tools).
- **`ver_log_errores` y `limpiar_log_errores` (tools)**: permiten inspeccionar y limpiar el log de errores persistido desde dentro de Dexter. Agregados a `dexter/tools/admin.py` (módulo pasa de 2 → 4 tools).
- **`dexter/error_log.py`**: sistema centralizado de logging de errores. Persiste cada error en `logs/dexter_errors.log` (formato JSON Lines rotado a 5 MB × 3 backups). API: `log_error(error, category, user_input, tool_name, company, extra)`, `get_recent_errors(n)`, `tail_log(n)`, `clear_log()`. Categorías: `api_call`, `tool_dispatch`, `user_input`, `auth`, `unknown`.
- **Integración automática del log en main.py**:
  - `qbo_request()` loggea cada respuesta 4xx/5xx con `category="api_call"` + extra `endpoint`, `status_code`, `response_preview`, `request_data_preview`
  - `refresh_qb_token()` loggea fallos de refresh con `category="auth"`
  - Tool dispatch (call_llm inner loop) loggea excepciones de tools con `category="tool_dispatch"`, `tool_name`, `arguments`, `user_message`
  - `main_loop()` loggea excepciones no atrapadas con `category="user_input"`, `user_input`, `company`
- **`scripts/oauth_flow.py`**: script para hacer el OAuth flow INICIAL (no solo refresh). Spawnea HTTP server en puerto 8000, abre el navegador, captura el callback, intercambia code por tokens, guarda en `.env` con `QB_ACCESS_TOKEN` + `QB_REFRESH_TOKEN` + `QB_REALM_ID`. Imprime resumen sin echo de tokens. Necesario para conectar empresas nuevas (sandbox, producción) que aún no tienen tokens.
- **Tests**: nuevo `tests/test_error_log.py` con 13 tests (JSONL format, append, ISO 8601, get_recent, tail, clear, extra, etc.) + 6 tests en `test_tools_aggregator.py` para los nuevos tools. **Total: 311/311 pasando** (era 287).
- **Setup multi-empresa documentado**: ahora `.env` puede apuntar a sandbox O producción, y `oauth_flow.py` regenera tokens sin perder configuración. `companies/<nombre>/meta.json` guarda tokens por empresa con aislamiento.

### 🔄 Cambiado
- `.gitignore` actualizado: agregados `companies/`, `secrets/`, `logs/`, `outputs/`, `.current_company`, `Backup/`, `Test/`, `Pending bills/*.pdf`, `Bank Reconciliation/*.txt`, `test_results.json`. Reduce ruido de untracked files.
- Routing keywords de `transactions.py`: agregados `"cliente"`, `"customer"`, `"nuevo cliente"` para que el LLM active `crear_cliente` cuando el usuario lo pida.
- Routing keywords de `admin.py`: agregados `"log"`, `"error"`, `"errores"`, `"diagnóstico"` para activar las nuevas tools de log.
- `_schema_utils.py` se mantiene sin cambios (no se usó para esta entrega pero está disponible).

### 🐛 Fixed
- **LXM: el LLM reportaba "no tengo acceso a la función agregar_cliente"** porque la tool no existía. Ahora existe (`crear_cliente`) y está expuesta correctamente. Cliente `AlfredoTPM` creado en sandbox como verificación end-to-end (ID 61).
- **Loop de errores silenciosos**: antes, los errores en tool_dispatch solo se imprimían a stdout (`traceback.print_exc()`) y se perdían al cerrar la sesión. Ahora se persisten en disco y pueden revisarse post-mortem con `tail_log()`.
- **Tokens stale en `.env`**: cuando el usuario cambia de empresa o re-autentica, ahora `oauth_flow.py` actualiza `.env` automáticamente (antes solo `refresh_token.py` actualizaba y solo funcionaba si ya había tokens).

### ⚠️ Backward compatibility
- **main.py: 3,608 líneas (era 3,551 — +57 líneas por las 2 nuevas tool wrappers + integración del log).** 0 funciones removidas. Shim de dexter.tools intacto.
- `from main import tool_xxx` sigue funcionando para los 26 tool_xxx definidos (24 previos + 2 nuevos).
- `get_relevant_tools()` y `TOOL_FUNCTIONS` se actualizan automáticamente vía el registry agregador.

### 📊 Métricas
- **main.py**: 3,608 líneas (era 3,551 — +57)
- **dexter/**: 17 archivos (era 15 — +2: `error_log.py` + `scripts/oauth_flow.py`)
- **Tests**: 311/311 pasando (era 287) — **+24 tests** (13 error_log + 6 aggregator + 5 admin/log)
- **Tools**: 46 totales (era 43 — +3: `crear_cliente`, `ver_log_errores`, `limpiar_log_errores`)
- **Dominios de tools**: 14 (sin cambios — `dexter/error_log.py` es cross-cutting, no un tool del LLM)
- **Categorías de error**: 5 (`api_call`, `tool_dispatch`, `user_input`, `auth`, `unknown`)
- **Capacidad de log**: 5 MB × 3 backups = 20 MB máximo de logs en disco

- **Refactor monolítico → arquitectura modular (Fases 0-7 completadas)**: 14 módulos en `dexter/tools/` con registry agregador
  - `dexter/tools/_schema_utils.py` — helpers `make_schema`, `prop_str`/`prop_num`/`prop_bool`/`prop_list`
  - `dexter/tools/__init__.py` — registry agregador con `ALL_SCHEMAS`, `ALL_FUNCTIONS`, `KEYWORDS_BY_MODULE` (data-driven routing)
  - `dexter/tools/bank_feed.py` (5 tools), `search.py` (4), `transactions.py` (5) ⬆️, `reports.py` (5), `tokens.py` (2), `admin.py` (4) ⬆️, `batch.py` (3), `reconciliation.py` (3), `ocr.py` (1), `behavior.py` (4), `report_custom.py` (2), `api_explorer.py` (5), `journal.py` (2), `web_code.py` (1)
- **Data-driven tool routing**: cada módulo declara sus `KEYWORDS`, `get_relevant_tools()` en main.py itera los 14 módulos para activar tools relevantes
- **Shim de backward compat**: `from main import tool_xxx` sigue funcionando (24 tool_xxx en main.py, 19 tool_xxx via dexter.tools)
- **Tests del agregador**: 11 tests de wiring + 3 tests parametrizados de los 14 dominios + 2 tests de shim. **287 tests pasando** (era 262)
- **Investigación "stubs fantasma"**: empíricamente demostrado que **NO HAY STUBS FANTASMA**. Los 43 tools son reales. El análisis previo usó un grep con regex malo que no detectó los nombres de tools en el dict `TOOL_FUNCTIONS`. `dexter/tools/` ahora cubre los 43 tools wireados.
- **Spec del refactor**: `docs/superpowers/specs/2026-06-04-refactor-main-tools-design.md`
- **Plan de implementación**: `docs/superpowers/plans/2026-06-04-refactor-fase-0-1-tools-bank-feed.md`

### 🔄 Cambiado
- `main.py`: `get_relevant_tools` reescrito de 27 hardcoded tool names a data-driven (43 tools, 14 dominios)
- `main.py`: `show_main_menu` ahora dice "43 tools disponibles en 14 dominios" (antes decía 27)
- `main.py`: 4 re-exports Fase 1 (bank_feed intelligence) + alias `ALL_SCHEMAS_DEXTER`/`ALL_FUNCTIONS_DEXTER` del agregador
- `dexter/tools/process_bank_feed.py` eliminado (duplicaba `procesar_bank_feed_csv` que ya está en `bank_feed.py`)

### ⚠️ Backward compatibility
- **main.py: 3,551 líneas, 0 funciones removidas.** Todos los tools viejos siguen funcionando con la misma firma.
- `from main import tool_xxx` funciona para los 24 tool_xxx definidos en main.py
- `from main import TOOLS` / `TOOL_FUNCTIONS` / `main_loop` / `call_llm` / `get_relevant_tools` / `build_conversation_context` sin cambios
- Los tests existentes (test_suite.py, test_main_loop.py) corren sin modificación

### 📊 Métricas
- **main.py**: 3,551 líneas (era 3,505 — +46 líneas por shim + comentarios de fase)
- **dexter/tools/**: 16 archivos (14 módulos + 2 infra), 6,635 líneas totales
- **Tests**: 287/287 pasando (era 262) — **+25 tests** (11 aggregator + 2 shim + 3 domain coverage + 9 verificados)
- **Tools**: 43 totales (era 27 hardcoded en `get_relevant_tools`, pero 43 wireados en `TOOL_FUNCTIONS`)
- **Dominios**: 14 (bank_feed, search, transactions, reports, tokens, admin, batch, reconciliation, ocr, behavior, report_custom, api_explorer, journal, web_code)

### 🐛 Fixed
- `get_relevant_tools` solo enviaba 27 tools al LLM (hardcoded), aunque había 43 disponibles. Los 16 tools sin keyword match nunca se mostraban al LLM. Ahora data-driven, los 43 pueden activarse.
- Mensaje "27 tools disponibles" en `show_main_menu` era incorrecto (realmente son 43)
- `process_bank_feed.py` huérfano — duplicaba funcionalidad ya en `bank_feed.py`

## [3.7.0] - 2026-01-23 — Guía Interactiva y Matching Engine

### 🔄 Cambiado
- `autonomia/bank_feed_intelligence.py`: reescrito con motor de matching en cascada (exacto → regex → fuzzy → default), confidence 0-100%. Las 3 funciones `tool_*` que eran stubs ahora funcionan end-to-end
- `autonomia/user_behavior_learning.py`: motor completo de aprendizaje con learn_account/vendor/report_preference, record_correction (con threshold), get_suggestions, active_tasks. Singleton reseteable para tests
- `autonomia/dynamic_report_generator.py`: parse_date_expression con 14+ patrones (meses, trimestres, Q1-Q4, últimos N días, ISO, es/en). detect_report_type para 4 tipos de reporte (orden importa: TrialBalance antes de BalanceSheet). generate_custom_report llama QBO API real
- `autonomia/autonomia_nivel2_api_explorer.py`: registry de 26 endpoints QBO con description + methods + category. tool_list_qbo_endpoints soporta filtro por categoría
- `ocr_bills.py`: nueva función `procesar_lote_ocr()` itera sobre todos los PDFs de una carpeta. Import de Gemini ahora es lazy (módulo importable sin la dependencia)
- `ocr_bills.py`: nueva función `validar_bill_minimo()` descarta extracciones inválidas
- `main.py`: `tool_obtener_estadisticas_tokens` ahora soporta `"sesion"`, `"dia"`, `"mes"`, `"YYYY-MM-DD"`, `"YYYY-MM"` (antes solo "sesion")
- `main.py`: `tool_generar_informe_tokens` ahora retorna summary estructurado (totales, promedios) además de generar el Excel
- `main.py`: `get_relevant_tools` añade keywords `recon`/`tag`/`marcar`/`lote`/`batch`/`depositar csv`
- `main.py`: `process_quick_command` detecta "recon tag" / "lote csv" / "depositar batch" e imprime guía

### 🐛 Fixed
- **Stub crítico**: `tool_find_pattern_for_transaction` retornaba `match_found: False` siempre. Ahora sí matchea con confidence
- **Stub user_behavior_learning**: `tool_get_user_suggestions` retornaba `suggestion: None`. Ahora retorna sugerencias reales ordenadas por count
- **Stub user_behavior_learning**: `tool_record_user_correction` no persistía nada. Ahora guarda en JSON con threshold
- **Stub dynamic_report_generator**: solo soportaba 3 expresiones ("este mes", "mes pasado", "este año"). Ahora 14+ patrones
- **Stub api_explorer**: `tool_list_qbo_endpoints` solo tenía 6 endpoints sin info de métodos. Ahora 26 con description + methods + category
- **OCR subutilizado**: `extraer_bills_de_pdf` solo procesaba 1 PDF. Ahora hay `procesar_lote_ocr` que itera sobre toda la carpeta
- **Módulo `autonomia` no testeable**: agregados tests para los 3 archivos de autonomía
- **Módulo `ocr_bills` no testeable**: agregados 19 tests con mock de Gemini
- **`tool_obtener_estadisticas_tokens` mentía**: prometía varios períodos pero solo soportaba `"sesion"`. Ahora sí lee del CSV histórico
- **`.gitignore` no se aplicaba**: estaba nombrado `gitignore` (sin punto). Renombrado a `.gitignore` + patterns nuevos para Dexter v4.0

### ⚠️ Backward compatibility
- **0 líneas removidas de main.py**. Todos los tools viejos siguen funcionando.
- Los nuevos tools BNK-RECON y batch deposits son **opt-in**: el LLM los elige si la conversación lo amerita.

## [3.7.0] - 2026-01-23 — Guía Interactiva y Matching Engine

### 🆕 Agregado
- **Guía Interactiva (Onboarding)**: Dexter detecta el estado de las carpetas (`Pending bills/`, `Bank Reconciliation/`, etc.) y ofrece guiar al usuario paso a paso en tareas complejas (OCR, Reconciliación)
- **Matching Engine (Bank Feed)**: diseño técnico del motor de conciliación inteligente entre CSVs bancarios y registros existentes en QBO para evitar duplicidades
- **Manual de Usuario Vivo**: `USER_GUIDE.md` integrado como base de conocimiento primaria del agente para su propia auto-explicación
- Banner minimalista rediseñado para máxima compatibilidad con terminales Linux y macOS
- Tono dinámico: comportamiento más proactivo, educativo y cercano al usuario

### 🔄 Cambiado
- Reconstrucción estructural de `main.py`: auditoría de sintaxis, eliminación de bloques truncados y resolución de `SyntaxError`
- Restauración del `SYSTEM_PROMPT` y de la función `call_llm` (orquestación de tool calls)
- Eliminación de llamadas recursivas y código duplicado al final del script
- Normalización de imports y vinculación explícita de `company_manager.py` con el núcleo
- Refactorización de `session_state` para rastreo dinámico de tokens y costos basado en el modelo (Hybrid Routing)

---

## [3.6.0] - 2026-01-23 — Inteligencia Híbrida y Bilingüe

### 🆕 Agregado
- **Model Routing híbrido**: Dexter decide entre Llama 3 (tareas simples, bajo costo) y DeepSeek V3 (análisis contable complejo) para optimizar costos y velocidad
- **Bilingüe ES/EN oficial**: sistema de traducción dinámica con persistencia de idioma guardada por empresa en `meta.json`

### 🔄 Cambiado
- El LLM por defecto del proyecto es ahora híbrido: ya no solo DeepSeek V3
- Costo por sesión reducido aún más (Llama 3 ≈ 10× más barato que DeepSeek V3)

---

## [3.5] - 2026-01-23 — Multi-Empresa PRO

### 🆕 Agregado
- **Sistema Multi-Empresa PRO**: gestión ilimitada de empresas con tokens aislados
- **`company_manager.py`**: módulo de gestión de empresas con extracción automática de Realm ID
- **Hot-swap de empresa**: cambio sin reiniciar la aplicación
- **Persistencia por empresa**: `companies/<nombre>/meta.json` con tokens, chart y reportes aislados
- **`gestionar_empresas`**: nuevo function tool (32 total)
- **Identidad "Dexter"**: asistente renombrado con personalidad profesional y amigable

### 🔄 Cambiado
- Nombre del asistente: de "Asistente TMP AI" a **Dexter**
- Total de function tools: de 31 a **32** (incluye `gestionar_empresas`)
- Conteo de líneas: de ~2,500 a ~3,000 líneas

---

## [3.0] - 2026-01-20 — Autonomía y Optimización

### 🆕 Agregado
- **Optimización de tokens (57% reducción)**: herramientas dinámicas, sliding window, system prompt condicional
- **6 Módulos de Autonomía** en `autonomia/` con 18 funciones avanzadas:
  - Nivel 1: Web Search (búsqueda web + docs QBO)
  - Nivel 2: API Explorer (journal entry, transfer, generic request, list endpoints, info endpoint)
  - Nivel 3: Code Executor (ejecutar Python dinámicamente)
  - Bank Feed Intelligence (clasificación inteligente de transacciones)
  - User Behavior Learning (aprendizaje de patrones del usuario)
  - Dynamic Report Generator (reportes personalizados con lenguaje natural)
- **OCR de Bills PDF** con Gemini Flash 2.0
- **18 nuevos function tools** (de 13 a 31 totales)
- **Bilingüe ES/EN** en system prompt
- **Sliding window** de historial (5 turnos)

### 🔄 Cambiado
- System prompt: de estático (~120 líneas) a dinámico (~25 líneas + contexto)
- Caché del chart: latencia de 3s → 0.1s
- Costo por sesión: ~40% de reducción

---

## [2.0] - 2026-01-15 — DeepSeek V3 y Function Calling

### 🆕 Agregado
- **Migración a DeepSeek V3** vía OpenRouter con function calling
- **13 function tools básicos**: búsquedas (4), transacciones (4), reportes (3), gestión (2)
- **Procesamiento CSV batch** con validación
- **Bank Feed processing** con splits
- **Reconciliación bancaria** automatizada (dos modos: con/sin balance)
- **Sistema de tracking de tokens** con CSV histórico + Excel
- **Token usage** tracking con costo en USD

---

## [1.0] - 2026-01-08 — MVP Inicial

### 🆕 Agregado
- Asistente conversacional para QuickBooks Online en español
- Autenticación OAuth 2.0 con QuickBooks
- Chart of Accounts con fuzzy matching
- Comandos rápidos (sin consumo de tokens): `refrescar chart`, `template csv`, `listar reportes`, `salir`
- Integración con DeepSeek V3 (sin function calling todavía)
- Caché local del chart de cuentas
- 4 funciones básicas: buscar cliente, crear depósito, generar reporte, listar reportes

---

## Tipos de cambios

- 🆕 **Agregado** — para funcionalidades nuevas
- 🔄 **Cambiado** — para cambios en funcionalidades existentes
- ⚠️ **Deprecado** — para funcionalidades que se eliminarán pronto
- 🗑️ **Eliminado** — para funcionalidades eliminadas
- 🐛 **Corregido** — para corrección de bugs
- 🔒 **Seguridad** — para vulnerabilidades

---

**Mantenedor:** Alfredo
**Asistente:** Dexter (v3.7)
