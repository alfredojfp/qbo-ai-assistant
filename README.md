<div align="center">

# 🧠 Dexter — QuickBooks AI Agent

[![Version](https://img.shields.io/badge/version-5.0.0-blue)](https://github.com/alfredojfp/qbo-ai-assistant)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-766_passing-green)](https://github.com/alfredojfp/qbo-ai-assistant/actions)
[![Tools](https://img.shields.io/badge/tools-121_purple)](docs/SETUP.md)
[![Skills](https://img.shields.io/badge/skills-24-orange)](docs/SKILL_REFACTOR.md)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)
[![QBO API](https://img.shields.io/badge/QBO-v3-orange)](https://developer.intuit.com)
[![Idiomas](https://img.shields.io/badge/idiomas-ES_|_EN-brightgreen)](docs/SETUP.md)

**El agente contable más completo para QuickBooks Online. Self-hosted. En español.**

Habla con tu contabilidad en lenguaje natural — **español e inglés**. 121 herramientas en 24 skills.
Fuzzy matching ≥85%. Batch engine con dry-run. Multi-empresa. OCR. Memoria persistente.

[Guía de Instalación](docs/SETUP.md) · [Documentación](docs/) · [Estudio de Mercado](docs/comparativa_mercado_2026.md) · [OpenContext](https://github.com/0xranx/OpenContext)

> 📖 *This document is also available in [English](README.en.md).*

</div>

---

## 🆕 Novedades v5.0.0

| Feature | Descripción |
|---|---|
| **Fuzzy Matching ≥85%** | Token-based con detección de prefijos. "Ben Haselman" matchea con "Benjamin Haselman" (95%). Busca contra todos los clientes/vendors activos (cache 5min) |
| **Batch Deposits v2** | CSV con columnas `bank_account` y `line_account`. Agrupa items con mismo date+bank en un solo depósito multi-línea. Creación de clientes en lote |
| **Entity Format QBO** | Formato plano `{value, type}` en DepositLineDetail — corregido contra API real de QBO |
| **Slash Autocomplete** | Presioná `/` para ver los 121 tools con fuzzy matching. Escribí `/bus` y filtra `buscar_cliente`, `buscar_vendor`, etc |
| **MCP Backend** (experimental) | Motor dual: `native` (default) o `mcp` (Intuit MCP Server oficial, 144 tools, 396 tests). Feature flag `QB_BACKEND=mcp` |
| **Auditoría Batch Engine** | 12 bugs corregidos, state machine completa, error reporting mejorado, mocks alineados con QBO real |
| **Documentación** | 12 docs en OpenContext + SKILL_REFACTOR.md + Engineering Manual |

---

## ⚡ Quick Start

```bash
# Opción 1: Instalación rápida (recomendada)
curl -fsSL https://raw.githubusercontent.com/alfredojfp/qbo-ai-assistant/main/install.sh | bash

# Opción 2: Manual
git clone https://github.com/alfredojfp/qbo-ai-assistant.git
cd qbo-ai-assistant
pip install -r requirements.txt
./run_dexter.sh              # primera vez: lanza setup wizard
```

---

## 📸 Demo

```
┌──────────────────────────────────────────────────────────┐
│          🧠  DEXTER  ·  QBO Assistant                     │
│               v5.0.0 · Endless                             │
└──────────────────────────────────────────────────────────┘

  Cargando contexto...
  Contexto: 331 cuentas · 0 reportes · 0 reglas · ES

  ✓ Conexión establecida

  DEXTER listo. 'menu' para ayuda, 'salir' para terminar.

❯ Tú: crea un depósito por $5000 en Checking con estos clientes

  ⚡ buscar_cliente · nombre=Carla Stoner
    ✓ Cliente encontrado (ID 3577)
  ⚡ buscar_cliente · nombre=Tammy Burgoyne
    ✓ Cliente encontrado (ID 3199)

  ⚡ crear_deposito · cuenta_destino_id=226, lineas=2
    ✓ Depósito creado — $5,000.00

❯ Tú: procesa el CSV de depósitos deposits_template.csv

📋 BATCH abc12345 CREADO
   Items: 3
   Cuentas resueltas desde CSV:
     1003 Checking - Bravera Bank → 226 (Bank)
     2100 Customer Deposits → 250 (Liability)

DRY RUN — Resumen del batch
   Listos para ejecutar:  3
   Omitidos / con error:  0

❯ Tú: s
   ✓ Depósito creado: $11,767.77 | 3 clientes → ID 23587
```

---

## 🎯 ¿Qué hace Dexter?

Dexter es un **agente de IA** que opera QuickBooks Online mediante lenguaje natural. No es un chatbot — es un asistente que ejecuta operaciones reales en QBO.

### Capacidades

| Área | Herramientas |
|---|---|
| 🔍 **Búsqueda** | Clientes, vendors, cuentas, items, estimates, invoices — fuzzy matching ≥85% |
| ✏️ **Creación** | Clientes, invoices, estimates, bills, pagos, depósitos, journal entries |
| 📊 **Reportes** | P&L, Balance Sheet, Cash Flow, Trial Balance, 13 reportes más |
| 📄 **OCR** | Extrae bills de PDFs, aprende formatos por proveedor |
| 🏦 **Bank Feed** | Clasifica transacciones, aprende patrones, CSV batch |
| 📦 **Batch Engine** | CSV deposits multi-cliente con state machine, dry-run, agrupación automática |
| 🔄 **Multi-Empresa** | Tokens, chart, memoria y clasificaciones aisladas por empresa. Cambio instantáneo |
| 🎯 **Fuzzy Matching** | Token-based ≥85% con detección de prefijos (Ben→Benjamin). Cache 5min |
| 🌐 **Bilingüe** | Detecta español/inglés automáticamente, keywords en ambos idiomas |
| 🛡️ **Seguridad** | Dry-run, modo confirmación, sin datos en la nube |
| ⚡ **MCP Backend** | Motor dual: native (Python puro) o Intuit MCP Server (144 tools oficiales) |

---

## 🚀 Features

### Fuzzy Matching ≥85%
Dexter busca clientes y vendors con similitud token-based. Si QBO no encuentra "Ben Haselman", busca contra todos los clientes activos y sugiere "Benjamin Haselman" (95% similar). Detecta prefijos comunes (Ben→Benjamin, Pat→Patrick).

### Batch Engine (v2)
Procesa CSVs de depósitos con columnas `bank_account` y `line_account`. Agrupa items con misma fecha y banco en un solo depósito multi-línea. State machine completa: PENDING → VALIDATED → DRY_RUN → CONFIRMED → EXECUTING. Creación de clientes en lote (2+ clientes nuevos sin preguntar info opcional).

### Modo Simulación (Dry-Run)
Probá cualquier operación sin tocar QBO. Agregá `--dry-run` y Dexter simula. Si te gusta, `ejecutalo`.

### Slash Autocomplete (`/`)
Presioná `/` en el prompt para ver los 121 tools con fuzzy matching. Escribí `/dep` y filtra `crear_deposito`, `depositar_lote_csv`, etc. Sin `/`, funcionamiento normal.

### Memoria Persistente
Dexter recuerda entre sesiones. Cada empresa tiene su propia memoria donde guarda IDs, preferencias, correcciones y aprendizajes.

### Aprendizaje Continuo
- **Bank feed:** aprende patrones de clasificación por empresa
- **OCR:** recuerda formatos de facturas por proveedor
- **Correcciones:** guarda tips cuando corregís algo

### Perfil Automático de Empresa
Al cargar una empresa por primera vez, Dexter estudia QBO y genera un perfil con chart of accounts, P&L, clientes activos y más.

### Terminal Profesional
Interfaz con Rich: paneles, colores, indicadores de herramientas. Cada `⚡ tool_call` muestra parámetros y resultados.

---

## 📊 Estado del Proyecto

| Métrica | Valor |
|---|---|
| Tests | 766 pasando |
| Herramientas QBO | 121 en 24 skills |
| Cobertura API QBO | 93% |
| Commits | 236 |
| Empresas soportadas | Ilimitadas (tokens aislados) |
| LLM | DeepSeek V3 via OpenRouter (multi-proveedor) |
| OCR | Gemini 2.0 Flash |
| Fuzzy Matching | Token-based ≥85% (HIGH-1) |
| Batch Engine | v2 con agrupación (HIGH-2) |
| MCP Backend | Intuit MCP Server (HIGH-3, experimental) |

---

## 📁 Estructura

```
Qbo Scripts/
├── main.py                    # Core del agente + QBOAdapter lifecycle (HIGH-3)
├── run_dexter.sh              # Launcher motor nativo
├── run_dexter_mcp.sh          # Launcher motor Intuit MCP (experimental)
├── dexter/
│   ├── skills/                # 24 skills con 121 herramientas
│   │   ├── search/fuzzy.py    # Token-based fuzzy matching ≥85% (HIGH-1)
│   │   └── engineering/       # Manual de ingeniería + procedimientos
│   ├── core/
│   │   ├── batch/             # State machine + batch engine (HIGH-2)
│   │   ├── mcp_bridge.py      # Python ↔ Node.js JSON-RPC (HIGH-3)
│   │   ├── qbo_adapter.py     # QBOClientProtocol via Intuit MCP (HIGH-3)
│   │   ├── qbo_client.py      # Cliente QBO nativo
│   │   └── memory.py          # Memoria persistente
│   ├── console.py             # UI Rich + slash autocomplete (/)
│   └── prompt.py              # System prompt JARVIS style
├── vendor/                    # Intuit MCP Server (gitignored, install.sh)
├── autonomia/                 # Web search, API explorer, bank feed intelligence
├── tests/                     # 750 tests
├── docs/                      # Documentación
│   ├── SKILL_REFACTOR.md      # Arquitectura de skills
│   ├── SETUP.md               # Guía de instalación
│   └── ...
├── companies/                 # Datos por empresa (tokens, memoria, perfil)
├── scripts/                   # OAuth, setup wizard, OCR, TSheets
└── data/                      # Datos generados
```

---

## 📖 Documentación

| Documento | Descripción |
|---|---|
| [SETUP.md](docs/SETUP.md) | Instalación y configuración completa |
| [SKILL_REFACTOR.md](docs/SKILL_REFACTOR.md) | Arquitectura de skills auto-descubribles |
| [DRY_RUN.md](docs/DRY_RUN.md) | Modo simulación |
| [MULTI_EMPRESA.md](docs/MULTI_EMPRESA.md) | Gestión multi-empresa |
| [comparativa_mercado_2026.md](docs/comparativa_mercado_2026.md) | Estudio de mercado |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Solución de problemas |
| `dexter/skills/engineering/SKILL.md` | Manual de ingeniería — cómo agregar features nuevas |

**También disponible en OpenContext:** 12 documentos con arquitectura, skills, batch engine, fuzzy matching, auditoría, QBO integration, y MCP backend. `oc context manifest dexter` para cargarlos.

---

---

## 🔒 Privacidad

Dexter es **100% self-hosted**. Tus datos contables nunca salen de tu máquina. Las credenciales se almacenan en `~/.config/dexter/CREDENTIALS` con permisos 600. El código es auditado con pre-commit hooks que detectan filtraciones de API keys.

---

## 📄 Licencia

**Propietaria — Todos los derechos reservados.** El uso de este software requiere autorización expresa del titular. Ver [LICENSE](LICENSE) para detalles completos.

---

<div align="center">
<sub>Built with ❤️ for accountants who code</sub>
</div>
