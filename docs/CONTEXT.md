# QuickBooks AI Assistant - Context Documentation

**Versión:** 4.0.0-dev 🆕  
**Fecha:** Junio 2026 (Refactor modular Fases 0-7 + sistema de logging)  
**Asistente:** Dexter (IA Experto)  
**Desarrollador:** Alfredo  
**LLM:** DeepSeek V3 + Llama 3 (Hybrid Routing vía OpenRouter)  

> **Nota (2026-06-04):** Refactor monolítico → registry modular completado. 46 tools en 14 módulos de `dexter/tools/` + sistema de logging de errores en `dexter/error_log.py`. Para el catálogo exhaustivo de tools, ver [`CAPACIDADES.md`](CAPACIDADES.md). Para arquitectura técnica, ver [`ARCHITECTURE.md`](ARCHITECTURE.md) y [`dexter/tools/README.md`](../dexter/tools/README.md). Para multi-empresa, ver [`MULTI_EMPRESA.md`](MULTI_EMPRESA.md). Para cambios recientes, ver [`CHANGELOG.md`](CHANGELOG.md). Para el log de desarrollo técnico, ver [`roadmap/DEVELOPMENT_LOG.md`](roadmap/DEVELOPMENT_LOG.md).

---

## 📋 OVERVIEW

QuickBooks AI Assistant (TMP AI / Dexter) es un asistente conversacional inteligente desarrollado en Python que automatiza tareas contables en QuickBooks Online mediante procesamiento de lenguaje natural. El sistema utiliza **Model Routing híbrido** (DeepSeek V3 para análisis contable complejo + Llama 3 para tareas simples) a través de OpenRouter con function calling para ejecutar operaciones contables complejas mediante comandos en español o inglés.

### Objetivo Principal

Eliminar la necesidad de navegar la interfaz de QuickBooks Online para tareas repetitivas, permitiendo al contador trabajar mediante conversación natural en español (o inglés) con comprensión de terminología contable latinoamericana.

- ✅ **Multi-Empresa PRO (v3.5)**: Registro y cambio "en caliente" de empresas con tokens aislados
- ✅ **Inteligencia Híbrida (v3.6)**: Model Routing Llama 3 ↔ DeepSeek V3 + bilingüe ES/EN con persistencia por empresa
- ✅ **Guía Interactiva (v3.7)**: Onboarding paso a paso + Matching Engine Bank Feed + Manual de Usuario vivo
- ✅ **Dexter**: Identidad y personalidad refinada del asistente
- ✅ **6 Módulos de Autonomía** con 18 funciones avanzadas
- ✅ **46 Function Tools** totales en **14 módulos de dominio** (`dexter/tools/`, v4.0)
- ✅ **Sistema de logging de errores** (`dexter/error_log.py`, v4.0) — JSONL persistido en `logs/dexter_errors.log` con categorías (api_call, tool_dispatch, user_input, auth)
- ✅ **Registry modular data-driven** (v4.0: `get_relevant_tools` itera `KEYWORDS_BY_MODULE`)
- ✅ **Optimización de tokens 57%** (ahorro masivo de costos)
- ✅ **OCR de facturas PDF** con extracción inteligente
- ✅ **System prompt dinámico** con contexto selectivo
- ✅ **Sliding window** para historial conversacional

---

## 🏗️ ARQUITECTURA

### Componentes Core

```
QuickBooks AI Assistant
├── company_manager.py (~200 líneas) 🆕 (v3.5)
│   ├── Extracción de Realm ID desde URLs
│   ├── Gestión de `meta.json` por empresa (Tokens)
│   ├── Carga/Guardado de contextos aislados
│   └── Menú interactivo de selección al inicio
│
├── main.py (~3,608 líneas) ⬆️ ACTUALIZADO v4.0 (shim de dexter.tools + log integration)
│   ├── Identidad: **Dexter** (Personalidad profesional/amigable)
│   ├── Autenticación QuickBooks OAuth 2.0 (Multi-token)
│   ├── Chart of Accounts dinámico por empresa
│   ├── 26 tool_xxx wrappers (backward compat shim)
│   ├── TOOLS + TOOL_FUNCTIONS dicts (46 entradas)
│   ├── get_relevant_tools() data-driven (KEYWORDS_BY_MODULE)
│   ├── Model Routing híbrido: Llama 3 ↔ DeepSeek V3 (v3.6)
│   ├── Bilingüe ES/EN con persistencia por empresa (v3.6)
│   ├── Sistema de tracking de tokens
│   ├── Procesamiento CSV batch
│   ├── Bank Feed Intelligence (Aislado por empresa)
│   ├── Matching Engine para conciliación inteligente (v3.7)
│   ├── Sistema de Onboarding interactivo (v3.7)
│   ├── OCR de Bills (PDFs)
│   └── Loop conversacional optimizado
│
├── autonomia/ 🆕
│   ├── __init__.py
│   ├── autonomia_nivel1_websearch.py (2.5 KB)
│   │   ├── tool_search_web
│   │   └── tool_search_qbo_docs
│   ├── autonomia_nivel2_api_explorer.py (4.4 KB)
│   │   ├── tool_create_journal_entry
│   │   ├── tool_create_transfer
│   │   ├── tool_qbo_generic_request
│   │   ├── tool_list_qbo_endpoints
│   │   └── tool_get_endpoint_info
│   ├── autonomia_nivel3_code_executor.py (1.1 KB)
│   │   └── tool_execute_python
│   ├── bank_feed_intelligence.py (3.3 KB)
│   │   ├── tool_analyze_bankfeed_for_classification
│   │   ├── tool_record_bankfeed_classification
│   │   ├── tool_get_classification_history_stats
│   │   └── tool_find_pattern_for_transaction
│   ├── user_behavior_learning.py (3.1 KB)
│   │   ├── tool_learn_from_interaction
│   │   ├── tool_get_user_suggestions
│   │   ├── tool_record_user_correction
│   │   └── tool_get_conversation_context
│   └── dynamic_report_generator.py (2.0 KB)
│       ├── tool_generate_custom_report
│       └── tool_parse_date_expression
│
├── .env (credenciales)
│   ├── QB_ACCESS_TOKEN
│   ├── QB_REFRESH_TOKEN
│   ├── QB_CLIENT_ID
│   ├── QB_CLIENT_SECRET
│   ├── QB_REALM_ID
│   ├── OPENROUTER_API_KEY
│   └── GEMINI_API_KEY 🆕
│
└── Archivos generados automáticamente:
    ├── chartofaccounts.json (caché, auto-generado)
    ├── savedreports.json (configuraciones)
    ├── tokenusage.csv (histórico)
    ├── tokenusagereport.xlsx (sobrescribe)
    └── depositstemplate.csv (plantilla)
```

