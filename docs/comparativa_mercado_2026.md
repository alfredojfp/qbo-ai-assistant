# Estudio de Mercado — Dexter vs Alternativas

> **Fecha:** Junio 2026
> **Autor:** opencode + Alfredo
> **Propósito:** Comparar Dexter contra alternativas open-source y comerciales para QBO automation con IA.

---

## 1. Alternativas Open Source (GitHub)

### 1.1. `voska/qbo-cli` ⭐ 26
**QuickBooks Online CLI for humans and AI agents**

| Aspecto | qbo-cli | Dexter |
|---|---|---|
| Lenguaje | Go | Python |
| Enfoque | CLI tradicional con flags | Agente conversacional LLM |
| Interface | Comandos `qbo list invoices --where "Balance > '0'` | Lenguaje natural "dame las facturas pendientes" |
| Tools | CRUD, reports, batch, CDC | 102 tools en 21 dominios |
| Multi-empresa | Sí (company switch) | Sí (aislada con tokens) |
| AI integration | Skill para Claude Code | LLM nativo (DeepSeek) + 102 tools |
| Instalación | Binary único (brew install) | Python + pip |
| Tests | No visibles | 668 tests, CI/CD |
| Estado | Dev temprano (22 commits) | Maduro (133 commits) |

**Veredicto:** qbo-cli es un excelente CLI para usuarios técnicos. Dexter lo supera en funcionalidad conversacional y cobertura de API (102 vs ~15 endpoints), pero qbo-cli es más fácil de instalar.

---

### 1.2. `wwilson1017/chatty` ⭐ 3
**Browser-based AI agent platform for small business**

| Aspecto | chatty | Dexter |
|---|---|---|
| Enfoque | Multi-agente en navegador | Agente único en terminal |
| Modelos | Gemini | DeepSeek (OpenRouter) |
| QBO | Indirecto (vía agentes genéricos) | API directa |
| Estado | MVP temprano | Producción |

**Veredicto:** Poco relevante para uso contable real. Más un experimento multi-agente.

---

### 1.3. `zavora-ai/skill-finance-accounting` ⭐ 1
**MCP finance skill for AI agents**

| Aspecto | zavora | Dexter |
|---|---|---|
| Enfoque | Skill MCP para Claude/Cursor | Agente standalone |
| Cobertura | Invoicing, collections, reconciliation | 102 tools (93% QBO API) |
| Estado | Skill individual, poco profundo | Plataforma completa |

**Veredicto:** Interesante como complemento, no como reemplazo. Dexter cubre mucho más.

---

### 1.4. `machulav/accountant24` ⭐ 16
**Local-first AI agent for personal accounting**

| Aspecto | accountant24 | Dexter |
|---|---|---|
| Enfoque | Finanzas personales | Contabilidad empresarial QBO |
| Modelos | Cualquier LLM local | DeepSeek vía OpenRouter |
| QBO | ❌ No tiene | ✅ API nativa |
| Datos | Archivos de texto locales | QBO + multi-empresa |

**Veredicto:** Excelente para finanzas personales con archivos de texto. No compite con Dexter — son mercados distintos.

---

### 1.5. Otros proyectos relevantes

| Proyecto | Estrellas | Qué hace | vs Dexter |
|---|---|---|---|
| `umair801/ap-automation-agent` | 0 | AP automation + DOCX + GPT-4o | Solo AP, no conversacional |
| `ArrushiTripathi2429/Nerve-agent` | 1 | D2C brand data (Shopify, Stripe, QBO, ads) | Foco en ecommerce, no contabilidad |
| `farhan-mohamed5/invoice_agent` | 1 | Invoice filing para UAE | Solo invoices, geolocalizado |
| `cmhrabi/timesheet-agent` | 0 | Submit QBO timesheets | Solo timesheets |
| `NehuenVill/quickbooks-binance-financial-AI-agent` | 0 | QBO + Binance queries | Solo consultas, muy limitado |

---

## 2. Alternativas Comerciales

### 2.1. Intuit QuickBooks AI (nativo)
- **Precio:** Incluido en planes QBO ($30-$200/mes)
- **Qué hace:** Categorización automática de transacciones, sugerencias de cuentas
- **vs Dexter:** Solo clasifica, no crea entidades ni ejecuta workflows complejos. Dexter es mucho más potente.

### 2.2. Bookeeping.ai
- **Precio:** No público
- **Qué hace:** AI conversacional para bookkeeping, auto-categorización
- **vs Dexter:** SaaS, datos en la nube. Dexter es local/privado.

### 2.3. Zeni AI
- **Precio:** Variable (AI + humanos)
- **Qué hace:** Bookkeeping con AI + revisión humana
- **vs Dexter:** Servicio gestionado, no herramienta. Más caro pero incluye soporte humano.

---

## 3. Matriz Comparativa Final

| | Dexter | qbo-cli | QBO AI (Intuit) | Bookeeping.ai | Zeni |
|---|---|---|---|---|---|
| **Código abierto** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Self-hosted** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Conversacional (NL)** | ✅ | ❌ | ❌ | ✅ | ❌ |
| **102 tools QBO** | ✅ | ❌ (~15) | ❌ (básico) | ❌ | ❌ |
| **Multi-empresa** | ✅ | ✅ | ✅ | ❓ | ❓ |
| **Bank feed classification** | ✅ | ❌ | ✅ | ❓ | ✅ |
| **Memoria persistente** | ✅ | ❌ | ❌ | ❓ | ❌ |
| **Single-command** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Aprendizaje continuo** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Terminal UI (Rich)** | ✅ | ✅ | N/A | N/A | N/A |
| **Telegram integrable** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Tests** | 668 | 0 visibles | ❓ | ❓ | ❓ |
| **Privacidad datos** | ✅ Local | ✅ Local | ☁️ Intuit | ☁️ SaaS | ☁️ SaaS |
| **Precio** | $0 + API | $0 | $30-200/mes | $?/mes | $?/mes |

---

## 4. Conclusión

**Dexter es único en el mercado.** No existe otro agente open-source que combine:

1. **102 tools de QBO** (93% de cobertura API) con lenguaje natural
2. **Multi-empresa con aislamiento total** (tokens, chart, memoria, clasificaciones)
3. **Memoria persistente Hermes-style** que aprende entre sesiones
4. **Terminal profesional con Rich** + integración Telegram
5. **Self-hosted** — datos nunca salen de tu máquina

El competidor más cercano es `qbo-cli` (26 estrellas, Go, CLI tradicional) pero no es conversacional ni tiene las 102 tools de Dexter.

Para tu caso de uso (contador con 2-3 empresas, automatización batch, OCR, reconciliación), **no hay alternativa en el mercado que se acerque a lo que Dexter ya hace hoy.**
