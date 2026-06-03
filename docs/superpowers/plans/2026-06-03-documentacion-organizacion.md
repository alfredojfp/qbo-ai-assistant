# Plan de Implementación: Organización y Documentación Integral

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convertir el proyecto QuickBooks AI Assistant (TMP AI / Dexter v3.5) en un repositorio autoexplicativo con un README raíz como hub, docs sincronizados a v3.5 y documentos especializados para vacíos actuales.

> **Nota (2026-06-03, post-ejecución):** Este plan fue ejecutado en su totalidad. La versión actual del proyecto es **v3.7.0** (Guía Interactiva + Matching Engine, construida sobre v3.6 Inteligencia Híbrida y v3.5 Multi-Empresa). La documentación fue posteriormente sincronizada a v3.7. Ver [`../CHANGELOG.md`](../CHANGELOG.md) para el historial completo.

**Architecture:** 12 tareas secuenciales. Primero movimientos físicos de carpetas, luego creación de documentos nuevos, luego sincronización de existentes, finalmente creación del README raíz. Sin tocar código.

**Tech Stack:** Markdown, Git, sistema de archivos. Sin código.

**Spec de referencia:** `docs/superpowers/specs/2026-06-03-documentacion-organizacion-design.md`

---

## 📋 Política de commits

**IMPORTANTE:** Cada tarea incluye un paso de commit, pero el usuario NO ha autorizado commits automáticos. El agente ejecutor debe:

1. Completar todos los pasos de la tarea
2. **Pausa** antes del paso de commit
3. Preguntar al usuario: "¿Commitear los cambios de esta tarea? (sí/no)"
4. Solo hacer commit si la respuesta es "sí"
5. Si el usuario dice "no, commitea todo al final", acumular cambios y commitear al final de las 12 tareas

Si el usuario da autorización global al inicio ("sí, commitea todo"), entonces ejecutar los commits automáticamente.

---

## 📁 Estructura de archivos

### Archivos a crear (7 + 1 spec ya creado)

| Path | Líneas | Propósito |
|------|--------|-----------|
| `README.md` | ~600-700 | Hub raíz, índice, ejemplo rápido |
| `docs/CHANGELOG.md` | ~150 | Historial versionado v1.0 → v3.5 |
| `docs/INSTALL.md` | ~150 | Instalación detallada |
| `docs/ARCHITECTURE.md` | ~400 | Diagramas, dataflow, patrones |
| `docs/CAPACIDADES.md` | ~500 | Catálogo de 31+ tools y 6 módulos |
| `docs/MULTI_EMPRESA.md` | ~200 | Guía específica v3.5 |
| `docs/USER_GUIDE.md` | ~350 | Refactor de MANUAL_USUARIO.md |

### Archivos a actualizar (4)

| Path | Cambio |
|------|--------|
| `docs/README.md` | Reescrito a v3.5 + tabla de contenidos |
| `docs/CONTEXT.md` | Sincronizar menciones (Dexter, 31+ tools, multi-empresa) |
| `docs/EXAMPLES.md` | Añadir 3-5 ejemplos nuevos (multi-empresa, OCR, Dexter) |
| `docs/TROUBLESHOOTING.md` | Añadir sección multi-empresa |

### Archivos a mover (6)

| Origen | Destino |
|--------|---------|
| `ROADMAPDOCS/ROADMAP.md` | `docs/roadmap/ROADMAP.md` |
| `ROADMAPDOCS/DEVELOPMENT_LOG.md` | `docs/roadmap/DEVELOPMENT_LOG.md` |
| `ROADMAPDOCS/MEMORIA_Y_ARQUITECTURA.md` | `docs/roadmap/MEMORIA_Y_ARQUITECTURA.md` |
| `ROADMAPDOCS/MATCHING_ENGINE_BANK_FEED.md` | `docs/roadmap/MATCHING_ENGINE_BANK_FEED.md` |
| `ROADMAPDOCS/ANALISIS_FINANCIERO_PRO.md` | `docs/roadmap/ANALISIS_FINANCIERO_PRO.md` |
| `ROADMAPDOCS/TODO.TEXT` | `docs/roadmap/TODO.TEXT` |
| `docs/MANUAL_USUARIO.md` | `docs/USER_GUIDE.md` (renombrado, no movido) |

### Archivos NO modificados (fuera de scope)

- Código: `main.py`, `company_manager.py`, `ocr_bills.py`, `gitmanager.py`, `install.sh`
- Paquetes: `autonomia/*`, `scripts/*`
- Datos: `Bank Reconciliation/`, `Pending bills/`, `Processed bills/`, `Backup/`, `outputs/`, `templates/`, `Test/`
- Config: `.env`, `.gitignore`, `.venv/`, `__pycache__/`
- El spec ya creado: `docs/superpowers/specs/2026-06-03-documentacion-organizacion-design.md`

---

## Tarea 1: Mover ROADMAPDOCS/ → docs/roadmap/

**Archivos:**
- Mover (origen → destino): 6 archivos listados arriba

- [ ] **Paso 1: Verificar origen**

```bash
ls -la "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/ROADMAPDOCS/"
```

Esperado: 6 archivos listados (ROADMAP.md, DEVELOPMENT_LOG.md, MEMORIA_Y_ARQUITECTURA.md, MATCHING_ENGINE_BANK_FEED.md, ANALISIS_FINANCIERO_PRO.md, TODO.TEXT)

- [ ] **Paso 2: Crear directorio destino**

```bash
mkdir -p "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/roadmap"
```

- [ ] **Paso 3: Mover archivos**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
mv ROADMAPDOCS/ROADMAP.md docs/roadmap/ROADMAP.md
mv ROADMAPDOCS/DEVELOPMENT_LOG.md docs/roadmap/DEVELOPMENT_LOG.md
mv ROADMAPDOCS/MEMORIA_Y_ARQUITECTURA.md docs/roadmap/MEMORIA_Y_ARQUITECTURA.md
mv ROADMAPDOCS/MATCHING_ENGINE_BANK_FEED.md docs/roadmap/MATCHING_ENGINE_BANK_FEED.md
mv ROADMAPDOCS/ANALISIS_FINANCIERO_PRO.md docs/roadmap/ANALISIS_FINANCIERO_PRO.md
mv ROADMAPDOCS/TODO.TEXT docs/roadmap/TODO.TEXT
rmdir ROADMAPDOCS
```

- [ ] **Paso 4: Verificar movimiento**

```bash
ls -la "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/roadmap/"
ls -la "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/ROADMAPDOCS" 2>&1 | head -3
```

Esperado: 6 archivos en `docs/roadmap/`; el segundo comando debe fallar con "No such file or directory".

- [ ] **Paso 5: Preguntar y commitear (condicional)**

Preguntar al usuario. Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add -A
git status
git commit -m "docs: move ROADMAPDOCS/ to docs/roadmap/"
```

---

## Tarea 2: Renombrar MANUAL_USUARIO.md → USER_GUIDE.md

**Archivos:**
- Renombrar: `docs/MANUAL_USUARIO.md` → `docs/USER_GUIDE.md`

- [ ] **Paso 1: Verificar archivo origen**

```bash
ls -la "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/MANUAL_USUARIO.md"
```

Esperado: archivo existe con ~3.6KB.

- [ ] **Paso 2: Renombrar**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
mv docs/MANUAL_USUARIO.md docs/USER_GUIDE.md
```

- [ ] **Paso 3: Verificar**

```bash
ls -la "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/USER_GUIDE.md"
ls "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/MANUAL_USUARIO.md" 2>&1 | head -2
```

Esperado: USER_GUIDE.md existe, MANUAL_USUARIO.md no.

- [ ] **Paso 4: Preguntar y commitear (condicional)**

Si el usuario autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add -A
git commit -m "docs: rename MANUAL_USUARIO.md to USER_GUIDE.md (standardized naming)"
```

---

## Tarea 3: Crear docs/CHANGELOG.md

**Archivos:**
- Crear: `docs/CHANGELOG.md`

- [ ] **Paso 1: Crear archivo con contenido inicial**

```bash
touch "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/CHANGELOG.md"
```

- [ ] **Paso 2: Escribir contenido completo**

Usar la herramienta `write` con el siguiente contenido:

```markdown
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
- **`docs/MULTI_EMPRESA.md`**: guía específica de la funcionalidad (post-organización)

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
```

- [ ] **Paso 3: Verificar**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/CHANGELOG.md"
head -20 "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/CHANGELOG.md"
```

Esperado: ~150 líneas, primeras líneas son el header del changelog.

- [ ] **Paso 4: Preguntar y commitear (condicional)**

Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add docs/CHANGELOG.md
git commit -m "docs: add CHANGELOG.md with v1.0 to v3.5 history"
```

---

## Tarea 4: Crear docs/INSTALL.md

**Archivos:**
- Crear: `docs/INSTALL.md`

- [ ] **Paso 1: Crear archivo y escribir contenido**

Usar la herramienta `write` con:

```markdown
# 🚀 Guía de Instalación Detallada

Instrucciones paso a paso para instalar y configurar QuickBooks AI Assistant (Dexter).

---

## 📋 Prerrequisitos

| Requisito | Versión | Cómo verificar |
|-----------|---------|----------------|
| Python | 3.9 o superior | `python --version` |
| pip | 21+ | `pip --version` |
| Git | 2.30+ | `git --version` |
| Cuenta QuickBooks Online | Sandbox o Producción | [developer.intuit.com](https://developer.intuit.com) |
| API Key de OpenRouter | Activa | [openrouter.ai](https://openrouter.ai) |
| API Key de Google Gemini | Activa | [aistudio.google.com](https://aistudio.google.com) (para OCR) |

---

## 🪜 Instalación paso a paso

### Paso 1: Clonar o descargar el proyecto

```bash
git clone <url-del-repo>
cd "Qbo Scripts"
```

Si ya tienes el proyecto, solo navega al directorio:

```bash
cd "/ruta/a/Qbo Scripts"
```

### Paso 2: Crear entorno virtual

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### Paso 3: Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Configurar credenciales

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales (ver sección [Variables de entorno](#-variables-de-entorno)).

### Paso 5: Configurar OAuth 2.0 con QuickBooks

1. Ve a [developer.intuit.com](https://developer.intuit.com) y crea una app
2. En la sección "Keys & OAuth", obtén tu `Client ID` y `Client Secret`
3. Configura redirect URI: `http://localhost:8000/callback` (o el que prefieras)
4. Autoriza la app contra tu empresa QBO: el script `scripts/refresh_token.py` te guiará
5. Tras autorizar, copia el `access_token` y `refresh_token` al `.env`

### Paso 6: Verificar instalación

```bash
python scripts/verify_setup.py
```

Salida esperada: todos los checks en verde ✅.

### Paso 7: Primer arranque

```bash
python main.py
```

Al iniciar, si tienes múltiples empresas configuradas, Dexter te preguntará con cuál trabajar.

---

## 🔐 Variables de entorno

| Variable | Descripción | Obligatoria |
|----------|-------------|-------------|
| `QB_ACCESS_TOKEN` | Token de acceso QBO (se refresca automáticamente) | Sí |
| `QB_REFRESH_TOKEN` | Token para refrescar el access token | Sí |
| `QB_CLIENT_ID` | Client ID de tu app QBO | Sí |
| `QB_CLIENT_SECRET` | Client Secret de tu app QBO | Sí |
| `QB_REALM_ID` | ID de la empresa QBO (Company ID) | Sí |
| `OPENROUTER_API_KEY` | API key de OpenRouter para DeepSeek V3 | Sí |
| `GEMINI_API_KEY` | API key de Google Gemini (solo si usas OCR) | No (recomendada) |

**Importante:**
- ❌ NUNCA subas `.env` a Git
- ✅ El archivo `.gitignore` ya excluye `.env`
- ✅ Para múltiples empresas, usa `company_manager.py` que gestiona los tokens por empresa

