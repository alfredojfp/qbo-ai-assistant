<div align="center">

# 🤖 Dexter — QuickBooks AI Assistant

![Version](https://img.shields.io/badge/version-3.7.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-Private-red.svg)
![Status](https://img.shields.io/badge/status-Active-success.svg)
![Tools](https://img.shields.io/badge/tools-43-purple.svg)
![QBO API](https://img.shields.io/badge/QBO-v3-orange.svg)

**Asistente conversacional inteligente para automatizar tareas contables en QuickBooks Online**

Habla con tu contabilidad en español natural. 43 function tools en 14 módulos. Multi-empresa. OCR. Optimizado al 57% en tokens.

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
| 🌐 **Bilingüe ES/EN (v3.6)** | Model Routing (Llama 3 / DeepSeek V3) + traducción dinámica con persistencia por empresa |
| 🎯 **Guía interactiva (v3.7)** | Onboarding paso a paso, Matching Engine para conciliación bancaria, Manual de Usuario vivo |
| 🆕 **43 function tools en 14 módulos (v4.0)** | [`dexter/tools/`](dexter/tools/) — registry modular, data-driven routing |
| 🧠 **6 módulos de autonomía** | Web search, API explorer, code execution, bank feed ML, user learning, dynamic reports |
| 📄 **OCR de facturas PDF** | Extrae datos de PDFs y crea bills automáticamente (Gemini Flash 2.0) |
| 🏦 **Reconciliación bancaria** | BNK-RECON tag-only (no crea txns) + matching exacto+fuzzy |
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
| 🔧 [**docs/CAPACIDADES.md**](docs/CAPACIDADES.md) | 🛠️ Devs | Catálogo de los 43 tools y 14 módulos |
| 🏢 [**docs/MULTI_EMPRESA.md**](docs/MULTI_EMPRESA.md) | 👥 Todos | Guía específica multi-empresa (v3.5) |
| 🚀 [**docs/INSTALL.md**](docs/INSTALL.md) | 🛠️ Devs | Instalación detallada paso a paso |
| 📜 [**docs/CHANGELOG.md**](docs/CHANGELOG.md) | 👥 Todos | Historial versionado v1.0 → v3.7 |
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

**43 function tools** distribuidos en 14 módulos de dominio. Ver [`docs/CAPACIDADES.md`](docs/CAPACIDADES.md) para el catálogo completo, o [`dexter/tools/README.md`](dexter/tools/README.md) para la arquitectura modular (v4.0).

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
| **TOTAL (v3.7)** | **32** | — |
| **TOTAL (v4.0)** | **43** | Distribuidos en 14 módulos de `dexter/tools/` |

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
- [x] v3.6 — Inteligencia Híbrida (Model Routing Llama 3 / DeepSeek V3) + Bilingüe ES/EN
- [x] v3.7 — Guía Interactiva (Onboarding) + Matching Engine Bank Feed + Manual de Usuario vivo

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

**Asistente IA:** Dexter (v3.7)

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
