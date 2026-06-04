# 📜 Changelog — QuickBooks AI Assistant

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased] - 2026-06-04

### 🆕 Agregado
- **Refactor monolítico → arquitectura modular (Fases 0-7 completadas)**: 14 módulos en `dexter/tools/` con registry agregador
  - `dexter/tools/_schema_utils.py` — helpers `make_schema`, `prop_str`/`prop_num`/`prop_bool`/`prop_list`
  - `dexter/tools/__init__.py` — registry agregador con `ALL_SCHEMAS`, `ALL_FUNCTIONS`, `KEYWORDS_BY_MODULE` (data-driven routing)
  - `dexter/tools/bank_feed.py` (5 tools), `search.py` (4), `transactions.py` (4), `reports.py` (5), `tokens.py` (2), `admin.py` (2), `batch.py` (3), `reconciliation.py` (3), `ocr.py` (1), `behavior.py` (4), `report_custom.py` (2), `api_explorer.py` (5), `journal.py` (2), `web_code.py` (1)
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
