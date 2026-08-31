<div align="center">

# 🧠 Dexter — QuickBooks AI Agent

[![Version](https://img.shields.io/badge/version-4.1.0--dev-blue)](https://github.com/alfredojfp/qbo-ai-assistant)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-766_passing-green)](https://github.com/alfredojfp/qbo-ai-assistant/actions)
[![Tools](https://img.shields.io/badge/tools-121-purple)](docs/SETUP.md)
[![Skills](https://img.shields.io/badge/skills-24-orange)](docs/SKILL_REFACTOR.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![QBO API](https://img.shields.io/badge/QBO-v3-orange)](https://developer.intuit.com)
[![Languages](https://img.shields.io/badge/languages-ES_|_EN-brightgreen)](docs/SETUP.md)

**The most complete AI agent for QuickBooks Online. Self-hosted. Private.**

Talk to your accounting in natural language — **Spanish & English**. 121 tools across 24 skills.
Fuzzy matching ≥85%. Batch engine with dry-run. Multi-company. OCR. Persistent memory.

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

## 📸 Demo

```
┌──────────────────────────────────────────────────────────┐
│          🧠  DEXTER  ·  QBO Assistant                     │
│               v4.1.0-dev · Endless                         │
└──────────────────────────────────────────────────────────┘

  Loading context...
  Context: 331 accounts · 0 reports · 0 rules · EN

  ✓ Connection established

  DEXTER ready. Type 'help' for commands, 'exit' to quit.

> create a deposit for $5000 in Checking with these customers

  ⚡ buscar_cliente · nombre=Carla Stoner
    ✓ Client found (ID 3577)
  ⚡ buscar_cliente · nombre=Tammy Burgoyne
    ✓ Client found (ID 3199)

  ⚡ crear_deposito · cuenta_destino_id=226, lineas=2
    ✓ Deposit created — $5,000.00

> process the deposit CSV deposits_template.csv

📋 BATCH abc12345 CREATED
   Items: 3
   Accounts resolved from CSV:
     1003 Checking - Bravera Bank → 226 (Bank)
     2100 Customer Deposits → 250 (Liability)

DRY RUN — Batch summary
   Ready to execute:  3
   Skipped / errors:  0

> yes
   ✓ Deposit created: $11,767.77 | 3 customers → ID 23587
```

---

## 🎯 What Dexter Does

Dexter is an **AI agent** that operates QuickBooks Online through natural language. It's not a chatbot — it's an assistant that executes real QBO operations.

### Capabilities

| Area | Tools |
|---|---|
| 🔍 **Search** | Customers, vendors, accounts, items, estimates, invoices — fuzzy matching ≥85% |
| ✏️ **Create** | Customers, invoices, estimates, bills, payments, deposits, journal entries |
| 📊 **Reports** | P&L, Balance Sheet, Cash Flow, Trial Balance, 13 more reports |
| 📄 **OCR** | Extract bills from PDFs, learn formats per vendor |
| 🏦 **Bank Feed** | Classify transactions, learn patterns, CSV batch |
| 📦 **Batch Engine** | Multi-customer CSV deposits with state machine, dry-run, auto-grouping |
| 🔄 **Multi-Company** | Tokens, chart, memory & classifications isolated per company. Instant switching |
| 🎯 **Fuzzy Matching** | Token-based ≥85% with prefix detection (Ben→Benjamin). 5min cache |
| 🌐 **Bilingual** | Auto-detect Spanish/English, keywords in both languages |
| 🛡️ **Security** | Dry-run mode, confirmation prompts, no cloud data |

---

## 🚀 Features

### Fuzzy Matching ≥85%
Dexter searches customers and vendors with token-based similarity. If QBO doesn't find "Ben Haselman", it searches all active customers and suggests "Benjamin Haselman" (95% similar). Detects common prefixes (Ben→Benjamin, Pat→Patrick).

### Batch Engine (v2)
Process deposit CSVs with `bank_account` and `line_account` columns. Groups items with same date and bank into a single multi-line deposit. Complete state machine: PENDING → VALIDATED → DRY_RUN → CONFIRMED → EXECUTING. Batch customer creation (2+ new customers without asking optional info).

### Dry-Run Mode
Test any operation without touching QBO. Add `--dry-run` and Dexter simulates. If you like it, just say `run it`.

### Slash Autocomplete (`/`)
Press `/` in the prompt to see all 121 tools with fuzzy matching. Type `/dep` to filter `crear_deposito`, `depositar_lote_csv`, etc. Without `/`, normal operation.

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
| Tests | 766 passing |
| QBO Tools | 121 in 24 skills |
| QBO API Coverage | 93% |
| Commits | 236 |
| Companies Supported | Unlimited (isolated tokens) |
| LLM | DeepSeek V3 via OpenRouter (multi-provider) |
| OCR | Gemini 2.0 Flash |
| Fuzzy Matching | Token-based ≥85% |
| Batch Engine | v2 with auto-grouping |

---

## 📁 Structure

```
Qbo Scripts/
├── main.py                    # Agent core
├── run_dexter.sh              # Launcher
├── dexter/
│   ├── skills/                # 24 skills with 121 tools
│   │   ├── search/fuzzy.py    # Token-based fuzzy matching ≥85%
│   │   └── engineering/       # Engineering manual + procedures
│   ├── core/
│   │   ├── batch/             # State machine + batch engine
│   │   ├── qbo_client.py      # Native QBO client
│   │   └── memory.py          # Persistent memory
│   ├── console.py             # Rich UI + slash autocomplete (/)
│   └── prompt.py              # System prompt
├── autonomia/                 # Web search, API explorer, bank feed intelligence
├── tests/                     # 766 tests
├── docs/                      # Documentation
│   ├── SKILL_REFACTOR.md      # Skills architecture
│   ├── SETUP.md               # Setup guide
│   └── ...
├── companies/                 # Per-company data (tokens, memory, profile)
├── scripts/                   # OAuth, setup wizard, OCR
└── data/                      # Generated data
```

---

## 📖 Documentation

| Document | Description |
|---|---|
| [SETUP.md](docs/SETUP.md) | Complete installation & configuration |
| [SKILL_REFACTOR.md](docs/SKILL_REFACTOR.md) | Self-discoverable skills architecture |
| [DRY_RUN.md](docs/DRY_RUN.md) | Simulation mode guide |
| [MULTI_EMPRESA.md](docs/MULTI_EMPRESA.md) | Multi-company management |
| [comparativa_mercado_2026.md](docs/comparativa_mercado_2026.md) | Market comparison |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Troubleshooting guide |
| `dexter/skills/engineering/SKILL.md` | Engineering manual — how to add new features |

---

## 🔒 Privacy

Dexter is **100% self-hosted**. Your accounting data never leaves your machine. Credentials are stored in `companies/` (excluded from git). The code is audited with pre-commit hooks that detect API key leaks.

---

## 📄 License

**MIT License.** See [LICENSE](LICENSE) for full details.

---

<div align="center">
<sub>Built with ❤️ for accountants who code</sub>
</div>