### Stack Tecnológico

- **Python 3.9+**
- **QuickBooks Online API v3**
- **OpenRouter API** (DeepSeek V3)
- **Google Gemini API** (Flash 2.0 - OCR) 🆕
- **pandas** - Procesamiento de datos
- **openpyxl** - Generación de Excel
- **requests** - HTTP requests
- **python-dotenv** - Manejo de credenciales
- **PyPDF2** 🆕 - Extracción de texto de PDFs

---

## 🔑 CARACTERÍSTICAS PRINCIPALES

### 1. Chart of Accounts (Fuente de Verdad: QBO)

**Implementación:**
- ✅ Carga automática desde QuickBooks Online al iniciar
- ✅ Caché local opcional (`chartofaccounts.json`)
- ✅ Actualización automática cada 24 horas
- ✅ Refresh manual con comando: `refrescar chart`
- ❌ El usuario NUNCA edita el JSON manualmente

**Funcionalidades:**
```python
def load_chart_of_accounts(force_refresh: bool = False) -> dict:
    """
    - Si force_refresh=False: carga desde caché si < 24 horas
    - Si force_refresh=True: descarga desde QBO API
    - Categoriza automáticamente: ACTIVO/PASIVO/INGRESO/GASTO
    - Almacena: ID, nombre, número, tipo, subtipo, balance
    """
```

**Fuzzy Matching:**
- Similitud mínima: 60% (SequenceMatcher)
- Búsqueda por nombre o número de cuenta
- Filtrado opcional por categoría
- Ordenamiento por score de similitud

---

### 2. 🆕 Sistema de Optimización de Tokens (57% reducción)

**Funciones Implementadas:**

#### A. `get_relevant_tools(user_message)` 
Filtra tools dinámicamente según contexto del mensaje:

```python
def get_relevant_tools(user_message: str) -> dict:
    """
    Retorna solo tools relevantes según keywords detectadas

    Detección:
    - "clasificar" → analizarbankfeed, reconocertransaccion
    - "reporte" → generarreportepl, generarbalancesheet  
    - "busca" → searchcustomer, searchvendor, findaccount
    - "bill" → procesarlotebills, createbill

    Default: Siempre incluye searchcustomer y generarreportepl
    """
```

**Ahorro:** ~40% de tokens en tool definitions

#### B. `build_conversation_context(history, max_turns=5)`
Implementa sliding window para historial:

```python
def build_conversation_context(history, max_turns=5):
    """
    Retorna: (recent_history, context_hints)

    - recent_history: Últimos 5 turnos (10 mensajes)
    - context_hints: Keywords detectados ("reportes", "clasificación")

    Optimización: Envía solo últimos 5 turnos en lugar de historial completo
    """
```

**Ahorro:** ~30% de tokens en historial

#### C. `necesita_chart(msg)`
Determina si incluir chart of accounts en system prompt:

```python
def necesita_chart(msg: str) -> bool:
    """
    Detecta keywords: clasificar, cuenta, bill, journal, asiento

    Si True: Incluye chart summary en system prompt
    Si False: System prompt más corto sin chart info
    """
```

**Ahorro:** ~25% de tokens en system prompt

**Resultados de Optimización:**

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Tokens/llamada | ~8,000 | ~3,500 | **56.25%** ⬇️ |
| Costo/1000 llamadas | $3.70 | $1.59 | **$2.11** ahorro |
| Duración $10 | 2.7 meses | **6.3 meses** | **+133%** ⏰ |
| Latencia | 1.2s | 0.8s | **+33%** más rápido |

---

### 3. 🆕 OCR de Facturas (Bills) PDF

**Módulo:** `ocr_bills.py`

