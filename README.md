<div align="center">

# 🧠 Dexter — QuickBooks AI Agent

[![Version](https://img.shields.io/badge/version-4.1.0_dev-blue)](https://github.com/alfredojfp/qbo-ai-assistant)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-692_passing-green)](https://github.com/alfredojfp/qbo-ai-assistant/actions)
[![Tools](https://img.shields.io/badge/tools-106-purple)](docs/SETUP.md)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)
[![QBO API](https://img.shields.io/badge/QBO-v3-orange)](https://developer.intuit.com)
[![Idiomas](https://img.shields.io/badge/idiomas-ES_|_EN-brightgreen)](docs/SETUP.md)

**El agente contable más completo para QuickBooks Online. Open source. Self-hosted. En español.**

Habla con tu contabilidad en lenguaje natural — **español e inglés**. 106 herramientas en 21 dominios.
Multi-empresa. OCR. Memoria persistente. Dry-run. Clasificación bank feed.

[Guía de Instalación](docs/SETUP.md) · [Documentación](docs/) · [Estudio de Mercado](docs/comparativa_mercado_2026.md)

> 📖 *This document is also available in [English](README.en.md).*

</div>

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

## 🎯 ¿Qué hace Dexter?

Dexter es un **agente de IA** que opera QuickBooks Online mediante lenguaje natural. No es un chatbot — es un asistente que ejecuta operaciones reales en QBO.

```
❯ Tú: crea un estimate para Prueba2 por $1,500

  ⚡ buscar_cliente · nombre=Prueba2
    ✓ Cliente encontrado (ID 70)

  Dexter · Voy a crear un estimate para Prueba2 (ID 70) por $1,500.
           ¿Confirmás?

❯ Tú: sí

  ⚡ crear_estimate · cliente_id=70, monto=1500
    ✓ Estimate #92 creado
```

### Capacidades

| Área | Herramientas |
|---|---|
| 🔍 **Búsqueda** | Clientes, vendors, cuentas, items, estimates, invoices |
| ✏️ **Creación** | Clientes, invoices, estimates, bills, pagos, depósitos, journal entries |
| 📊 **Reportes** | P&L, Balance Sheet, Cash Flow, Trial Balance, 13 reportes más |
| 📄 **OCR** | Extrae bills de PDFs, aprende formatos por proveedor |
| 🏦 **Bank Feed** | Clasifica transacciones, aprende patrones, CSV batch |
| 🔄 **Multi-Empresa** | Tokens, chart, memoria y clasificaciones aisladas por empresa |
| 🌐 **Bilingüe** | Detecta español/inglés automáticamente, keywords en ambos idiomas |
| 🛡️ **Seguridad** | Dry-run, modo confirmación, sin datos en la nube |

---

## 🚀 Features

### Modo Simulación (Dry-Run)
Probá cualquier operación sin tocar QBO. Agregá `--dry-run` y Dexter simula. Si te gusta, `ejecutalo`.

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
| Tests | 692 pasando |
| Herramientas QBO | 106 en 21 módulos |
| Cobertura API QBO | 93% |
| Commits | 147 |
| Empresas soportadas | Ilimitadas (tokens aislados) |
| LLM | DeepSeek V3 via OpenRouter |
| OCR | Gemini 2.0 Flash |

---

## 📁 Estructura

```
Qbo Scripts/
├── main.py                    # Core del agente
├── dexter/
│   ├── tools/                 # 106 herramientas en 21 módulos
│   ├── core/                  # API helpers, memoria, retry, safe_json
│   ├── console.py             # UI con Rich
│   └── error_log.py           # Log persistente JSONL
├── autonomia/                 # Módulos de autonomía (web, API, bank feed)
├── tests/                     # 692 tests
├── docs/                      # Documentación
│   ├── SETUP.md               # Guía de instalación ← empezá acá
│   └── ...
├── companies/                 # Datos por empresa (tokens, memoria, perfil)
├── scripts/                   # OAuth, refresh, verify, TSheets
└── data/                      # Datos generados
```

---

## 📖 Documentación

| Documento | Descripción |
|---|---|
| [SETUP.md](docs/SETUP.md) | Instalación y configuración completa |
| [CONOCIMIENTO_CONTABLE.md](docs/CONOCIMIENTO_CONTABLE.md) | Base de conocimiento contable |
| [DRY_RUN.md](docs/DRY_RUN.md) | Modo simulación |
| [MULTI_EMPRESA.md](docs/MULTI_EMPRESA.md) | Gestión multi-empresa |
| [comparativa_mercado_2026.md](docs/comparativa_mercado_2026.md) | Estudio de mercado |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Solución de problemas |

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
