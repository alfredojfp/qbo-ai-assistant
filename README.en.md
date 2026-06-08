<div align="center">

# 🧠 Dexter — QuickBooks AI Agent

[![Version](https://img.shields.io/badge/version-4.1.0_dev-blue)](https://github.com/alfredojfp/qbo-ai-assistant)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-692_passing-green)](https://github.com/alfredojfp/qbo-ai-assistant/actions)
[![Tools](https://img.shields.io/badge/tools-106-purple)](docs/SETUP.md)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)
[![QBO API](https://img.shields.io/badge/QBO-v3-orange)](https://developer.intuit.com)
[![Languages](https://img.shields.io/badge/languages-ES_|_EN-brightgreen)](docs/SETUP.md)

**The most complete open-source AI agent for QuickBooks Online. Self-hosted. Private.**

Talk to your accounting in natural language — **Spanish & English**. 106 tools across 21 domains.
Multi-company. OCR. Persistent memory. Dry-run. Bank feed classification.

[Setup Guide](docs/SETUP.md) · [Documentation](docs/) · [Market Comparison](docs/comparativa_mercado_2026.md)

> 📖 *Este documento también está disponible en [español](README.md).*

</div>

---

## ⚡ Quick Start

```bash
# Option 1: Quick install (recommended)
curl -fsSL https://raw.githubusercontent.com/alfredojfp/qbo-ai-assistant/main/install.sh | bash

# Option 2: Manual
git clone https://github.com/alfredojfp/qbo-ai-assistant.git
cd qbo-ai-assistant
pip install -r requirements.txt
./run_dexter.sh              # first run: launches setup wizard
```

---

## 🎯 What Dexter Does

Dexter is an **AI agent** that operates QuickBooks Online through natural language. It's not a chatbot — it's an assistant that executes real QBO operations.

```
> create an estimate for Acme Corp for $1,500

  ⚡ buscar_cliente · nombre=Acme Corp
    ✓ Client found (ID 70)

  Dexter · I'll create an estimate for Acme Corp (ID 70) for $1,500.
           Confirm?

> yes

  ⚡ crear_estimate · cliente_id=70, monto=1500
    ✓ Estimate #92 created
```

### Capabilities

| Area | Tools |
|---|---|
| 🔍 **Search** | Customers, vendors, accounts, items, estimates, invoices |
| ✏️ **Create** | Customers, invoices, estimates, bills, payments, deposits, journal entries |
| 📊 **Reports** | P&L, Balance Sheet, Cash Flow, Trial Balance, 13 more reports |
| 📄 **OCR** | Extract bills from PDFs, learn formats per vendor |
| 🏦 **Bank Feed** | Classify transactions, learn patterns, CSV batch |
| 🔄 **Multi-Company** | Tokens, chart, memory & classifications isolated per company |
| 🌐 **Bilingual** | Auto-detect Spanish/English, keywords in both languages |
| 🛡️ **Security** | Dry-run mode, confirmation prompts, no cloud data |

---

## 🚀 Features

### Dry-Run Mode
Test any operation without touching QBO. Add `--dry-run` and Dexter simulates. If you like it, just say `run it`.

### Persistent Memory
Dexter remembers between sessions. Each company has its own memory where it stores IDs, preferences, corrections, and learnings.

### Continuous Learning
- **Bank feed:** learns classification patterns per company
- **OCR:** remembers invoice formats per vendor
- **Corrections:** saves tips when you fix something

### Auto Company Profile
On first load, Dexter studies QBO and generates a profile with chart of accounts, P&L, active customers, and more.

### Professional Terminal
Rich-powered UI: panels, colors, tool indicators. Every `⚡ tool_call` shows parameters and results.

---

## 📊 Project Status

| Metric | Value |
|---|---|
| Tests | 692 passing |
| QBO Tools | 106 in 21 modules |
| QBO API Coverage | 93% |
| Commits | 149 |
| Companies Supported | Unlimited (isolated tokens) |
| LLM | DeepSeek V3 via OpenRouter |
| OCR | Gemini 2.0 Flash |

---

## 📁 Structure

```
Qbo Scripts/
├── main.py                    # Agent core
├── dexter/
│   ├── tools/                 # 106 tools in 21 modules
│   ├── core/                  # API helpers, memory, retry, safe_json
│   ├── console.py             # Rich-powered CLI
│   └── error_log.py           # Persistent JSONL error log
├── autonomia/                 # Autonomy modules (web, API, bank feed)
├── tests/                     # 692 tests
├── docs/                      # Documentation
│   ├── SETUP.md               # Setup guide ← start here
│   └── ...
├── companies/                 # Per-company data (tokens, memory, profile)
├── scripts/                   # OAuth, refresh, verify, TSheets
└── data/                      # Generated data
```

---

## 📖 Documentation

| Document | Description |
|---|---|
| [SETUP.md](docs/SETUP.md) | Complete installation & configuration |
| [CONOCIMIENTO_CONTABLE.md](docs/CONOCIMIENTO_CONTABLE.md) | Accounting knowledge base (ES) |
| [DRY_RUN.md](docs/DRY_RUN.md) | Simulation mode guide (ES) |
| [MULTI_EMPRESA.md](docs/MULTI_EMPRESA.md) | Multi-company management (ES) |
| [comparativa_mercado_2026.md](docs/comparativa_mercado_2026.md) | Market comparison (ES) |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Troubleshooting (ES) |

---

## 🔒 Privacy

Dexter is **100% self-hosted**. Your accounting data never leaves your machine. Credentials are stored in `~/.config/dexter/CREDENTIALS` with chmod 600. The code is audited with pre-commit hooks that detect API key leaks.

---

## 📄 License

**Proprietary — All Rights Reserved.** Use of this software requires express authorization from the owner. See [LICENSE](LICENSE) for full details.

---

<div align="center">
<sub>Built with ❤️ for accountants who code</sub>
</div>