**Funcionalidad:**
Extrae automáticamente información de facturas en PDF y genera CSV para importación:

```python
def extraer_bills_de_pdf(pdf_path: str, gemini_api_key: str) -> dict:
    """
    Procesa PDF de factura y extrae:
    - Vendor/Supplier
    - Invoice Number
    - Date
    - Due Date
    - Total Amount
    - Line Items (descripción, cantidad, precio unitario)
    - Tax Amount
    """
```

**Proceso:**
1. Usuario coloca PDFs en carpeta `Pending bills/`
2. Comando: `"Procesa los bills pendientes"`
3. Sistema extrae texto de cada PDF
4. Gemini Flash 2.0 analiza y estructura datos
5. Genera CSV preview en `Pending bills/preview_bills.csv`
6. Usuario revisa y aprueba
7. Sistema crea Bills en QuickBooks

**Formato CSV Generado:**
```csv
vendor,invoice_number,date,due_date,total,description,quantity,rate,account,pdf_file
ACME Corp,INV-12345,2026-01-15,2026-02-15,1250.00,Office Supplies,1,1250.00,Office Supplies,acme_jan.pdf
```

**Comando en Asistente:**
```
Usuario: "Procesa los PDFs de facturas en Pending bills"
Asistente: 
   📄 Procesando 3 PDFs...
   ✅ acme_jan.pdf → Vendor: ACME Corp ($1,250.00)
   ✅ tech_supply.pdf → Vendor: Tech Supply ($850.50)
   ❌ damaged_file.pdf → Error: PDF corrupto

   CSV generado: Pending bills/preview_bills.csv
   Revisa y di "aprobar" para crear bills en QuickBooks
```

---

### 4. Sistema de Tracking de Tokens

**Arquitectura de Doble Archivo:**

#### A. CSV Histórico (`tokenusage.csv`)
- **Modo:** Append (nunca sobrescribe)
- **Actualización:** Al cerrar cada sesión
- **Estructura:**
  ```csv
  fecha,sesion_inicio,sesion_fin,duracion_min,input_tokens,output_tokens,total_tokens,costo_usd,operaciones,detalles
  2026-01-20,14:30,15:45,75,45820,8340,54160,0.0238,12,"8 searches, 3 deposits"
  ```

#### B. Informe Excel (`tokenusagereport.xlsx`)
- **Modo:** Sobrescribe (siempre mismo nombre)
- **Generación:** On-demand con comando
- **Comando:** `"dame el informe de tokens"`

**Cálculo de Costos:**
```python
PRICE_INPUT_PER_1M = 0.19   # USD por millón de tokens
PRICE_OUTPUT_PER_1M = 0.87  # USD por millón de tokens
```

---

### 5. 31 Function Tools para el LLM 🆕

El sistema implementa 31 tools organizadas en 2 categorías:

#### **A. TOOLS BÁSICAS (13)**

##### Búsquedas (4 tools)
1. **`buscar_cliente`** - Fuzzy search de clientes
2. **`buscar_vendor`** - Búsqueda de proveedores
3. **`buscar_cuenta`** - Búsqueda en Chart of Accounts
4. **`buscar_item`** - Búsqueda de items/servicios

##### Transacciones (4 tools)
5. **`crear_invoice`** - Crear factura
6. **`crear_bill`** - Crear cuenta por pagar
7. **`crear_deposito`** - Crear depósito bancario
8. **`crear_pago`** - Registrar pago recibido

##### Reportes (3 tools)
9. **`generar_reporte_pl`** - Profit & Loss
10. **`generar_balance_sheet`** - Balance General
11. **`guardar_reporte`** - Guardar configuración

##### Gestión (2 tools)
12. **`cargar_reporte`** - Cargar configuración guardada
13. **`listar_reportes_guardados`** - Listar todos los reportes

#### **B. TOOLS DE AUTONOMÍA (18)** 🆕

##### NIVEL 1: Web Search (2 tools)
14. **`buscarenweb`** - Búsqueda en web con API
   ```python
   tool_search_web(query: str, max_results: int = 5)
   # Busca información actualizada en internet
   ```

15. **`buscardocsqbo`** - Búsqueda en documentación QuickBooks
   ```python
   tool_search_qbo_docs(query: str)
   # Busca en docs oficiales de QuickBooks API
   ```

##### NIVEL 2: API Explorer (5 tools)
16. **`crearasientodiario`** - Crear Journal Entry
   ```python
   tool_create_journal_entry(lines: List[dict], date: str, memo: str)
   # Crea asientos contables complejos
   ```

17. **`creartransferencia`** - Crear Transfer entre cuentas
   ```python
   tool_create_transfer(from_account_id: str, to_account_id: str, 
                        amount: float, date: str)
   ```

18. **`qborequestgenerico`** - Request genérico a QBO API
   ```python
   tool_qbo_generic_request(method: str, endpoint: str, data: dict)
   # Acceso directo a cualquier endpoint de QBO
   ```

19. **`listarendpointsqbo`** - Listar endpoints disponibles
   ```python
   tool_list_qbo_endpoints(category: str = None)
   # Retorna lista de endpoints de QBO API
   ```

20. **`infoendpointqbo`** - Info de endpoint específico
   ```python
   tool_get_endpoint_info(endpoint: str)
   # Retorna documentación y parámetros del endpoint
   ```

