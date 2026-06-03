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
