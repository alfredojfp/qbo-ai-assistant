# 📜 Changelog — QuickBooks AI Assistant

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased] - 2026-06-03

### 🆕 Agregado
- **Motor batch genérico** (`dexter/core/batch/`) con state machine, persistencia SQLite, audit log completo
- **Skill de bank deposits multi-cliente** con desambiguación interactiva (resuelve clientes nuevos en QBO)
- **Documentación**: `docs/BATCH_ENGINE.md` con guía completa del nuevo sistema
- **128 tests unitarios** (`unittest` stdlib, sin dependencias)

### 🔄 Cambiado
- `autonomia/bank_feed_intelligence.py`: reescrito con motor de matching en cascada (exacto → regex → fuzzy → default), confidence 0-100%. Las 3 funciones `tool_*` que eran stubs ahora funcionan end-to-end
- `ocr_bills.py`: nueva función `procesar_lote_ocr()` itera sobre todos los PDFs de una carpeta. Import de Gemini ahora es lazy (módulo importable sin la dependencia)
- `ocr_bills.py`: nueva función `validar_bill_minimo()` descarta extracciones inválidas

### 🐛 Fixed
- **Stub crítico**: `tool_find_pattern_for_transaction` retornaba `match_found: False` siempre. Ahora sí matchea con confidence
- **OCR subutilizado**: `extraer_bills_de_pdf` solo procesaba 1 PDF. Ahora hay `procesar_lote_ocr` que itera sobre toda la carpeta
- **Módulo `autonomia` no testeable**: agregados 27 tests para `bank_feed_intelligence`
- **Módulo `ocr_bills` no testeable**: agregados 19 tests con mock de Gemini

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