##### NIVEL 3: Code Executor (1 tool)
21. **`ejecutarcodigo`** - Ejecutar Python dinámicamente
   ```python
   tool_execute_python(code: str, timeout: int = 30)
   # Ejecuta código Python para análisis avanzados
   # Ejemplo: Calcular métricas, analizar tendencias, etc.
   ```

##### Bank Feed Intelligence (4 tools)
22. **`analizarbankfeed`** - Analizar transacciones
   ```python
   tool_analyze_bankfeed_for_classification(transactions: List[dict])
   # Sugiere clasificaciones basadas en patrones históricos
   ```

23. **`registrarclasificacion`** - Guardar clasificaciones
   ```python
   tool_record_bankfeed_classification(transaction_id: str, 
                                       classification: dict)
   # Aprende de clasificaciones manuales
   ```

24. **`estadisticasclasificacion`** - Estadísticas
   ```python
   tool_get_classification_history_stats()
   # Retorna métricas de precisión y patrones detectados
   ```

25. **`buscarpatron`** - Buscar patrones históricos
   ```python
   tool_find_pattern_for_transaction(description: str, amount: float)
   # Encuentra clasificaciones similares previas
   ```

##### User Behavior Learning (4 tools)
26. **`aprenderinteraccion`** - Aprender de interacciones
   ```python
   tool_learn_from_interaction(user_action: dict, context: dict)
   # Registra patrones de uso del usuario
   ```

27. **`obtenersugerencias`** - Sugerencias personalizadas
   ```python
   tool_get_user_suggestions(context: str)
   # Sugiere acciones basadas en historial
   ```

28. **`registrarcorreccion`** - Registrar correcciones
   ```python
   tool_record_user_correction(original: dict, corrected: dict)
   # Aprende de correcciones del usuario
   ```

29. **`obtenercontexto`** - Contexto de conversación
   ```python
   tool_get_conversation_context(turns: int = 10)
   # Retorna resumen del contexto reciente
   ```

##### Dynamic Report Generator (2 tools)
30. **`generarreportecustom`** - Reportes personalizados
   ```python
   tool_generate_custom_report(query: str, parameters: dict)
   # Genera reportes con lenguaje natural
   # Ejemplo: "ventas por cliente del último trimestre"
   ```

31. **`parsearfecha`** - Parsear expresiones de fecha
   ```python
   tool_parse_date_expression(expression: str)
   # Convierte "último mes" → fecha específica
   ```

---

### 6. 🆕 System Prompt Dinámico y Optimizado

**Antes (v2.0):** ~120 líneas, prompt estático
**Después (v3.0):** ~25 líneas, prompt dinámico con contexto

```python
def call_llm(user_message: str, tools: list = None):
    # 1. Determinar tools relevantes
    relevant_tools = get_relevant_tools(user_message)

    # 2. Aplicar sliding window al historial
    recent_hist, context_hint = build_conversation_context(conversation_history)

    # 3. Construir system prompt condicional
    system_content = SYSTEM_PROMPT

    if necesita_chart(user_message):
        chart_summary = f"{len(chart_of_accounts)} cuentas disponibles"
        system_content += chart_summary

    system_content += context_hint

    # 4. Llamar a LLM con contexto optimizado
    ...
```

**System Prompt Optimizado:**
```
Eres asistente IA para QuickBooks. Tono natural y amigable.

CAPACIDADES: Clasificación, Reportes, Facturas, Búsquedas, OCR

REGLAS:
1. Español, usa "Alfredo"
2. Asume defaults (mes actual)
3. Confirma antes de ejecutar
4. Mantén contexto
5. Emojis 📊💰✅

TÉRMINOS:
- anticipo → customer deposit (pasivo)
- prepago → prepaid expense (activo)
- proveedor → vendor
- factura → invoice

VALIDACIONES CRÍTICAS:
- Verificar existencia antes de crear transacciones
- Sugerir alternativas con fuzzy matching
- Advertir si categoría incorrecta
- Validar sumas en depósitos
```

---

### 7. Bank Feed Processing (Depósitos con Splits)

**Funcionalidad:**
Procesa transacciones bancarias complejas donde un solo depósito contiene múltiples componentes.

**Ejemplo Real:**
```
Bank Deposit: $2,375.00

Composición:
  - Cliente A: $1,500.00 (Income)
  - Cliente B: $900.00 (Income)
  - Fee: -$25.00 (Expense)
  Total: $2,375.00 ✅
```

**Proceso:**
1. Agrupa líneas por `deposit_id`
2. Valida suma = `bank_feed_amount`
3. Crea UN depósito con múltiples líneas
4. Asocia ingresos a clientes
5. Registra fees en cuenta de gastos

---

### 8. Reconciliación Bancaria Automatizada

**Dos Modos:**

#### Modo A: CON Balance (Validación Completa)
```csv
date,description,debit,credit,balance,reference
2026-01-01,Opening Balance,,,5000.00,
2026-01-15,Payment,,2500.00,7500.00,CHK-1234
```

**Validaciones:**
- ✅ Balance = balance anterior + credit - debit
- ✅ Opening + Credits - Debits = Ending
- ✅ Tolerancia 1 centavo para redondeo

