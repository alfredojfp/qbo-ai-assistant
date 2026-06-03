# 📜 Changelog — QuickBooks AI Assistant

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

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
**Asistente:** Dexter (v3.5+)