---

## 🐛 Troubleshooting de instalación

### Error: "No module named 'requests'"

```bash
# Asegúrate de tener el venv activado
source .venv/bin/activate  # o equivalente en Windows
pip install -r requirements.txt
```

### Error: "QB_ACCESS_TOKEN is missing"

Edita `.env` y agrega las credenciales. Ver [Paso 4](#paso-4-configurar-credenciales).

### Error: "Invalid client_id or client_secret"

Verifica que copiaste correctamente las credenciales desde developer.intuit.com, sin espacios extra.

### Error: "Token expired" persistente

```bash
python scripts/refresh_token.py
```

Si persiste, regenera el refresh token desde la app de Intuit.

### Error: "OPENROUTER_API_KEY is missing"

Crea una cuenta en [openrouter.ai](https://openrouter.ai) y obtén tu API key.

---

## ✅ Verificación final

Tras seguir todos los pasos, deberías poder:

- [x] Ejecutar `python main.py` sin errores
- [x] Ver el saludo de Dexter
- [x] Hacer una búsqueda de prueba: `"busca el cliente de prueba"`
- [x] Ver el chart de cuentas cargado

Si todo funciona, ¡ya estás listo para usar Dexter!

---

**Siguiente paso:** Lee [`USER_GUIDE.md`](USER_GUIDE.md) para aprender a usar el asistente.
```

- [ ] **Paso 2: Verificar**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/INSTALL.md"
```

Esperado: ~150 líneas.

- [ ] **Paso 3: Preguntar y commitear (condicional)**

Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add docs/INSTALL.md
git commit -m "docs: add detailed INSTALL.md guide"
```

---

## Tarea 5: Crear docs/ARCHITECTURE.md

**Archivos:**
- Crear: `docs/ARCHITECTURE.md`

- [ ] **Paso 1: Escribir contenido**

Usar la herramienta `write` con:

```markdown
# 🏗️ Arquitectura del Sistema

Documento técnico de referencia para desarrolladores que necesiten entender, mantener o extender QuickBooks AI Assistant (Dexter).

---

## 🎯 Visión general

Dexter es un agente conversacional en Python que conecta un LLM (DeepSeek V3) con la API de QuickBooks Online mediante function calling. La arquitectura está diseñada para:

- **Aislamiento de contexto por empresa** (v3.5+)
- **Optimización agresiva de tokens** (57% reducción vs v2.0)
- **Extensibilidad mediante módulos de autonomía** (6 módulos en `autonomia/`)

---

## 📐 Diagrama de componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUARIO (Alfredo)                       │
│                    Habla en español natural                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       main.py (3,000 líneas)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Loop conversacional                                     │  │
│  │ • System prompt dinámico                                  │  │
│  │ • 32 Function tools (JSON Schema)                         │  │
│  │ • Tracking de tokens (CSV + Excel)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────┬─────────────────────────┘
             │                          │
             ▼                          ▼
┌────────────────────────┐   ┌──────────────────────────────────┐
│  company_manager.py    │   │       autonomia/ (6 módulos)      │
│  • Multi-empresa       │   │  • nivel1: web search             │
│  • meta.json aislado   │   │  • nivel2: API explorer           │
│  • Hot-swap            │   │  • nivel3: code executor          │
│                        │   │  • bank feed intelligence         │
│                        │   │  • user behavior learning         │
│                        │   │  • dynamic report generator       │
└────────────┬───────────┘   └──────────────┬───────────────────┘
             │                               │
             ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APIs Externas                                │
│  • QuickBooks Online API v3 (REST)                              │
│  • OpenRouter → DeepSeek V3 (LLM)                               │
│  • Google Gemini Flash 2.0 (OCR)                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📂 Mapa de archivos del proyecto

| Archivo | Líneas | Responsabilidad |
|---------|--------|-----------------|
| `main.py` | ~3,000 | Loop conversacional, 32 tools, tracking, system prompt |
| `company_manager.py` | ~200 | Multi-empresa, `meta.json`, hot-swap |
| `ocr_bills.py` | ~150 | Extracción de datos de PDFs de facturas |
| `gitmanager.py` | 449 | Utilidad de versionado (commits, status, log) |
| `install.sh` | ~400 | Script de instalación automatizada |
| `autonomia/__init__.py` | <10 | Marca el directorio como paquete |
| `autonomia/nivel1_websearch.py` | ~80 | `search_web`, `search_qbo_docs` |
| `autonomia/nivel2_api_explorer.py` | ~150 | `create_journal_entry`, `create_transfer`, `qbo_generic_request`, etc. |
| `autonomia/nivel3_code_executor.py` | ~40 | `execute_python` |
| `autonomia/bank_feed_intelligence.py` | ~120 | 4 tools de clasificación inteligente |
| `autonomia/user_behavior_learning.py` | ~100 | 4 tools de aprendizaje de patrones |
| `autonomia/dynamic_report_generator.py` | ~70 | `generate_custom_report`, `parse_date_expression` |
| `scripts/verify_setup.py` | ~300 | Verificación pre-arranque |
| `scripts/refresh_token.py` | ~50 | Refresh manual de token OAuth |

---

## 🔄 Flujo de una solicitud

```
1. Usuario: "muéveme $2500 de Acme Retainers a Checking"
   │
   ▼
2. main.py recibe input
   │
   ├─→ get_relevant_tools(msg)         [filtra tools por keyword]
   ├─→ build_conversation_context()    [sliding window 5 turnos]
   └─→ necesita_chart(msg)?            [decide si incluir chart]
   │
   ▼
3. Llama a DeepSeek V3 con:
   • system_prompt (dinámico)
   • tools relevantes (filtrados)
   • historial (últimos 5 turnos)
   │
   ▼
4. DeepSeek decide tool calls:
   • buscar_cliente("Acme")
   • buscar_cuenta("Client Retainers")
   • buscar_cuenta("Checking")
   • crear_deposito(...)
   │
   ▼
5. main.py ejecuta cada tool (autonomía si está en autonomia/)
   │
   ├─→ Llamadas a QBO API
   ├─→ company_manager valida empresa activa
   └─→ tracking de tokens actualizado
   │
   ▼
6. DeepSeek genera respuesta final con resultados
   │
   ▼
7. Usuario ve respuesta con formato amigable
```

---

## 🏢 Multi-empresa (v3.5)

**Concepto clave:** Cada empresa tiene su propio `meta.json` con tokens, chart, reportes y bank feed aislados.

### Estructura de archivos

```
Qbo Scripts/
├── .env                      # Solo credenciales de la empresa por defecto
├── companies/
│   ├── acme_corp/
│   │   ├── meta.json         # Tokens, realm_id, contexto
│   │   ├── chart_of_accounts.json
│   │   ├── saved_reports.json
│   │   └── bank_feed_history.json
│   ├── tech_inc/
│   │   ├── meta.json
│   │   └── ...
│   └── ...
```

### Aislamiento por empresa

| Recurso | ¿Aislado por empresa? |
|---------|----------------------|
| Access Token | ✅ Sí (en `meta.json`) |
| Refresh Token | ✅ Sí (en `meta.json`) |
| Chart of Accounts | ✅ Sí |
| Saved Reports | ✅ Sí |
| Bank Feed History | ✅ Sí |
| User Behavior Patterns | ⚠️ Compartido (v3.5) |
| Token Usage CSV | ⚠️ Compartido (a nivel global) |

### Hot-swap

El usuario puede decir a Dexter: `"cambiar a Tech Inc"` y el sistema:
1. Guarda el contexto de la empresa actual
2. Carga el `meta.json` de Tech Inc
3. Refresca tokens si es necesario
4. Re-carga el chart of accounts
5. Continúa la conversación sin reiniciar

---

## 🧮 Optimización de tokens (57% reducción)

### 1. `get_relevant_tools(user_message)`

**Cómo funciona:**
- Detecta keywords en el mensaje del usuario
- Filtra tools irrelevantes antes de enviarlos al LLM
- Mantiene un set mínimo (search_customer, generate_pl_report) siempre incluido

**Ejemplo:**
```python
# Mensaje: "dame el P&L de enero"
# Tools enviados: [generar_reporte_pl, guardar_reporte] (2 tools)
# vs. todos los 32 tools si no se filtrara
```

**Ahorro:** ~40% de tokens en tool definitions.

### 2. `build_conversation_context(history, max_turns=5)`

**Cómo funciona:**
- Mantiene solo los últimos 5 turnos (10 mensajes) en el contexto
- Genera "context hints" con keywords detectados
- El historial completo se guarda en sesión pero no se envía

**Ahorro:** ~30% de tokens en historial.

### 3. `necesita_chart(msg)`

**Cómo funciona:**
- Si el mensaje menciona "cuenta", "clasificar", "bill", "journal": incluye chart summary
- Si no: omite el chart, system prompt más corto

**Ahorro:** ~25% de tokens en system prompt.

### Resultado combinado

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Tokens/llamada | ~8,000 | ~3,500 | -56% |
| Costo/sesión 45min | ~$0.012 | ~$0.005 | -58% |
| Latencia | 1.2s | 0.8s | -33% |

---

## 🎨 Patrones de diseño aplicados

### 1. Sliding Window para historial
Memoria de corto plazo para el LLM, sin enviar historial completo.

### 2. Dynamic System Prompt
Prompt que se adapta al contexto del mensaje, ahorrando tokens.

### 3. Fuzzy Matching
Búsqueda tolerante a errores tipográficos (SequenceMatcher, threshold 60%).

### 4. Learning Loop
- **Bank Feed Intelligence**: aprende de clasificaciones manuales
- **User Behavior Learning**: detecta patrones de uso y sugiere acciones
- **Dynamic Report Generator**: interpreta lenguaje natural para queries

### 5. Caché con TTL
Chart of Accounts: se cachea localmente con TTL de 24h, refresh manual disponible.

### 6. Sliding Window + Hints
El contexto enviado al LLM incluye no solo mensajes sino también keywords extraídos.

---

## 🔌 Extensibilidad

### Agregar un nuevo tool

1. Definir JSON Schema del tool en `main.py` (en la lista de tools)
2. Implementar la función del tool (en `main.py` o en `autonomia/<modulo>.py`)
3. Si está en autonomía: importarlo y registrarlo en la lista
4. Agregar ejemplo de uso a `docs/EXAMPLES.md`
5. Documentar en `docs/CAPACIDADES.md`

### Agregar un nuevo módulo de autonomía

1. Crear `autonomia/<nombre>_modulo.py`
2. Definir tools siguiendo el patrón existente
3. Exportar en `autonomia/__init__.py`
4. Importar y registrar en `main.py`
5. Documentar en `docs/ARCHITECTURE.md` (este archivo) y `docs/CAPACIDADES.md`

---

## 📊 Session State

```python
session_state = {
    "start_time": datetime,
    "input_tokens": int,
    "output_tokens": int,
    "operations": {
        "searches": int,
        "deposits": int,
        "invoices": int,
        "bills": int,
        "payments": int,
        "reports": int,
        "csv_batches": int,
        "ocr_processed": int,
        "web_searches": int,
        "code_executions": int,
    },
    "chart_of_accounts": dict,
    "saved_reports": dict,
    "last_search_results": {
        "customers": list,
        "vendors": list,
        "accounts": list,
    },
    "optimization_stats": {
        "tokens_saved": int,
        "tools_filtered": int,
        "chart_skips": int,
    },
    "active_company": str,  # v3.5+
}
```

---

## 🔗 Referencias

- [QuickBooks Online API v3](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)
- [OpenRouter](https://openrouter.ai/docs)
- [Google Gemini](https://ai.google.dev/docs)
- [Keep a Changelog](https://keepachangelog.com/)
```

- [ ] **Paso 2: Verificar**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/ARCHITECTURE.md"
```

Esperado: ~400 líneas.

- [ ] **Paso 3: Preguntar y commitear (condicional)**

Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add docs/ARCHITECTURE.md
git commit -m "docs: add ARCHITECTURE.md with diagrams and dataflow"
```

---

## Tarea 6: Crear docs/CAPACIDADES.md

**Archivos:**
- Crear: `docs/CAPACIDADES.md`

- [ ] **Paso 1: Escribir contenido**

Usar la herramienta `write` con:

```markdown
# 🔧 Catálogo de Capacidades

Catálogo exhaustivo de las **32 function tools** y los **6 módulos de autonomía** que componen QuickBooks AI Assistant (Dexter).

> **Versión del proyecto:** 3.5
> **Total de tools:** 32 (13 básicas + 18 de autonomía + 1 multi-empresa)
> **Total de módulos de autonomía:** 6

---

## 📊 Resumen ejecutivo

| Categoría | Tools | Descripción |
|-----------|-------|-------------|
| Búsquedas | 4 | Localizar clientes, vendors, cuentas, items |
| Transacciones | 4 | Crear invoices, bills, deposits, payments |
| Reportes | 3 | Generar P&L, balance sheet, guardar configs |
| Gestión de reportes | 2 | Cargar/guardar configuraciones de reportes |
| **Web Search (Nivel 1)** | 2 | Buscar en web y en docs QBO |
| **API Explorer (Nivel 2)** | 5 | Acceso genérico a QBO API + journal/transfer |
| **Code Executor (Nivel 3)** | 1 | Ejecutar Python dinámicamente |
| **Bank Feed Intelligence** | 4 | Clasificación inteligente de transacciones |
| **User Behavior Learning** | 4 | Aprender patrones del usuario |
| **Dynamic Report Generator** | 2 | Reportes personalizados con lenguaje natural |
| **Multi-Empresa (v3.5)** | 1 | Gestionar empresas (cambio hot-swap) |
| **TOTAL** | **32** | |

---

## 🔍 13 Tools Básicas

### Búsquedas (4)

#### 1. `buscar_cliente`
- **Categoría:** Búsqueda
- **Costo aprox.:** ~480 input + 120 output = $0.0002 USD
- **Descripción:** Búsqueda difusa (fuzzy) de clientes en QBO
- **Parámetros:** `query: str, limit: int = 5`
- **Salida:** Lista de clientes con ID, nombre, email, balance

**Ejemplo:**
```
👤: "busca el cliente Acme"
🤖: [buscar_cliente("Acme")]
   🔍 Encontré 2 clientes:
   • Acme Corporation (ID: 123, balance: $5,200)
   • Acme Subsidiary (ID: 456, balance: $0)
```

#### 2. `buscar_vendor`
- **Categoría:** Búsqueda
- **Descripción:** Búsqueda de proveedores (vendors)
- **Parámetros:** `query: str, limit: int = 5`

#### 3. `buscar_cuenta`
- **Categoría:** Búsqueda
- **Descripción:** Búsqueda en Chart of Accounts
- **Parámetros:** `query: str, categoria: str = None, limit: int = 5`
- **Costo aprox.:** ~600 input + 150 output = $0.0003 USD

#### 4. `buscar_item`
- **Categoría:** Búsqueda
- **Descripción:** Búsqueda de items/servicios/productos
- **Parámetros:** `query: str, limit: int = 5`

### Transacciones (4)

#### 5. `crear_invoice`
- **Categoría:** Transacción
- **Descripción:** Crear factura para un cliente
- **Parámetros:** `customer_id, line_items, due_date, memo`
- **Costo aprox.:** ~720 input + 210 output = $0.0003 USD

#### 6. `crear_bill`
- **Categoría:** Transacción
- **Descripción:** Crear cuenta por pagar (bill) de un vendor
- **Parámetros:** `vendor_id, line_items, due_date, memo`

#### 7. `crear_deposito`
- **Categoría:** Transacción
- **Descripción:** Crear depósito bancario (soporta splits)
- **Parámetros:** `bank_account_id, lines[], date, memo`
- **Costo aprox.:** ~720 input + 210 output = $0.0003 USD

#### 8. `crear_pago`
- **Categoría:** Transacción
- **Descripción:** Registrar pago recibido y aplicarlo a invoice(s)
- **Parámetros:** `customer_id, amount, invoice_ids[], date`

### Reportes (3)

#### 9. `generar_reporte_pl`
- **Categoría:** Reporte
- **Descripción:** Generar Profit & Loss
- **Parámetros:** `start_date, end_date, save_as: str = None`
- **Costo aprox.:** ~1,500 input + 480 output = $0.0007 USD

#### 10. `generar_balance_sheet`
- **Categoría:** Reporte
- **Descripción:** Generar Balance General
- **Parámetros:** `as_of_date, save_as: str = None`

#### 11. `guardar_reporte`
- **Categoría:** Reporte
- **Descripción:** Guardar configuración de reporte para reutilizar
- **Parámetros:** `name, type, parameters`

### Gestión (2)

#### 12. `cargar_reporte`
- **Descripción:** Cargar configuración de reporte guardada
- **Parámetros:** `name`

#### 13. `listar_reportes_guardados`
- **Descripción:** Listar todos los reportes guardados
- **Parámetros:** ninguno

---

## 🧠 18 Tools de Autonomía (v3.0+)

### Nivel 1: Web Search (2)

#### 14. `buscarenweb`
- **Categoría:** Autonomía Nivel 1
- **Descripción:** Búsqueda en web con API
- **Parámetros:** `query: str, max_results: int = 5`
- **Costo aprox.:** ~900 input + 180 output = $0.0003 USD

**Caso de uso:**
```
👤: "busca en web las mejores prácticas para depreciar activos"
🤖: [buscarenweb("mejores prácticas depreciación activos")]
   📊 3 resultados relevantes encontrados
```

#### 15. `buscardocsqbo`
- **Descripción:** Búsqueda en documentación oficial de QuickBooks API
- **Parámetros:** `query: str`

### Nivel 2: API Explorer (5)

#### 16. `crearasientodiario`
- **Descripción:** Crear Journal Entry (asiento contable)
- **Parámetros:** `lines: List[dict], date: str, memo: str`

#### 17. `creartransferencia`
- **Descripción:** Crear Transfer entre cuentas bancarias
- **Parámetros:** `from_account_id, to_account_id, amount, date`

#### 18. `qborequestgenerico`
- **Descripción:** Request genérico a cualquier endpoint de QBO
- **Parámetros:** `method: str, endpoint: str, data: dict`
- **⚠️ Potente:** acceso directo a TODA la API

#### 19. `listarendpointsqbo`
- **Descripción:** Listar endpoints disponibles de QBO API
- **Parámetros:** `category: str = None`

#### 20. `infoendpointqbo`
- **Descripción:** Información detallada de un endpoint específico
- **Parámetros:** `endpoint: str`

### Nivel 3: Code Executor (1)

#### 21. `ejecutarcodigo`
- **Descripción:** Ejecutar Python dinámicamente
- **Parámetros:** `code: str, timeout: int = 30`
- **⚠️ Seguridad:** sandbox limitado, no acceso a filesystem fuera de `/tmp`

**Caso de uso:**
```
👤: "calcula el promedio de ventas mensuales del último año"
🤖: [ejecutarcodigo(...)"]
   📊 Promedio mensual: $45,230.50
```

### Bank Feed Intelligence (4)

#### 22. `analizarbankfeed`
- **Descripción:** Analizar transacciones y sugerir clasificaciones
- **Parámetros:** `transactions: List[dict]`

#### 23. `registrarclasificacion`
- **Descripción:** Guardar clasificación manual para aprendizaje
- **Parámetros:** `transaction_id, classification: dict`

#### 24. `estadisticasclasificacion`
- **Descripción:** Estadísticas de precisión y patrones
- **Parámetros:** ninguno

#### 25. `buscarpatron`
- **Descripción:** Buscar patrón histórico para una transacción
- **Parámetros:** `description: str, amount: float`

### User Behavior Learning (4)

#### 26. `aprenderinteraccion`
- **Descripción:** Aprender de una interacción del usuario
- **Parámetros:** `user_action: dict, context: dict`

#### 27. `obtenersugerencias`
- **Descripción:** Sugerencias personalizadas basadas en historial
- **Parámetros:** `context: str`

#### 28. `registrarcorreccion`
- **Descripción:** Registrar corrección del usuario
- **Parámetros:** `original: dict, corrected: dict`

#### 29. `obtenercontexto`
- **Descripción:** Resumen del contexto reciente
- **Parámetros:** `turns: int = 10`

### Dynamic Report Generator (2)

#### 30. `generarreportecustom`
- **Descripción:** Generar reporte personalizado con lenguaje natural
- **Parámetros:** `query: str, parameters: dict`

#### 31. `parsearfecha`
- **Descripción:** Parsear expresiones de fecha naturales
- **Parámetros:** `expression: str`

---

## 🏢 Multi-Empresa (v3.5) — 1 Tool Adicional

#### 32. `gestionar_empresas`
- **Categoría:** Multi-Empresa
- **Descripción:** Listar, agregar, seleccionar o eliminar empresas
- **Parámetros:** `action: str ("list" | "add" | "select" | "remove"), name: str = None, realm_id: str = None`
- **🆕 Agregado en v3.5**

**Caso de uso:**
```
👤: "muéstrame las empresas configuradas"
🤖: [gestionar_empresas("list")]
   🏢 Empresas registradas:
   1. Acme Corp (activa)
   2. Tech Inc
   3. Design Co

👤: "cambia a Tech Inc"
🤖: [gestionar_empresas("select", "Tech Inc")]
   ✅ Cambiado a Tech Inc. Chart de cuentas recargado.
```

---

## 🧩 6 Módulos de Autonomía

| Módulo | Archivo | Tools | Propósito |
|--------|---------|-------|-----------|
| **Nivel 1: Web Search** | `autonomia/nivel1_websearch.py` | 2 | Búsqueda en web y docs QBO |
| **Nivel 2: API Explorer** | `autonomia/nivel2_api_explorer.py` | 5 | Acceso genérico a QBO + journal/transfer |
| **Nivel 3: Code Executor** | `autonomia/nivel3_code_executor.py` | 1 | Ejecutar Python dinámicamente |
| **Bank Feed Intelligence** | `autonomia/bank_feed_intelligence.py` | 4 | Clasificación inteligente con ML |
| **User Behavior Learning** | `autonomia/user_behavior_learning.py` | 4 | Aprender patrones del usuario |
| **Dynamic Report Generator** | `autonomia/dynamic_report_generator.py` | 2 | Reportes con lenguaje natural |
| **TOTAL** | — | **18** | — |

---

## 📄 OCR de Bills (PDF)

**Módulo:** `ocr_bills.py` (no es autonomy, pero es feature destacada)

**Flujo:**
1. Usuario coloca PDFs en `Pending bills/`
2. Dexter ejecuta OCR con Gemini Flash 2.0
3. Genera `Pending bills/preview_bills.csv`
4. Usuario revisa y aprueba
5. Sistema crea Bills en QBO
6. PDFs se mueven a `Processed bills/`

**Costo:** ~1,800 input + 300 output = $0.0006 USD por factura

---

## 💰 Tabla resumen: Costo por operación

| Operación | Tokens Input | Tokens Output | Costo USD |
|-----------|--------------|---------------|-----------|
| Búsqueda simple | 480 | 120 | $0.0002 |
| Crear depósito | 720 | 210 | $0.0003 |
| Reporte P&L | 1,500 | 480 | $0.0007 |
| CSV batch (10) | 2,100 | 360 | $0.0007 |
| Bank feed (5) | 2,400 | 420 | $0.0008 |
| Reconciliación | 2,700 | 540 | $0.0010 |
| OCR Bill | 1,800 | 300 | $0.0006 |
| Web Search | 900 | 180 | $0.0003 |
| Code Execution | 1,200 | 250 | $0.0004 |
| Sesión completa (45 min) | ~18,000 | ~3,500 | **~$0.006** |

**Precios referencia DeepSeek V3 (enero 2026):**
- Input: $0.19 / 1M tokens
- Output: $0.87 / 1M tokens

---

## 🔗 Documentos relacionados

- [ARCHITECTURE.md](ARCHITECTURE.md) — Diagramas y patrones de diseño
- [MULTI_EMPRESA.md](MULTI_EMPRESA.md) — Feature multi-empresa
- [EXAMPLES.md](EXAMPLES.md) — Ejemplos de uso reales
- [USER_GUIDE.md](USER_GUIDE.md) — Guía para usuarios finales
```

- [ ] **Paso 2: Verificar**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/CAPACIDADES.md"
```

Esperado: ~500 líneas.

- [ ] **Paso 3: Preguntar y commitear (condicional)**

Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add docs/CAPACIDADES.md
git commit -m "docs: add CAPACIDADES.md with 32 tools catalog and 6 autonomy modules"
```

---

## Tarea 7: Crear docs/MULTI_EMPRESA.md

**Archivos:**
- Crear: `docs/MULTI_EMPRESA.md`

- [ ] **Paso 1: Escribir contenido**

Usar la herramienta `write` con:

```markdown
# 🏢 Gestión Multi-Empresa (v3.5)

Guía específica de la funcionalidad multi-empresa introducida en v3.5. Permite a Dexter gestionar **múltiples empresas de QuickBooks** de forma independiente con tokens aislados y cambio en caliente.

---

## 🎯 ¿Qué es?

Cada empresa de QuickBooks tiene:
- Sus propios tokens de acceso (access + refresh)
- Su propio Chart of Accounts
- Sus propias configuraciones de reportes guardados
- Su propio historial de bank feed
- Su propio `meta.json` de persistencia

**Aislamiento total:** cambiar de empresa es como tener un Dexter diferente para cada una, pero sin reiniciar la aplicación.

---

## 📂 Estructura de archivos

```
Qbo Scripts/
├── .env                              # Solo credenciales de la empresa por defecto
├── companies/                        # 🆕 Carpeta de empresas (creada al registrar)
│   ├── acme_corp/
│   │   ├── meta.json                 # Tokens, realm_id, contexto aislado
│   │   ├── chart_of_accounts.json    # Caché del chart
│   │   ├── saved_reports.json        # Reportes guardados
│   │   └── bank_feed_history.json    # Patrones aprendidos
│   ├── tech_inc/
│   │   ├── meta.json
│   │   ├── chart_of_accounts.json
│   │   └── ...
│   └── design_co/
│       └── ...
├── main.py                           # Lee de companies/<activa>/meta.json
└── company_manager.py                # 🆕 Lógica de gestión
```

---

## 🔄 Flujo de cambio de empresa

```
Usuario: "cambia a Tech Inc"
   │
   ▼
1. main.py detecta intención → invoca gestionar_empresas
   │
   ▼
2. company_manager.guardar_contexto_actual()
   • Guarda session_state en companies/<actual>/meta.json
   • Serializa chart, reportes, bank feed
   │
   ▼
3. company_manager.cargar_empresa("Tech Inc")
   • Lee companies/tech_inc/meta.json
   • Actualiza .env con tokens de Tech Inc
   • Refresca access token si está expirado
   • Recarga chart_of_accounts desde QBO o caché
   │
   ▼
4. main.py continúa conversación con Tech Inc
   • session_state["active_company"] = "Tech Inc"
   • Próximas operaciones aplican a Tech Inc
```

---

## 💻 Comandos del tool `gestionar_empresas`

### Listar empresas

```
👤: "muéstrame las empresas configuradas"
🤖: [gestionar_empresas(action="list")]

   🏢 Empresas registradas (3):
   1. ⭐ Acme Corp (activa)
   2. Tech Inc
   3. Design Co
```

### Cambiar empresa

```
👤: "cambia a Tech Inc"
🤖: [gestionar_empresas(action="select", name="Tech Inc")]

   ✅ Cambiado a Tech Inc
   📊 Chart de cuentas recargado: 87 cuentas
   🔑 Tokens actualizados correctamente
```

### Agregar empresa

```
👤: "registra una nueva empresa llamada Beta LLC"
🤖: [gestionar_empresas(action="add", name="Beta LLC", realm_id="123456789...")]

   🆕 Empresa Beta LLC registrada
   ⚠️ Necesito que autorices el acceso OAuth. Ejecuta: python scripts/refresh_token.py
```

### Eliminar empresa

```
👤: "elimina Design Co"
🤖: [gestionar_empresas(action="remove", name="Design Co")]

   🗑️ Empresa Design Co eliminada
   ⚠️ Los archivos en companies/design_co/ NO se borraron (hazlo manualmente si quieres)
```

---

## 🔐 Seguridad y aislamiento

| Recurso | ¿Aislado por empresa? | ¿Cómo se aísla? |
|---------|----------------------|-----------------|
| Access Token | ✅ Sí | `meta.json` por empresa |
| Refresh Token | ✅ Sí | `meta.json` por empresa |
| Realm ID | ✅ Sí | `meta.json` por empresa |
| Chart of Accounts | ✅ Sí | `chart_of_accounts.json` por empresa |
| Saved Reports | ✅ Sí | `saved_reports.json` por empresa |
| Bank Feed Patterns | ✅ Sí | `bank_feed_history.json` por empresa |
| Token Usage CSV | ⚠️ Compartido | `tokenusage.csv` global (no por empresa) |
| User Behavior Patterns | ⚠️ Compartido | Singleton en memoria (v3.5) |

---

## ⚠️ Limitaciones actuales (v3.5)

- **Token usage** se acumula globalmente, no por empresa
- **User Behavior Learning** aún no aísla patrones por empresa (planeado para v3.6)
- **No hay encriptación** de `meta.json` (los tokens están en texto plano)
- **Cambio de empresa** requiere que la app esté autorizada en cada empresa por separado (OAuth por empresa)

---

## 🛠️ Configuración inicial

### Primera vez (una sola empresa)

1. Autoriza la app en QBO siguiendo [`INSTALL.md`](INSTALL.md)
2. Las credenciales se guardan en `.env` por defecto
3. Al primer arranque, `company_manager.py` crea `companies/<nombre>/` y `meta.json`

### Agregar segunda empresa

1. Desde la app QBO de la nueva empresa, autoriza el mismo Client ID
2. Obtén el `realm_id` de la nueva empresa
3. Ejecuta el comando `"registra una nueva empresa llamada <nombre>"` en Dexter
4. Autoriza con `python scripts/refresh_token.py`
5. La nueva empresa queda registrada

### Listo

Ahora puedes alternar entre empresas sin reiniciar.

---

## 📊 Casos de uso

### Caso 1: Contador con múltiples clientes

> "Tengo 12 clientes contables, cada uno con su QBO. Quiero gestionar todos desde un solo Dexter."

**Solución:** Registra cada empresa y cambia con `"cambia a Cliente X"`.

### Caso 2: Empresa con múltiples subsidiarias

> "Mi grupo empresarial tiene 3 subsidiarias, cada una con QBO separado."

**Solución:** Cambia entre subsidiarias para consolidar reportes.

### Caso 3: Sandbox vs Producción

> "Quiero probar cambios en sandbox antes de aplicar a producción."

**Solución:** Registra ambas y cambia con `"cambia a Sandbox"`.

---

## 🐛 Troubleshooting

### "Empresa no encontrada"

Verifica que la empresa está registrada:
```
👤: "lista las empresas"
```

### "Token inválido al cambiar"

```bash
python scripts/refresh_token.py
```

O reinicia la app y vuelve a autorizar.

### "Chart de cuentas vacío"

Fuerza refresh:
```
👤: "refrescar chart"
```

### "No puedo registrar nueva empresa"

Verifica que tienes el `realm_id` correcto y que la app está autorizada en esa empresa.

---

## 🔗 Documentos relacionados

- [ARCHITECTURE.md](ARCHITECTURE.md) — Diagrama de componentes multi-empresa
- [CAPACIDADES.md](CAPACIDADES.md) — Tool `gestionar_empresas` (tool #32)
- [CHANGELOG.md](CHANGELOG.md) — Cambios introducidos en v3.5
```

- [ ] **Paso 2: Verificar**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/MULTI_EMPRESA.md"
```

Esperado: ~200 líneas.

- [ ] **Paso 3: Preguntar y commitear (condicional)**

Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add docs/MULTI_EMPRESA.md
git commit -m "docs: add MULTI_EMPRESA.md guide for v3.5 feature"
```

---

## Tarea 8: Refactorizar docs/USER_GUIDE.md

**Archivos:**
- Modificar: `docs/USER_GUIDE.md` (refactor completo, manteniendo compatibilidad con MANUAL_USUARIO.md renombrado)

- [ ] **Paso 1: Verificar contenido actual**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/USER_GUIDE.md"
```

Esperado: ~83 líneas (el archivo MANUAL_USUARIO.md renombrado).

- [ ] **Paso 2: Sobrescribir con versión expandida**

Usar la herramienta `write` con (mantener la primera línea como comentario para preservar la atribución):

```markdown
# 📖 Guía de Usuario: Dexter (v3.5)
*Tu Asistente de IA Inteligente para QuickBooks*

> **Nota histórica:** Este documento es la versión expandida de `MANUAL_USUARIO.md` (v3.5), reorganizado y renombrado a `USER_GUIDE.md` como parte de la [organización de documentación 2026-06-03](../superpowers/specs/2026-06-03-documentacion-organizacion-design.md).

---

## 📑 Contenido

1. [Introducción: ¿Qué es Dexter?](#1-introducción-qué-es-dexter)
2. [Primeros pasos](#2-primeros-pasos)
3. [Gestión Multi-Empresa](#3-gestión-multi-empresa)
4. [Módulo OCR: Procesamiento de Facturas](#4-módulo-ocr-procesamiento-de-facturas)
5. [Módulo de Bancos: Reconciliación y Matching](#5-módulo-de-bancos-reconciliación-y-matching)
6. [Reportes y Análisis Financiero](#6-reportes-y-análisis-financiero)
7. [Consultas Naturales (CFO Virtual)](#7-consultas-naturales-cfo-virtual)
8. [Glosario de Términos](#8-glosario-de-términos)
9. [FAQ - Preguntas Frecuentes](#9-faq---preguntas-frecuentes)
10. [Ayuda Contextual: Comandos Rápidos](#10-ayuda-contextual-comandos-rápidos)

---

## 1. Introducción: ¿Qué es Dexter?

**Dexter** es un agente contable con inteligencia artificial diseñado para automatizar las tareas repetitivas en QuickBooks Online. Utiliza modelos de IA avanzados (DeepSeek V3 / GPT-4) para entender tus instrucciones en español y ejecutarlas directamente en tus libros contables.

A diferencia de otros asistentes, Dexter:

- ✅ Entiende terminología contable latinoamericana (anticipo, prepago, retainer, etc.)
- ✅ Tiene acceso directo a tu QBO (no es solo un chatbot)
- ✅ Aprende de tus patrones con el tiempo
- ✅ Puede ejecutar código Python para análisis avanzados
- ✅ Gestiona múltiples empresas de forma independiente

### ¿Para quién es?

- **Contadores** que quieren automatizar tareas repetitivas
- **Emprendedores** que llevan su propia contabilidad
- **Despachos contables** con múltiples clientes

---

## 2. Primeros pasos

### Antes de empezar

1. **Instalación completada:** Si aún no has instalado Dexter, sigue [`INSTALL.md`](INSTALL.md)
2. **Empresa configurada:** Al menos una empresa de QBO autorizada
3. **Conexión a internet:** Stable, para acceso a QBO y al LLM

### Tu primer comando

```bash
python main.py
```

Verás algo como:

```
============================================================
   🏢  DEXTER - QuickBooks AI Assistant v3.5
============================================================

🔐 Selecciona empresa:
  1. ⭐ Acme Corp (por defecto)
  2. Tech Inc
  3. Design Co

Empresa [1]: _
```

Selecciona la empresa con la que quieres trabajar (o presiona Enter para la por defecto).

### Tu primera conversación

```
👤 Tú: Busca el cliente de prueba

🤖 Dexter: 🔍 Buscando "cliente de prueba"...
   ✅ Encontré: ACME Test Client (ID: 123, balance: $0.00)
   ¿Quieres ver más detalles?
```

¡Listo! Ya estás hablando con Dexter.

---

## 3. Gestión Multi-Empresa

Dexter puede manejar múltiples empresas de QuickBooks de forma independiente.

### Al iniciar

Si tienes más de una empresa registrada, Dexter te preguntará con cuál deseas trabajar.

### Cambio en caliente

Puedes cambiar de empresa en cualquier momento:

```
👤: "cambia a Tech Inc"

🤖: ✅ Cambiado a Tech Inc
   📊 Chart de cuentas recargado: 87 cuentas
   🔑 Tokens actualizados
```

### Contexto aislado

Cada empresa mantiene:
- Su propio Chart of Accounts
- Sus propias configuraciones de reportes
- Su propio historial de bank feed
- Sus propios tokens de acceso

> **Más detalles:** Ver [`MULTI_EMPRESA.md`](MULTI_EMPRESA.md)

---

## 4. Módulo OCR: Procesamiento de Facturas

Esta herramienta extrae datos de PDFs o imágenes de facturas y los crea en QuickBooks automáticamente.

### Procedimiento

1. **Coloca las facturas** (PDF/JPG/PNG) en la carpeta `/Pending bills/`
2. **Dile a Dexter:** *"Procesa las facturas pendientes"* o *"Haz el OCR de los recibos"*
3. **Dexter analiza** cada archivo, identifica proveedor, monto, fecha y cuenta contable
4. **Validación:** Si Dexter no está seguro, te preguntará antes de crear el registro
5. **Finalización:** Los archivos procesados se mueven a `/Processed bills/`

### Ejemplo real

```
👤: "Procesa los PDFs en Pending bills"

🤖: 📂 Escaneando carpeta Pending bills/...
   📄 3 PDFs encontrados

   🔄 Procesando acme_jan.pdf...
   ✅ Vendor: ACME Corp
   ✅ Total: $1,250.00

   🔄 Procesando utility_bill.pdf...
   ✅ Vendor: Electric Company
   ✅ Total: $345.80

   📊 CSV preview: Pending bills/preview_bills.csv
   ¿Apruebo la creación de los bills? (sí/no)
```

### Costos

- ~$0.0006 USD por factura
- Usa Gemini Flash 2.0 (modelo económico)

---

## 5. Módulo de Bancos: Reconciliación y Matching

Dexter ayuda a que tu banco y tus libros coincidan perfectamente.

### Reconciliación por CSV

1. Coloca tu estado de cuenta (CSV) en `/Bank Reconciliation/`
2. Dile a Dexter: *"Reconcilia el banco con este archivo"*
3. Dexter validará que la suma cuadre y creará los depósitos o gastos faltantes

Dos modos disponibles:
- **Con balance:** validación matemática completa
- **Sin balance:** más rápido, solo identifica transacciones

### Matching Engine (Bank Feed Intelligence)

Dexter busca proactivamente si un cargo del banco ya existe en QuickBooks:

```
👤: "Tengo un cargo de $500 de Office Depot en el banco"

🤖: 🔍 Buscando coincidencias...
   ⚠️ Encontré: Ya existe un bill de Office Depot por $498.50 del 15/01
   (diferencia de $1.50, posiblemente el mismo cargo)

   ¿Quieres que use el bill existente o cree uno nuevo?
```

### Evita duplicados

Antes de registrar algo, Dexter te dirá si ya existe una transacción similar.

---

## 6. Reportes y Análisis Financiero

### Reportes predefinidos

```
👤: "Dame el P&L de este mes"
🤖: [genera Profit & Loss de enero 2026]

👤: "¿Cómo está mi balance hoy?"
🤖: [genera Balance Sheet al día actual]

👤: "Compara el P&L de enero vs diciembre"
🤖: [genera ambos y muestra comparación]
```

### Reportes personalizados (CFO Virtual)

Dexter interpreta lenguaje natural para queries complejas:

```
👤: "¿Cuánto le debo al proveedor ACME?"
🤖: 🔍 Buscando bills pendientes de ACME...
   💰 Total adeudado: $3,450.00 (3 bills)
   • Bill #001: $1,250.00 (vence 15/02)
   • Bill #005: $1,500.00 (vence 28/02)
   • Bill #008: $700.00 (vencido desde 10/01)

👤: "¿Cuáles fueron mis gastos más altos del mes pasado?"
🤖: [analiza bills y agrupa por categoría]
   📊 Top 5 categorías de gasto (diciembre):
   1. Payroll: $45,000
   2. Rent: $12,000
   3. Marketing: $8,500
   ...

👤: "¿Tenemos facturas vencidas hoy?"
🤖: [busca invoices con due_date < hoy y balance > 0]
   ⚠️ 4 facturas vencidas, total: $7,850.00
```

### Guardar configuración

Si haces un reporte recurrente:

```
👤: "Genera este P&L y guárdalo como 'Quincenal'"

🤖: ✅ P&L generado y guardado como "Quincenal"
   Para cargarlo en el futuro: "carga el reporte Quincenal"
```

---

## 7. Consultas Naturales (CFO Virtual)

Puedes hablar con Dexter como si fuera tu contador personal:

- *"¿Cuánto le debo al proveedor X?"*
- *"¿Cuáles fueron mis gastos más altos de publicidad el mes pasado?"*
- *"Busca el cliente que más nos ha comprado este año."*
- *"¿Tenemos facturas vencidas hoy?"*
- *"Dame el flujo de caja del trimestre."*
- *"¿Cuál es mi margen bruto?"*

Dexter decide qué herramientas invocar para responder.

---

## 8. Glosario de Términos

| Término | Significado en QBO |
|---------|-------------------|
| **Anticipo** | Customer Deposit (pasivo) - dinero recibido antes de facturar |
| **Prepago** | Prepaid Expense (activo) - gasto pagado por adelantado |
| **Retainer** | Sin equivalente directo, se maneja como Customer Deposit |
| **Proveedor** | Vendor |
| **Factura** | Invoice (cuenta por cobrar) |
| **Cuenta por pagar** | Bill |
| **Depósito** | Bank Deposit |
| **Asiento** | Journal Entry |
| **Libro mayor** | Chart of Accounts |
| **Estado de cuenta** | Bank Statement |
| **Conciliación** | Reconciliation |

---

## 9. FAQ - Preguntas Frecuentes

### ¿Cuánto cuesta usar Dexter?

~$0.006 USD por sesión de 45 minutos. Ver [CAPACIDADES.md](CAPACIDADES.md#-tabla-resumen-costo-por-operación) para detalles.

### ¿Mis datos están seguros?

Sí:
- Credenciales en `.env` (no en código)
- Comunicación con QBO vía OAuth 2.0
- Datos aislados por empresa

### ¿Funciona sin internet?

No. Requiere conexión para:
- Llamadas a QBO API
- Llamadas al LLM (DeepSeek V3)
- OCR (Gemini, opcional)

### ¿Puedo agregar mis propios tools?

Sí, pero requiere conocimientos de Python. Ver [ARCHITECTURE.md](ARCHITECTURE.md#-extensibilidad) para la guía de extensibilidad.

### ¿Qué pasa si cambio de empresa a mitad de conversación?

Dexter guarda el contexto y carga el de la nueva empresa. No se pierde información.

### ¿Cuántas empresas puedo registrar?

Sin límite técnico, pero cada empresa requiere autorización OAuth separada.

### ¿Funciona con QuickBooks Desktop?

No, solo QuickBooks Online (QBO).

### ¿Puedo usar otro LLM en lugar de DeepSeek?

El sistema está optimizado para DeepSeek V3, pero理论上 puedes cambiar el modelo modificando la configuración en `main.py`.

---

## 10. Ayuda Contextual: Comandos Rápidos

Si en algún momento te sientes perdido, usa estos comandos (no consumen tokens):

| Comando | Función |
|---------|---------|
| `ayuda` | Muestra ayuda general |
| `ayuda ocr` | Paso a paso del OCR de facturas |
| `ayuda bancos` | Guía para reconciliación |
| `ayuda reportes` | Ejemplos de análisis que puedes pedir |
| `refrescar chart` | Recarga el Chart of Accounts desde QBO |
| `template csv` | Genera plantilla de depósitos en CSV |
| `listar reportes` | Muestra reportes guardados |
| `¿cuánto he gastado?` | Estadísticas de tokens de la sesión |
| `salir` | Termina la sesión |

---

## 🆘 ¿Necesitas más ayuda?

1. **Revisa la documentación:** [`docs/`](.)
2. **Busca en Troubleshooting:** [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
3. **Mira ejemplos:** [`EXAMPLES.md`](EXAMPLES.md)
4. **Si es un bug:** Contacta al desarrollador (Alfredo)

---

**Elaborado por:** Dexter AI Assistant
**Propietario:** Alfredo J.
**Versión del documento:** 3.5
**Última actualización:** 2026-06-03
```

- [ ] **Paso 3: Verificar**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/USER_GUIDE.md"
```

Esperado: ~350 líneas.

- [ ] **Paso 4: Preguntar y commitear (condicional)**

Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add docs/USER_GUIDE.md
git commit -m "docs: expand USER_GUIDE.md with FAQ, glossary, multi-empresa, OCR, help commands"
```

---

## Tarea 9: Actualizar docs/README.md a v3.5

**Archivos:**
- Modificar: `docs/README.md`

- [ ] **Paso 1: Sobrescribir con versión v3.5**

Usar la herramienta `write` con:

```markdown
# 📚 Documentación de QuickBooks AI Assistant (Dexter)

Bienvenido a la documentación de **Dexter**, tu asistente de IA para QuickBooks Online.

> **Versión:** 3.5 (Multi-Empresa PRO)
> **Identidad del asistente:** Dexter
> **Total de function tools:** 32 (13 básicas + 18 autonomía + 1 multi-empresa)
> **Módulos de autonomía:** 6

---

## 📑 Índice de documentos

| Documento | Para quién | Descripción |
|-----------|-----------|-------------|
| 📄 [**README.md**](../README.md) (raíz) | Todos | Hub principal del proyecto, índice rápido |
| 📘 [**USER_GUIDE.md**](USER_GUIDE.md) | Usuarios / Contadores | Cómo usar Dexter paso a paso, sin jerga técnica |
| 📗 [**EXAMPLES.md**](EXAMPLES.md) | Todos | 10+ ejemplos reales de conversaciones con Dexter |
| 📕 [**TROUBLESHOOTING.md**](TROUBLESHOOTING.md) | Todos | Solución de problemas comunes |
| 📙 [**CONTEXT.md**](CONTEXT.md) | Desarrolladores / LLMs | Contexto completo del proyecto (32 KB) |
| 🏗️ [**ARCHITECTURE.md**](ARCHITECTURE.md) | Desarrolladores | Diagramas, dataflow, patrones de diseño |
| 🔧 [**CAPACIDADES.md**](CAPACIDADES.md) | Desarrolladores | Catálogo de los 32 tools y 6 módulos de autonomía |
| 🏢 [**MULTI_EMPRESA.md**](MULTI_EMPRESA.md) | Todos | Guía específica de la feature v3.5 multi-empresa |
| 🚀 [**INSTALL.md**](INSTALL.md) | Desarrolladores | Instalación detallada paso a paso |
| 📜 [**CHANGELOG.md**](CHANGELOG.md) | Todos | Historial versionado v1.0 → v3.5 |
| 🗺️ [**roadmap/**](roadmap/) | Todos | Roadmap y documentos estratégicos |

---

## 🚀 Inicio rápido

1. **Nuevo usuario (contador):** Lee [`USER_GUIDE.md`](USER_GUIDE.md)
2. **Nuevo desarrollador:** Lee [`../README.md`](../README.md) → [`INSTALL.md`](INSTALL.md) → [`ARCHITECTURE.md`](ARCHITECTURE.md)
3. **Quieres ver qué puede hacer:** Lee [`EXAMPLES.md`](EXAMPLES.md) → [`CAPACIDADES.md`](CAPACIDADES.md)
4. **Tienes un problema:** Revisa [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
5. **Quieres entender la historia:** Lee [`CHANGELOG.md`](CHANGELOG.md) → [`roadmap/ROADMAP.md`](roadmap/ROADMAP.md)

---

## 🆕 Novedades v3.5 (Multi-Empresa PRO)

- **Multi-empresa** con tokens aislados por empresa
- **Cambio en caliente** sin reiniciar la app
- **Identidad "Dexter"** (antes "Asistente TMP AI")
- **32 function tools** (1 nuevo: `gestionar_empresas`)
- Persistencia por empresa en `companies/<nombre>/meta.json`

Ver [`MULTI_EMPRESA.md`](MULTI_EMPRESA.md) para detalles completos.

---

## 🏗️ Estructura del proyecto

```
Qbo Scripts/
├── README.md                 ← Hub principal
├── docs/                     ← Estás aquí
│   ├── README.md             ← Este archivo (índice)
│   ├── USER_GUIDE.md
│   ├── EXAMPLES.md
│   ├── TROUBLESHOOTING.md
│   ├── CONTEXT.md
│   ├── ARCHITECTURE.md
│   ├── CAPACIDADES.md
│   ├── MULTI_EMPRESA.md
│   ├── INSTALL.md
│   ├── CHANGELOG.md
│   ├── requirements.txt
│   ├── roadmap/              ← Roadmap y docs estratégicos
│   └── superpowers/
│       └── specs/            ← Specs de diseño
├── main.py                   ← Aplicación principal
├── company_manager.py        ← Multi-empresa (v3.5)
├── ocr_bills.py              ← OCR de facturas
├── gitmanager.py             ← Utilidad de versionado
├── install.sh                ← Instalación automatizada
├── autonomia/                ← 6 módulos de autonomía
├── scripts/                  ← Scripts auxiliares
├── Pending bills/            ← PDFs a procesar (OCR)
├── Processed bills/          ← PDFs ya procesados
├── Bank Reconciliation/      ← CSVs de reconciliación
├── Backup/                   ← Respaldos
├── outputs/                  ← Archivos generados
├── templates/                ← Plantillas
└── Test/                     ← Pruebas
```

---

## 🔗 Recursos externos

- [QuickBooks Online API v3](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)
- [OpenRouter](https://openrouter.ai/docs) (DeepSeek V3)
- [Google Gemini](https://ai.google.dev/docs) (OCR)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Mantenedor:** Alfredo
**Asistente:** Dexter
**Última actualización de este índice:** 2026-06-03
```

- [ ] **Paso 2: Verificar**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/README.md"
```

Esperado: ~110 líneas (vs las 333 de la versión desactualizada).

- [ ] **Paso 3: Preguntar y commitear (condicional)**

Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add docs/README.md
git commit -m "docs: sync docs/README.md to v3.5 with full index of all documents"
```

---

## Tarea 10: Sincronizar docs/CONTEXT.md

**Archivos:**
- Modificar: `docs/CONTEXT.md` (actualizar menciones de versión, herramientas, nomenclatura)

- [ ] **Paso 1: Verificar versión actual**

```bash
head -10 "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/CONTEXT.md"
```

- [ ] **Paso 2: Reemplazar menciones desactualizadas**

**Búsqueda 1:** Reemplazar menciones de "18 tools" o "13 function tools" por "32 function tools"

```
Buscar:    18 function tools
Reemplazar: 32 function tools
```

```
Buscar:    18 tools especializados
Reemplazar: 32 function tools
```

**Búsqueda 2:** Reemplazar referencias a `chartofaccounts.json` por `chart_of_accounts.json`

```
Buscar:    chartofaccounts.json
Reemplazar: chart_of_accounts.json
```

**Búsqueda 3:** Reemplazar "Asistente" (sin nombre) por "Dexter" donde aplique

```
Buscar:    El asistente ahora se llama
Reemplazar: El asistente (Dexter) ahora
```

Usar la herramienta `grep` para encontrar todas las ocurrencias primero:

```bash
grep -n "18 tools\|chartofaccounts\|TMP AI" "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/CONTEXT.md"
```

Para cada match, decidir si reemplazar. Si son consistentes con v3.5, dejar; si son desactualizados, reemplazar.

- [ ] **Paso 3: Añadir nota al inicio**

Insertar después de la línea 1 (después del título principal), antes de la línea 2:

```markdown
> **Nota (2026-06-03):** Este documento ha sido sincronizado a v3.5. Para el catálogo exhaustivo de tools, ver [`CAPACIDADES.md`](CAPACIDADES.md). Para arquitectura técnica, ver [`ARCHITECTURE.md`](ARCHITECTURE.md). Para multi-empresa, ver [`MULTI_EMPRESA.md`](MULTI_EMPRESA.md).
```

- [ ] **Paso 4: Verificar cambios**

```bash
grep -c "32 function tools" "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/CONTEXT.md"
grep -c "chartofaccounts" "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/CONTEXT.md"
```

Esperado:
- Primer comando: ≥1
- Segundo comando: 0 (ya no debe quedar la versión sin underscore)

- [ ] **Paso 5: Preguntar y commitear (condicional)**

Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add docs/CONTEXT.md
git commit -m "docs: sync CONTEXT.md to v3.5 (tools count, file naming, links to new docs)"
```

---

## Tarea 11: Sincronizar docs/EXAMPLES.md

**Archivos:**
- Modificar: `docs/EXAMPLES.md` (añadir 3-5 ejemplos nuevos)

- [ ] **Paso 1: Verificar versión actual**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/EXAMPLES.md"
head -20 "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/EXAMPLES.md"
```

- [ ] **Paso 2: Añadir sección al final (antes de cualquier footer)**

Usar la herramienta `edit` para añadir antes de la última línea en blanco del archivo:

**oldString:**
```
---
```

**newString:**
```
---

## 🆕 Ejemplos nuevos (v3.5) — Multi-Empresa, OCR, Dexter

### Ejemplo 11: Cambio de empresa en caliente

```
👤: "cambia a Tech Inc"

🤖: [gestionar_empresas("select", "Tech Inc")]

   ✅ Cambiado a Tech Inc
   📊 Chart de cuentas recargado: 87 cuentas
   🔑 Tokens actualizados correctamente

👤: "busca el cliente Acme en esta empresa"

🤖: 🔍 Buscando "Acme" en Tech Inc...
   ℹ️ Tech Inc no tiene clientes con "Acme" en el nombre
   💡 Sugerencia: ¿quizás querías buscar en Acme Corp? Usa "cambia a Acme Corp"
```

### Ejemplo 12: OCR de facturas PDF

```
👤: "Procesa los PDFs en Pending bills"

🤖: 📂 Escaneando carpeta Pending bills/...
   📄 3 PDFs encontrados

   🔄 Procesando acme_jan.pdf con Gemini Flash 2.0...
   ✅ Factura extraída:
      Vendor: ACME Corp
      Total: $1,250.00
      Fecha: 2026-01-15

   🔄 Procesando utility.pdf...
   ✅ Vendor: Electric Company - $345.80

   📊 CSV preview: Pending bills/preview_bills.csv

👤: "apruebo"

🤖: ✅ 2 bills creados en QuickBooks
   📁 Archivos movidos a: Processed bills/
```

### Ejemplo 13: Bank Feed Intelligence con matching

```
👤: "Tengo un cargo de $500 de Office Depot en el banco"

🤖: [analizarbankfeed]

   🔍 Buscando coincidencias...

   ⚠️ Match encontrado:
      • Bill existente: Office Depot #4521 ($498.50) del 15/01
      • Diferencia: $1.50 (probable mismo cargo, redondeo o fee)

   ¿Quieres que use el bill existente o cree uno nuevo?
```

### Ejemplo 14: Reporte personalizado con lenguaje natural

```
👤: "¿Cuáles fueron mis gastos más altos del último trimestre agrupados por categoría?"

🤖: [generarreportecustom]

   📊 Gastos Q4 2025 por categoría:

   1. Payroll:              $125,450 (42%)
   2. Rent & Occupancy:     $45,000  (15%)
   3. Marketing:            $28,900  (10%)
   4. Professional Services:$15,600  (5%)
   5. Insurance:            $12,500  (4%)

   💡 Insight: Marketing subió 22% vs Q3, revisa ROI.

   ¿Quieres que lo guarde como "Gastos Q4"?
```

### Ejemplo 15: Dexter saluda y se presenta

```
👤: "hola"

🤖: ¡Hola Alfredo! 👋 Soy Dexter, tu asistente para QuickBooks.

   📊 Estado actual:
   • Empresa activa: Acme Corp
   • Chart de cuentas: 142 cuentas (cache: 2 horas)
   • Sesión iniciada: 14:30

   ¿En qué te ayudo hoy?
```

---
```

- [ ] **Paso 3: Verificar adición**

```bash
grep -c "Ejemplo 1[1-5]:" "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/EXAMPLES.md"
```

Esperado: 5 (ejemplos 11, 12, 13, 14, 15).

- [ ] **Paso 4: Preguntar y commitear (condicional)**

Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add docs/EXAMPLES.md
git commit -m "docs: add 5 new examples to EXAMPLES.md (multi-empresa, OCR, bank feed, custom reports, Dexter)"
```

---

## Tarea 12: Sincronizar docs/TROUBLESHOOTING.md

**Archivos:**
- Modificar: `docs/TROUBLESHOOTING.md` (añadir sección multi-empresa)

- [ ] **Paso 1: Verificar versión actual**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/TROUBLESHOOTING.md"
grep -n "^##" "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/TROUBLESHOOTING.md"
```

- [ ] **Paso 2: Añadir sección 9 al índice y al final**

**Editar el índice (línea ~17):**

oldString:
```
8. [Errores Generales](#8-errores-generales)
```

newString:
```
8. [Errores Generales](#8-errores-generales)
9. [Problemas Multi-Empresa (v3.5)](#9-problemas-multi-empresa-v35)
```

**Añadir nueva sección al final del archivo:**

oldString:
```
[última línea del archivo]
```

newString:
```
[última línea del archivo]

---

## 9. Problemas Multi-Empresa (v3.5)

### ❌ Error: "Empresa no encontrada"

**Síntomas:**
```
❌ Empresa 'Tech Inc' no encontrada. Empresas registradas: Acme Corp, Design Co
```

**Causa:** Intentas cambiar a una empresa no registrada.

**Solución:**
```
👤: "lista las empresas"
🤖: 🏢 Empresas registradas: Acme Corp, Design Co

👤: "registra Tech Inc con realm_id <tu_realm_id>"
```

---

### ❌ Error: "Token inválido al cambiar empresa"

**Síntomas:**
```
❌ 401 Unauthorized al cambiar a Tech Inc
```

**Causa:** El access token de Tech Inc expiró y el refresh falló.

**Solución:**
```bash
# Opción 1: Refrescar manualmente
python scripts/refresh_token.py

# Opción 2: Re-autorizar la app
# Ve a https://developer.intuit.com → tu app → "Keys & OAuth"
# Regenera tokens y actualiza .env
```

---

### ❌ Error: "Chart de cuentas vacío tras cambiar"

**Síntomas:**
```
⚠️ No se encontraron cuentas en la empresa actual
```

**Causa:** El caché de chart está vacío o es de otra empresa.

**Solución:**
```
👤: "refrescar chart"
🤖: 📊 Descargando chart desde QBO... 87 cuentas encontradas ✅
```

---

### ❌ Error: "No puedo registrar nueva empresa"

**Síntomas:**
```
❌ No se puede registrar empresa: realm_id no válido
```

**Solución:**
1. Verifica que el `realm_id` es correcto (en la URL de QBO, después de `/company/`)
2. Verifica que la app está autorizada en esa empresa
3. Si la app no está autorizada, ejecuta `python scripts/refresh_token.py`

---

### ❌ Error: "Cambio de empresa no se refleja"

**Síntomas:** Dices "cambia a Tech Inc" pero las operaciones siguen aplicando a la empresa anterior.

**Causa:** Bug en v3.5 conocido cuando hay concurrencia con operaciones pendientes.

**Solución:**
1. Espera a que terminen las operaciones en curso
2. Vuelve a decir "cambia a Tech Inc"
3. Si persiste, reinicia la app

Ver [`MULTI_EMPRESA.md`](MULTI_EMPRESA.md) para más detalles.

---
```

- [ ] **Paso 3: Verificar adición**

```bash
grep -c "^## 9\." "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/TROUBLESHOOTING.md"
```

Esperado: 1 (la nueva sección 9).

- [ ] **Paso 4: Preguntar y commitear (condicional)**

Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add docs/TROUBLESHOOTING.md
git commit -m "docs: add Section 9 (multi-empresa troubleshooting) to TROUBLESHOOTING.md"
```

---

## Tarea 13: Crear README.md raíz (hub principal)

**Archivos:**
- Crear: `README.md` (en la raíz del proyecto)

- [ ] **Paso 1: Verificar que NO existe actualmente**

```bash
ls "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/README.md" 2>&1 | head -2
```

Esperado: error "No such file or directory".

- [ ] **Paso 2: Crear el archivo**

Usar la herramienta `write` con el siguiente contenido (es el más largo del plan, ~600-700 líneas):

```markdown
<div align="center">

# 🤖 Dexter — QuickBooks AI Assistant

![Version](https://img.shields.io/badge/version-3.5-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-Private-red.svg)
![Status](https://img.shields.io/badge/status-Active-success.svg)
![Tools](https://img.shields.io/badge/tools-32-purple.svg)
![QBO API](https://img.shields.io/badge/QBO-v3-orange.svg)

**Asistente conversacional inteligente para automatizar tareas contables en QuickBooks Online**

Habla con tu contabilidad en español natural. 32 function tools. Multi-empresa. OCR. Optimizado al 57% en tokens.

[Instalación](#-instalación-rápida) • [Características](#-características-principales) • [Documentación](#-documentación) • [Ejemplos](#-uso-básico)

</div>

---

## 📑 Tabla de contenidos

### Para todos
1. [TL;DR](#-tldr)
2. [Características principales](#-características-principales)
3. [Ejemplo de uso rápido](#-ejemplo-de-uso-rápido)
4. [¿Para quién es?](#-para-quién-es)
5. [Documentación](#-documentación)

### Para desarrolladores
6. [Arquitectura (resumen)](#-arquitectura-resumen)
7. [Stack tecnológico](#-stack-tecnológico)
8. [Instalación rápida](#-instalación-rápida)
9. [Catálogo de capacidades](#-catálogo-de-capacidades)
10. [Optimización y costos](#-optimización-y-costos)
11. [Seguridad](#-seguridad)
12. [Roadmap](#-roadmap)
13. [Cómo contribuir / extender](#-cómo-contribuir--extender)

### Anexos
- [A. Empresas / casos de uso](#-anexo-a-empresas--casos-de-uso)
- [B. Licencia y créditos](#-anexo-b-licencia-y-créditos)

---

## 🎯 TL;DR

**Dexter** es un asistente de IA conversacional que conecta un LLM (DeepSeek V3) con QuickBooks Online. En lugar de navegar la interfaz de QBO, le dices a Dexter qué quieres hacer en español y él ejecuta las operaciones contables por ti.

```bash
# En tu terminal:
python main.py
```

```
👤 Tú: Muéveme $2500 de Client Retainers de Acme Corp a Checking Account

🤖 Dexter:
   ✅ Depósito creado:
      • Acme Corp: $2,500.00 desde Client Retainers
      • Total depositado en Checking: $2,500.00
      • Fecha: 2026-01-20
```

**Costo típico:** ~$0.006 USD por sesión de 45 minutos.

---

## 🚀 Características principales

| Capacidad | Descripción |
|-----------|-------------|
| 💬 **IA conversacional en español** | Entiende terminología contable latinoamericana (anticipo, prepago, retainer) |
| 🏢 **Multi-empresa (v3.5)** | Gestiona múltiples empresas QBO con tokens aislados y cambio en caliente |
| 🔧 **32 function tools** | Búsquedas, transacciones, reportes, herramientas de autonomía |
| 🧠 **6 módulos de autonomía** | Web search, API explorer, code execution, bank feed ML, user learning, dynamic reports |
| 📄 **OCR de facturas PDF** | Extrae datos de PDFs y crea bills automáticamente (Gemini Flash 2.0) |
| 🏦 **Reconciliación bancaria** | Automatiza conciliaciones por CSV con validación matemática |
| 📊 **Reportes personalizados** | Lenguaje natural → queries (CFO Virtual) |
| ⚡ **Optimización de tokens (57%)** | Tools dinámicos, sliding window, system prompt condicional |
| 💰 **Tracking de costos** | CSV histórico + Excel con 4 hojas de análisis |
| 🔐 **OAuth 2.0 seguro** | Tokens se refrescan automáticamente, aislados por empresa |

---

## 📸 Ejemplo de uso rápido

### Crear un depósito multi-cliente

```
👤: "Muéveme $1500 de Client Retainers de Tech Inc y $2300 de Prepaid Labour de Design Co a Checking Account"

🤖: [buscar_cliente × 2, buscar_cuenta × 3, crear_deposito]

   ✅ Depósito creado:
      • Tech Inc: $1,500.00 desde Client Retainers
      • Design Co: $2,300.00 desde Prepaid Labour
      • Total depositado: $3,800.00
      • Fecha: 2026-01-20
```

### Generar un reporte

```
👤: "Dame el P&L de enero y guárdalo como 'Quincenal Ene'"

🤖: [generar_reporte_pl, guardar_reporte]

   📊 Profit & Loss - Enero 2026:
      Ingresos:    $125,450.00
      Gastos:       $78,320.00
      Utilidad:     $47,130.00
      Margen:        37.6%

   ✅ Guardado como: "Quincenal Ene"
   Para recargarlo: "carga el reporte Quincenal Ene"
```

### Cambiar de empresa

```
👤: "cambia a Tech Inc"

🤖: [gestionar_empresas]

   ✅ Cambiado a Tech Inc
   📊 Chart de cuentas recargado: 87 cuentas
   🔑 Tokens actualizados
```

---

## 👥 ¿Para quién es?

### ✅ Perfecto para ti si:
- Eres **contador** y haces tareas repetitivas en QBO
- Eres **emprendedor** que lleva su propia contabilidad
- Llevas un **despacho contable** con múltiples clientes
- Quieres **automatizar** sin aprender a programar la API de QBO

### ❌ No es para ti si:
- Solo quieres un chatbot genérico (esto se conecta a QBO)
- Usas QuickBooks Desktop (solo QBO está soportado)
- No tienes conexión a internet estable
- Esperas que funcione 100% sin revisión humana (siempre valida)

---

## 📚 Documentación

| Documento | Para quién | Descripción |
|-----------|-----------|-------------|
| 📘 [**docs/USER_GUIDE.md**](docs/USER_GUIDE.md) | 👤 Contadores | Cómo usar Dexter paso a paso, sin jerga |
| 📗 [**docs/EXAMPLES.md**](docs/EXAMPLES.md) | 👥 Todos | 15+ ejemplos reales de conversaciones |
| 📕 [**docs/TROUBLESHOOTING.md**](docs/TROUBLESHOOTING.md) | 👥 Todos | Solución de problemas comunes |
| 📙 [**docs/CONTEXT.md**](docs/CONTEXT.md) | 🛠️ Devs / LLMs | Contexto completo del proyecto (32 KB) |
| 🏗️ [**docs/ARCHITECTURE.md**](docs/ARCHITECTURE.md) | 🛠️ Devs | Diagramas, dataflow, patrones de diseño |
| 🔧 [**docs/CAPACIDADES.md**](docs/CAPACIDADES.md) | 🛠️ Devs | Catálogo de los 32 tools y 6 módulos |
| 🏢 [**docs/MULTI_EMPRESA.md**](docs/MULTI_EMPRESA.md) | 👥 Todos | Guía específica multi-empresa v3.5 |
| 🚀 [**docs/INSTALL.md**](docs/INSTALL.md) | 🛠️ Devs | Instalación detallada paso a paso |
| 📜 [**docs/CHANGELOG.md**](docs/CHANGELOG.md) | 👥 Todos | Historial versionado v1.0 → v3.5 |
| 🗺️ [**docs/roadmap/**](docs/roadmap/) | 👥 Todos | Roadmap y documentos estratégicos |

---

## 🏗️ Arquitectura (resumen)

```
┌─────────────────────────────────────────────────────────────────┐
│                     USUARIO (en español)                        │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                main.py (loop conversacional)                    │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ • 32 function tools (JSON Schema)                       │  │
│   │ • System prompt dinámico (optimización 57%)              │  │
│   │ • Sliding window de historial (5 turnos)                 │  │
│   └─────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────┬─────────────────────────┘
             │                          │
             ▼                          ▼
┌────────────────────────┐   ┌──────────────────────────────────┐
│  company_manager.py    │   │     autonomia/ (6 módulos)       │
│  (multi-empresa)       │   │  • web search • API explorer    │
│                        │   │  • code executor • bank feed    │
│                        │   │  • user learning • reports      │
└────────────┬───────────┘   └──────────────┬───────────────────┘
             │                               │
             ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   APIs Externas                                │
│  • QuickBooks Online API v3                                     │
│  • OpenRouter (DeepSeek V3)                                     │
│  • Google Gemini (OCR)                                          │
└─────────────────────────────────────────────────────────────────┘
```

**Para el diagrama completo y dataflow:** ver [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## ⚙️ Stack tecnológico

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Python** | 3.9+ | Lenguaje principal |
| **QuickBooks Online API** | v3 | Integración contable vía OAuth 2.0 |
| **OpenRouter + DeepSeek V3** | - | LLM con function calling |
| **Google Gemini Flash 2.0** | - | OCR de facturas PDF |
| **pandas** | - | Procesamiento CSV |
| **openpyxl** | - | Generación de reportes Excel |
| **requests** | - | HTTP requests |
| **python-dotenv** | - | Variables de entorno |
| **PyPDF2** | - | Extracción de texto de PDFs |

---

## 🚀 Instalación rápida

```bash
# 1. Clonar
git clone <url-del-repo>
cd "Qbo Scripts"

# 2. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar credenciales
cp .env.example .env
# Edita .env con tus credenciales (QB_*, OPENROUTER_API_KEY, GEMINI_API_KEY)

# 5. Verificar
python scripts/verify_setup.py

# 6. ¡Ejecutar!
python main.py
```

> 📘 **Instalación detallada** (OAuth, troubleshooting, variables de entorno): [`docs/INSTALL.md`](docs/INSTALL.md)

---

## 🎯 Uso básico

### Comandos conversacionales (consumen tokens)

```
"Muéveme $2500 de Client Retainers de Acme a Checking"
"Dame el P&L del 1 al 15 de enero"
"Procesa los PDFs en Pending bills"
"¿Cuánto le debo al proveedor X?"
"Cambia a Tech Inc"
```

### Comandos rápidos (sin consumir tokens)

| Comando | Función |
|---------|---------|
| `ayuda` | Muestra ayuda general |
| `refrescar chart` | Recarga Chart of Accounts desde QBO |
| `template csv` | Genera plantilla CSV de depósitos |
| `listar reportes` | Muestra reportes guardados |
| `¿cuánto he gastado?` | Estadísticas de tokens de la sesión |
| `informe de tokens` | Genera Excel con análisis de costos |
| `salir` | Termina la sesión |

> 📘 **Más ejemplos:** [`docs/EXAMPLES.md`](docs/EXAMPLES.md)
> 📘 **Guía para usuarios:** [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)

---

## 🔧 Catálogo de capacidades

**32 function tools** distribuidos en 11 categorías. Ver [`docs/CAPACIDADES.md`](docs/CAPACIDADES.md) para el catálogo completo.

| Categoría | Tools | Ejemplos |
|-----------|-------|----------|
| Búsquedas | 4 | `buscar_cliente`, `buscar_cuenta` |
| Transacciones | 4 | `crear_deposito`, `crear_invoice`, `crear_bill` |
| Reportes | 3 | `generar_reporte_pl`, `generar_balance_sheet` |
| Web Search | 2 | `buscarenweb`, `buscardocsqbo` |
| API Explorer | 5 | `qborequestgenerico`, `crearasientodiario` |
| Code Executor | 1 | `ejecutarcodigo` |
| Bank Feed Intelligence | 4 | `analizarbankfeed`, `buscarpatron` |
| User Behavior Learning | 4 | `obtenersugerencias`, `registrarcorreccion` |
| Dynamic Report Generator | 2 | `generarreportecustom`, `parsearfecha` |
| Gestión de reportes | 2 | `guardar_reporte`, `cargar_reporte` |
| Multi-Empresa | 1 | `gestionar_empresas` |
| **TOTAL** | **32** | — |

**6 módulos de autonomía** en `autonomia/`:

```
autonomia/
├── nivel1_websearch.py        (Web search + docs QBO)
├── nivel2_api_explorer.py     (Acceso genérico a QBO API)
├── nivel3_code_executor.py    (Python dinámico)
├── bank_feed_intelligence.py  (ML de clasificación)
├── user_behavior_learning.py  (Aprendizaje de patrones)
└── dynamic_report_generator.py (Reportes con NL)
```

---

## 💰 Optimización y costos

### Optimización de tokens (v3.0)

| Técnica | Reducción |
|---------|-----------|
| Tools dinámicos (filtrado por keyword) | -40% en tool definitions |
| Sliding window de historial (5 turnos) | -30% en historial |
| System prompt condicional (chart) | -25% en system prompt |
| **Reducción combinada** | **-57% en tokens/llamada** |

### Costos por operación (DeepSeek V3, enero 2026)

| Operación | Tokens | Costo USD |
|-----------|--------|-----------|
| Búsqueda simple | ~600 | $0.0002 |
| Crear depósito | ~930 | $0.0003 |
| Reporte P&L | ~1,980 | $0.0007 |
| CSV batch (10 registros) | ~2,460 | $0.0007 |
| Bank feed (5 transacciones) | ~2,820 | $0.0008 |
| Reconciliación | ~3,240 | $0.0010 |
| OCR Bill (por factura) | ~2,100 | $0.0006 |
| Web Search | ~1,080 | $0.0003 |
| **Sesión completa (45 min)** | ~21,500 | **~$0.006** |

**Precios referencia DeepSeek V3:** Input $0.19/1M tokens, Output $0.87/1M tokens.

### Proyección mensual
- 20 sesiones/mes → ~430,000 tokens → **~$0.12 USD/mes**
- vs. sin optimización: ~$0.20 USD/mes
- **Ahorro anual: ~$0.96 USD** (sin contar la escalabilidad)

---

## 🔒 Seguridad

✅ Credenciales en `.env` (excluido de Git)  
✅ OAuth 2.0 con QuickBooks (sin contraseñas en código)  
✅ Refresh automático de tokens (sin intervención manual)  
✅ Validación de existencia antes de crear transacciones  
✅ Detección de duplicados potenciales (Bank Feed)  
✅ Validación de categorías de cuentas (fuzzy + reglas)  
✅ Aislamiento de tokens por empresa (v3.5)  
✅ Sandboxing limitado en `ejecutarcodigo`  

⚠️ **Limitaciones conocidas:**
- `meta.json` almacena tokens en texto plano (sin encriptación)
- Code executor no tiene sandbox completo (cuidado con lo que ejecutas)
- No hay autenticación de dos factores en la app misma

Ver [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) si encuentras problemas.

---

## 🗺️ Roadmap

### ✅ Completado
- [x] v1.0 — MVP inicial con OAuth y búsquedas
- [x] v2.0 — DeepSeek V3 con function calling (13 tools)
- [x] v3.0 — 6 módulos de autonomía, optimización 57%, OCR (31 tools)
- [x] v3.5 — Multi-empresa con tokens aislados (32 tools)

### 🚧 En desarrollo (post-organización)
- [ ] Encriptación de `meta.json` por empresa
- [ ] UI web con Streamlit
- [ ] Reportes PDF automáticos
- [ ] Integración con Google Sheets
- [ ] Notificaciones Slack/Email

### 💡 Ideas futuras
- [ ] Dashboard de analytics
- [ ] Comandos por voz
- [ ] Scheduled reports
- [ ] Categorización ML avanzada
- [ ] Detección de anomalías
- [ ] Predicción de cash flow
- [ ] Automatización de compliance fiscal

Ver [`docs/roadmap/ROADMAP.md`](docs/roadmap/ROADMAP.md) para el roadmap completo.

---

## 🤝 Cómo contribuir / extender

### Agregar un nuevo function tool

1. **Define el JSON Schema** del tool en `main.py` (lista de tools)
2. **Implementa la función** que ejecuta la lógica (en `main.py` o `autonomia/<modulo>.py`)
3. **Si va en autonomía:** créalo en `autonomia/<nombre>.py` y regístralo en `__init__.py`
4. **Documenta** en [`docs/CAPACIDADES.md`](docs/CAPACIDADES.md) y añade ejemplo a [`docs/EXAMPLES.md`](docs/EXAMPLES.md)
5. **Commit** con mensaje descriptivo: `feat: add <tool_name> tool`

### Agregar un nuevo módulo de autonomía

1. **Crea** `autonomia/<nombre>_modulo.py` siguiendo el patrón de los existentes
2. **Importa y registra** los tools en `main.py`
3. **Documenta** en [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) y [`docs/CAPACIDADES.md`](docs/CAPACIDADES.md)
4. **Añade ejemplos** de uso a [`docs/EXAMPLES.md`](docs/EXAMPLES.md)

### Reportar bugs

1. Revisa [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) primero
2. Si no se resuelve, contacta a Alfredo con:
   - Pasos para reproducir
   - Salida esperada vs obtenida
   - Versión (`main.py` muestra la versión al iniciar)
   - Empresa y entorno (sandbox/prod)

---

## 🏢 Anexo A: Empresas / casos de uso

### Quién lo usa hoy

- **Alfredo** — Contador con 1 empresa propia (uso principal)
- **Despacho piloto** — 3 clientes en producción, evaluando escalabilidad

### Casos de uso típicos

| Caso | Descripción |
|------|-------------|
| **Contador con múltiples clientes** | Registra cada cliente como empresa, cambia con "cambia a Cliente X" |
| **Empresa con subsidiarias** | Cambia entre subsidiarias para consolidar reportes |
| **Sandbox vs Producción** | Prueba cambios en sandbox antes de producción |
| **Contabilidad personal** | Automatiza bookkeeping personal sin aprender API de QBO |
| **Análisis financiero (CFO Virtual)** | Pregunta en lenguaje natural, obtén reportes |

---

## 📄 Anexo B: Licencia y créditos

**Licencia:** Privado. Proyecto de uso interno de Alfredo.

**Desarrollador principal:** Alfredo

**Asistente IA:** Dexter (v3.5+)

**Tecnologías clave:**
- **DeepSeek V3** vía [OpenRouter](https://openrouter.ai)
- **QuickBooks Online API v3** vía [Intuit Developer](https://developer.intuit.com)
- **Google Gemini Flash 2.0** vía [AI Studio](https://aistudio.google.com)

**Librerías Python:** Ver [`requirements.txt`](requirements.txt)

**Agradecimientos:**
- A la comunidad de OpenRouter por hacer accesibles modelos avanzados
- A Intuit por su API bien documentada
- A todos los que reportaron bugs y pidieron features

---

## 📞 Soporte

1. 📘 Lee la [documentación completa](docs/README.md)
2. 🔧 Revisa [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. 💬 Pregunta a Dexter (¡también responde preguntas técnicas!)

---

<div align="center">

**Hecho con ❤️ para automatizar la contabilidad**

⭐ Si te resulta útil, considera compartirlo con otros contadores.

[⬆ Volver arriba](#-dexter--quickbooks-ai-assistant)

</div>
```

- [ ] **Paso 3: Verificar**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/README.md"
grep -c "^##" "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/README.md"
```

Esperado:
- `wc -l`: 600-700 líneas
- `grep -c "^##"`: ≥25 secciones

- [ ] **Paso 4: Preguntar y commitear (condicional)**

Si autoriza:

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git add README.md
git commit -m "docs: add comprehensive README.md as project hub (v3.5, 32 tools, multi-empresa)"
```

---

## ✅ Verificación final post-implementación

Tras completar las 13 tareas, ejecutar:

- [ ] **Verificación de estructura**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
echo "=== docs/ ==="
ls -la docs/*.md
echo "=== docs/roadmap/ ==="
ls -la docs/roadmap/
echo "=== Raíz ==="
ls README.md
echo "=== ROADMAPDOCS no debe existir ==="
ls ROADMAPDOCS 2>&1 | head -1
echo "=== MANUAL_USUARIO.md no debe existir ==="
ls docs/MANUAL_USUARIO.md 2>&1 | head -1
```

Esperado:
- `docs/*.md` lista 10+ archivos .md (los 9 docs + CHANGELOG)
- `docs/roadmap/` lista 6 archivos
- `README.md` existe en raíz
- `ROADMAPDOCS` y `docs/MANUAL_USUARIO.md` dan error "No such file"

- [ ] **Verificación de contenido**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
echo "=== Versiones sincronizadas ==="
grep -l "v3.5" docs/*.md | wc -l
echo "=== Multi-empresa mencionado ==="
grep -l "multi.empresa\|Multi.Empresa" docs/*.md | wc -l
echo "=== Dexter mencionado ==="
grep -l "Dexter" docs/*.md | wc -l
```

Esperado:
- `v3.5` en ≥6 archivos
- `multi-empresa` en ≥5 archivos
- `Dexter` en ≥4 archivos

- [ ] **Verificación de código NO modificado**

```bash
cd "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts"
git diff --stat main.py company_manager.py ocr_bills.py install.sh
```

Esperado: 0 cambios en estos archivos.

---

## 🎉 Plan completo

**Total de tareas:** 13 (todas de contenido) + sección de verificación final
**Total de archivos nuevos:** 7 docs + 1 README raíz = 8
**Total de archivos actualizados:** 4
**Total de archivos movidos:** 6 (5 desde ROADMAPDOCS + TODO.TEXT)
**Líneas estimadas de nueva documentación:** ~2,200-2,500
**Plan de implementación:** 2,897 líneas

**Próximo paso:** Ejecutar las tareas según la política de commits (preguntar al usuario antes de cada commit, o autorizar globalmente).
```

- [ ] **Verificar plan**

```bash
wc -l "/media/alfredojfp/90F8A433F8A4198C/Mis Apps/Qbo Scripts/docs/superpowers/plans/2026-06-03-documentacion-organizacion.md"
```

Esperado: ~2,000-2,500 líneas.

---

**Plan guardado en:** `docs/superpowers/plans/2026-06-03-documentacion-organizacion.md`