#### Modo B: SIN Balance (Más Rápido)
```csv
date,description,debit,credit,reference
2026-01-01,Opening Balance,,,
2026-01-15,Payment,,2500.00,CHK-1234
```

**Proceso:**
1. Identifica Opening/Ending Balance
2. Valida matemática (si tiene balance)
3. Credit → Deposit (Income)
4. Debit → Bill (Expense)
5. Genera reporte de reconciliación

---

## 💬 EJEMPLOS DE USO v3.0

### Ejemplo 1: Búsqueda Web Autónoma 🆕

```
👤: "Busca en web las mejores prácticas para depreciar activos"

🤖: [Invoca tool_search_web automáticamente]

   📊 Resultados de búsqueda:

   1. IRS: Depreciación de activos empresariales
      - Método lineal vs acelerado
      - Vida útil según tipo de activo

   2. QuickBooks Blog: Cómo registrar depreciación
      - Crear cuenta Accumulated Depreciation
      - Asiento mensual de depreciación

   3. Contabilidad práctica
      - Ejemplo: Equipo de $10,000 a 5 años
      - Depreciación anual: $2,000

   ¿Quieres que te ayude a crear el asiento de depreciación?
```

### Ejemplo 2: Exploración de API 🆕

```
👤: "Lista todos los endpoints disponibles en QuickBooks API"

🤖: [Invoca tool_list_qbo_endpoints]

   📋 Endpoints disponibles (32):

   TRANSACCIONES:
   • /invoice - Crear/leer invoices
   • /bill - Gestionar bills
   • /payment - Registrar pagos
   • /deposit - Crear depósitos
   • /journalentry - Asientos contables

   CONSULTAS:
   • /customer - Gestión de clientes
   • /vendor - Gestión de vendors
   • /account - Chart of accounts
   • /item - Items y servicios

   REPORTES:
   • /reports/ProfitAndLoss
   • /reports/BalanceSheet
   • /reports/CashFlow

   ¿Sobre cuál necesitas más información?
```

### Ejemplo 3: Ejecución de Código Python 🆕

```
👤: "Calcula el promedio de ventas mensuales del último año"

🤖: [Invoca tool_execute_python]

   ```python
   # Código ejecutado:
   df = get_sales_data(start='2025-01-01', end='2025-12-31')
   monthly_avg = df.groupby(df['date'].dt.month)['amount'].sum().mean()
   print(f"Promedio mensual: ${monthly_avg:,.2f}")
   ```

   📊 Resultado:
   Promedio mensual: $45,230.50

   Desglose por mes:
   • Enero: $38,450
   • Febrero: $42,100
   • Marzo: $51,800
   ...
   • Diciembre: $48,900

   Tendencia: Crecimiento del 12% año vs año
```

### Ejemplo 4: Clasificación Inteligente de Bank Feed 🆕

```
👤: "Analiza estas transacciones y sugiere clasificaciones"

🤖: [Invoca tool_analyze_bankfeed_for_classification]

   🔍 Analizando patrones históricos...

   Transacción 1: "AMAZON.COM*123456" - $85.50
   ✅ Sugerencia: Office Supplies (95% confianza)
   Razón: 12 transacciones similares clasificadas así

   Transacción 2: "STARBUCKS #8521" - $24.30
   ✅ Sugerencia: Meals & Entertainment (88% confianza)
   Razón: Patrón detectado en últimos 3 meses

   Transacción 3: "UNKNOWN VENDOR" - $1,250.00
   ⚠️ Sin patrón encontrado
   Sugerencias posibles:
   • Equipment (si es compra de activo)
   • Professional Services (si es consultoría)
   • Other Operating Expenses

   ¿Apruebo las clasificaciones sugeridas?
```

### Ejemplo 5: OCR de Facturas PDF 🆕

```
👤: "Procesa las facturas en Pending bills/"

🤖: [Invoca procesarlotebills automáticamente]

   📂 Escaneando carpeta Pending bills/...
   📄 3 PDFs encontrados

   🔄 Procesando acme_invoice_jan.pdf...
   [Extrae texto con PyPDF2]
   [Analiza con Gemini Flash 2.0]

   ✅ Factura extraída:
      Vendor: ACME Corp
      Invoice #: INV-2026-001
      Date: 2026-01-15
      Due: 2026-02-15
      Total: $1,250.00

      Items:
      • Office Supplies x 1 @ $1,250.00

   🔄 Procesando tech_supply.pdf...
   ✅ Vendor: Tech Supply Co. - $850.50

   🔄 Procesando utility_bill.pdf...
   ✅ Vendor: Electric Company - $345.80

   ═══════════════════════════════════════════
   📊 RESUMEN
   ═══════════════════════════════════════════
   Total facturas: 3
   ✅ Procesadas: 3
   ❌ Errores: 0
   💰 Total: $2,446.30

   CSV generado: Pending bills/preview_bills.csv

   Revisa el CSV y di "aprobar" para crear bills en QuickBooks
```

### Ejemplo 6: Reporte Personalizado con Lenguaje Natural 🆕

```
👤: "Genera un reporte de gastos del último trimestre agrupado por categoría"

🤖: [Invoca tool_generate_custom_report]

   📊 Generando reporte personalizado...
   Período: 2025-10-01 a 2025-12-31 (Q4)

   ═══════════════════════════════════════════
   GASTOS POR CATEGORÍA - Q4 2025
   ═══════════════════════════════════════════

   1. Payroll                    $125,450.00 (42%)
   2. Rent & Occupancy            $45,000.00 (15%)
   3. Office Supplies              $8,230.00 (3%)
   4. Professional Services       $15,600.00 (5%)
   5. Utilities                   $6,450.00 (2%)
   6. Marketing                  $28,900.00 (10%)
   7. Insurance                  $12,500.00 (4%)
   8. Other Expenses             $55,870.00 (19%)

   ───────────────────────────────────────────
   TOTAL GASTOS:                $298,000.00
   ═══════════════════════════════════════════

   📈 Comparación vs Q3 2025:
   • Payroll: +5%
   • Marketing: +22% ⚠️ (revisar ROI)
   • Office Supplies: -8%

   ¿Quieres que lo guarde como "Gastos Q4"?
```

---

## 📊 ESTRUCTURA DE DATOS

### Session State v3.0

```python
session_state = {
    "start_time": datetime.now(),
    "input_tokens": 0,
    "output_tokens": 0,
    "operations": {
        "searches": 0,
        "deposits": 0,
        "invoices": 0,
        "bills": 0,
        "payments": 0,
        "reports": 0,
        "csv_batches": 0,
        "ocr_processed": 0,  # 🆕
        "web_searches": 0,   # 🆕
        "code_executions": 0  # 🆕
    },
    "chart_of_accounts": {},
    "saved_reports": {},
    "last_search_results": {
        "customers": [],
        "vendors": [],
        "accounts": []
    },
    "optimization_stats": {  # 🆕
        "tokens_saved": 0,
        "tools_filtered": 0,
        "chart_skips": 0
    }
}
```

---

## 🚀 OPTIMIZACIONES v3.0

### 1. Caché del Chart of Accounts
- Reduce latencia: 3s → 0.1s
- Ahorra ~200 tokens/sesión

### 2. Tools Dinámicos
- Filtra tools por contexto
- Ahorra ~40% tokens en tool definitions

### 3. Sliding Window
- Solo últimos 5 turnos en historial
- Ahorra ~30% tokens en historial

### 4. System Prompt Condicional
- Chart summary solo cuando necesario
- Ahorra ~25% tokens en system prompt

### 5. Búsquedas Paralelas
```python
# El LLM hace esto automáticamente
buscar_cliente("Acme Corp")
buscar_cuenta("Client Retainers")
buscar_cuenta("Checking Account")
# Todo en una sola iteración
```

### 6. 🆕 OCR Batch Processing
- Procesa múltiples PDFs en una sola operación
- Genera CSV preview para revisión
- Evita errores de transcripción manual

### 7. 🆕 Aprendizaje de Patrones
- Bank Feed Intelligence aprende clasificaciones
- User Behavior Learning optimiza sugerencias
- Reduce tiempo de clasificación manual en 70%

---

## 📈 MÉTRICAS Y MONITOREO v3.0

### Costos Promedio (Optimizado)

| Operación | Tokens Input | Tokens Output | Costo USD | vs v2.0 |
|-----------|--------------|---------------|-----------|---------|
| Búsqueda simple | 480 | 120 | $0.0002 | **-40%** ⬇️ |
| Crear depósito | 720 | 210 | $0.0003 | **-40%** ⬇️ |
| Reporte P&L | 1500 | 480 | $0.0007 | **-42%** ⬇️ |
| CSV batch (10) | 2100 | 360 | $0.0007 | **-42%** ⬇️ |
| Bank feed (5) | 2400 | 420 | $0.0008 | **-43%** ⬇️ |
| Reconciliación | 2700 | 540 | $0.0010 | **-38%** ⬇️ |
| OCR Bill 🆕 | 1800 | 300 | $0.0006 | N/A |
| Web Search 🆕 | 900 | 180 | $0.0003 | N/A |

### Sesión Promedio v3.0
- **Duración:** 30-45 minutos
- **Tokens totales:** 15,000 - 20,000 (vs 25,000-35,000 en v2.0)
- **Costo:** $0.005 - $0.008 (vs $0.008-$0.012 en v2.0)
- **Ahorro:** **~40% por sesión**

### Proyección Mensual v3.0
- **20 sesiones/mes**
- **Tokens totales:** ~360,000 (vs ~600,000 en v2.0)
- **Costo:** **~$0.12 USD/mes** (vs $0.20 en v2.0)
- **Ahorro anual:** **$0.96 USD**

---

## 💰 VALORACIÓN Y POTENCIAL DE NEGOCIO 🆕

### Competidores Identificados

| Competidor | Precio/mes | Características Principales |
|------------|------------|----------------------------|
| **Intuit QuickBooks AI** | $65-275 | AI categorization, agents integrados |
| **Bookeeping.ai (Paula)** | No especificado | Conversational AI, auto-categorization |
| **Bookkeeper AI** | $48/usuario | AI Assistant, workflow automation |
| **Zeni AI Bookkeeping** | Variable | AI + human bookkeeping |

### Ventajas Competitivas de TMP AI

| Ventaja | TMP AI | Competidores | Valor |
|---------|--------|--------------|-------|
| **Autonomía avanzada** | ✅ 6 módulos | ❌ 0/4 | ⭐⭐⭐ ALTO |
| **Self-hosted / On-premise** | ✅ Sí | ❌ 0/4 | ⭐⭐⭐⭐ MUY ALTO |
| **Integración nativa QBO** | ✅ API directa | 1/4 (Intuit) | ⭐⭐⭐ ALTO |
| **Optimización de costos** | ✅ 57% reducción | ❌ 0/4 | ⭐⭐⭐ ALTO |
| **Aprendizaje de patrones** | ✅ Sí | 1/4 | ⭐⭐⭐ ALTO |
| **OCR de facturas** | ✅ Sí | 2/4 | ⭐⭐ MEDIO |

### Modelos de Monetización

#### OPCIÓN 1: Licencia Empresarial (On-premise) ⭐ RECOMENDADO
- **Precio:** $5,000/año por empresa
- **Target:** 5 empresas medianas
- **ARR:** $25,000
- **Valoración (4x):** $100,000
- **Valoración (25x AI SaaS):** **$625,000**
- **Esfuerzo:** Bajo | **Riesgo:** Bajo

#### OPCIÓN 2: SaaS Multi-tenant
- **Precio:** $99/mes por empresa
- **Target:** 50 empresas pequeñas
- **ARR:** $59,400
- **Valoración (4x):** $237,600
- **Valoración (25x AI SaaS):** **$1,485,000**
- **Esfuerzo:** Alto | **Riesgo:** Medio

#### OPCIÓN 3: Servicio Premium + AI
- **Precio:** $750/mes por cliente
- **Target:** 10 clientes premium
- **ARR:** $90,000
- **Valoración (4x):** $360,000
- **Valoración (25x AI SaaS):** **$2,250,000**
- **Esfuerzo:** Alto | **Riesgo:** Medio

#### OPCIÓN 4: Producto White-label
- **Precio:** $15,000-50,000 one-time + royalties
- **Target:** 2-3 firmas contables
- **ARR:** $30,000-100,000
- **Valoración (4x):** $120,000-400,000
- **Valoración (25x AI SaaS):** **$750,000-2,500,000**
- **Esfuerzo:** Medio | **Riesgo:** Bajo

### Valoración Realista del Proyecto

| Etapa | Valoración | Justificación |
|-------|-----------|---------------|
| **Estado actual (MVP)** | **$50,000 - $150,000** | Producto funcional, sin tracción comercial |
| **Con 5-10 clientes** | **$250,000 - $750,000** | Tracción inicial validada |
| **Con 50+ clientes** | **$1M - $3M** | Producto escalado con recurrencia |
| **Adquisición estratégica** | **$2M - $10M+** | Por firma grande o Intuit |

### Recomendación Estratégica (3-6 meses)

1. **Licenciar a 3-5 firmas contables locales**
   - Precio: $3,000-5,000/año
   - Target: Despachos con 10-50 clientes
   - Beneficio: Ingresos inmediatos, bajo riesgo

2. **Ofrecer como servicio managed**
   - Precio: $500-750/mes por cliente final
   - Incluye: Software + soporte
   - Beneficio: Premium pricing

3. **White-label para firma grande**
   - Precio: $25,000-50,000 one-time + royalties
   - Customización a su marca
   - Beneficio: Gran pago inicial

---

## 🔮 ROADMAP FUTURO

### En Desarrollo
1. ✅ **Optimización de tokens** (COMPLETADO v3.0)
2. ✅ **Módulos de autonomía** (COMPLETADO v3.0)
3. ✅ **OCR de facturas** (COMPLETADO v3.0)

### Próximas Características
4. **Interfaz Web** - UI con Streamlit/Flask
5. **Reportes PDF** - Generación automática
6. **Integraciones:**
   - Google Sheets
   - Slack notifications
   - Email reports
7. **Analytics Avanzado** - Dashboard de métricas
8. **Multi-company** - Soporte para múltiples empresas
9. **Voice Input** - Comandos por voz
10. **Scheduled Reports** - Reportes automáticos

### Características Avanzadas
11. **Categorización ML** - Clasificación automática con ML
12. **Detección de Anomalías** - Alertas de transacciones sospechosas
13. **Dashboard de Reconciliación** - Visualización de estado
14. **Predicción de Cash Flow** - Proyecciones con AI
15. **Automatización de Compliance** - Reportes fiscales automatizados

---

## 📚 RECURSOS

### APIs Utilizadas
- [QuickBooks Online API v3](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)
- [OpenRouter API](https://openrouter.ai/docs)
- [Google Gemini API](https://ai.google.dev/docs)

### Documentación
- [OAuth 2.0 QuickBooks](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)
- [DeepSeek V3](https://api-docs.deepseek.com/)

---

## 👨‍💻 DESARROLLO v3.0

### Estructura del Código

```python
# main.py - Organización modular (~2,500 líneas)
# ==================== CONFIGURACIÓN ====================
# ==================== UTILIDADES GENERALES ====================
# ==================== AUTENTICACIÓN QUICKBOOKS ====================
# ==================== CHART OF ACCOUNTS ====================
# ==================== TRACKING DE TOKENS ====================
# ==================== BÚSQUEDAS EN QUICKBOOKS ====================
# ==================== CREACIÓN DE TRANSACCIONES ====================
# ==================== REPORTES ====================
# ==================== PROCESAMIENTO CSV ====================
# ==================== BANK FEED PROCESSING ====================
# ==================== RECONCILIACIÓN BANCARIA ====================
# ==================== OPTIMIZACIONES 🆕 ====================
# ==================== LLM INTEGRATION ====================
# ==================== TOOLS PARA EL LLM ====================
# ==================== FUNCIONES DE LOS TOOLS ====================
# ==================== COMANDOS RÁPIDOS ====================
# ==================== LOOP PRINCIPAL ====================
# ==================== ENTRY POINT ====================
```

### Mejores Prácticas v3.0
- ✅ Type hints en todas las funciones
- ✅ Docstrings descriptivos
- ✅ Manejo de errores exhaustivo
- ✅ Logging de operaciones
- ✅ Código autodocumentado
- ✅ Validaciones matemáticas con Decimal
- ✅ Tolerancias configurables
- ✅ 🆕 Optimizaciones de tokens documentadas
- ✅ 🆕 Módulos de autonomía separados
- ✅ 🆕 Tests de integración

---

---

## 📄 LICENCIA

Proyecto privado desarrollado por Alfredo para automatización contable interna.

---

**Última actualización:** 4 de Junio, 2026 (refactor modular Fases 0-7)  
**Versión del documento:** 4.0.0-dev 🆕  
**Mantenedor:** Alfredo  

**Cambios en v4.0 (2026-06-04) — Refactor modular completo:**

> **El monolito `main.py` (3,608 líneas) se mantiene 100% intacto por backward compat, pero ahora delega a `dexter/tools/` (registry modular de 46 tools en 14 dominios) y `dexter/error_log.py` (sistema de logging de errores).**

- ✅ **Registry modular:** `dexter/tools/` con 14 módulos de dominio + `_schema_utils.py` + `__init__.py` agregador. Cada módulo declara `SCHEMA` + `FUNCTIONS` + `KEYWORDS` (data-driven routing).
- ✅ **Data-driven tool routing:** `get_relevant_tools()` itera `KEYWORDS_BY_MODULE` en vez de 27 keywords hardcoded. Cobertura: 46/46 tools pueden activarse.
- ✅ **Investigación "stubs fantasma":** empíricamente demostrado que NO HAY STUBS — los 46 tools son reales. El análisis previo usó regex malo. `dexter/tools/` ahora los cubre todos.
- ✅ **Backward compat total:** 0 líneas removidas de main.py. `from main import tool_xxx` sigue funcionando (24 tool_xxx wrappers).
- ✅ **Tests:** 287/287 pasando (+25 nuevos: 11 aggregator + 2 shim + 3 parametrizados de los 14 dominios + 9 verificados).
- ✅ **Documentación:** `dexter/tools/README.md` nuevo, `CHANGELOG.md` actualizado con métricas, `CAPACIDADES.md` reescrito (46 tools en 14 módulos), `ARCHITECTURE.md` extendido con diagrama v4.0.
- 📦 **Distribuciones de tools por dominio:** `bank_feed` (5), `search` (4), `transactions` (5)⬆️, `reports` (5), `tokens` (2), `admin` (4)⬆️, `batch` (3), `reconciliation` (3), `ocr` (1), `behavior` (4), `report_custom` (2), `api_explorer` (5), `journal` (2), `web_code` (1) = **46 totales**.

**Cambios en v3.7:**
- ✅ **Guía Interactiva:** Dexter detecta el estado de las carpetas y guía al usuario paso a paso (Onboarding).
- ✅ **Matching Engine:** Diseño técnico del motor de conciliación inteligente entre CSVs bancarios y QBO (evita duplicados).
- ✅ **Manual de Usuario Vivo:** `USER_GUIDE.md` integrado como base de conocimiento para auto-explicación de Dexter.

**Cambios en v3.6:**
- ✅ **Model Routing híbrido:** Llama 3 (tareas simples, bajo costo) ↔ DeepSeek V3 (análisis contable complejo).
- ✅ **Bilingüe ES/EN:** Traducción dinámica con persistencia de idioma por empresa en `meta.json`.

**Cambios en v3.5:**
- ✅ **Identidad:** El asistente ahora se llama **Dexter**.
- ✅ **Multi-Empresa:** Implementado `company_manager.py` para soporte ilimitado de empresas.
- ✅ **Hot-Swap:** Cambio de empresa sin reiniciar la aplicación con tokens aislados.
- ✅ **Persistencia:** Almacenamiento de contexto (Chart, Reportes, Reglas) por empresa en `companies/`.
- ✅ **Actualizado:** De ~2,500 a ~3,000 líneas de código totales.

**Cambios en v3.0 (Previo):**
- ✅ Agregados 6 módulos de autonomía con 18 funciones
- ✅ Implementada optimización de tokens (57% reducción)
- ✅ Agregado OCR de facturas PDF con Gemini
- ✅ System prompt dinámico con contexto selectivo
- ✅ Sliding window para historial conversacional
- ✅ Análisis de mercado y valoración del proyecto
