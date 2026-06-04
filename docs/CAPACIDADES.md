# 🔧 Catálogo de Capacidades

Catálogo exhaustivo de las **43 function tools** organizadas en **14 módulos de dominio** que componen QuickBooks AI Assistant (Dexter).

> **Versión del proyecto:** 4.0.0-dev
> **Total de tools:** 43
> **Total de módulos de dominio:** 14
> **Organización:** `dexter/tools/` (refactor Fases 0-7, 2026-06-04)
> **Novedades v4.0:** Registry modular, data-driven tool routing, BNK-RECON tag-only, batch genérico, multi-empresa persistencia
> **Documentación técnica:** `dexter/tools/README.md`

---

## 📊 Resumen ejecutivo

| Módulo | Tools | Categoría | Descripción |
|--------|---:|---|-------------|
| `search` | 4 | Búsqueda | Localizar clientes, vendors, cuentas, items |
| `transactions` | 4 | Crear | Crear invoices, bills, deposits, payments |
| `reports` | 5 | Reportes | P&L, balance sheet, guardar/cargar/listar configs |
| `tokens` | 2 | Tracking | Estadísticas de uso + informe Excel |
| `admin` | 2 | Administración | Refrescar chart, multi-empresa |
| `batch` | 3 | Lote | CSV depósitos, template, batch engine |
| `reconciliation` | 3 | Reconciliación | BNK-RECON tag-only (no crea txns) |
| `ocr` | 1 | OCR | Procesar PDFs de `Pending bills/` |
| `behavior` | 4 | Learning | Aprender, sugerencias, correcciones, contexto |
| `report_custom` | 2 | Reportes | Reportes dinámicos, parsear fechas |
| `api_explorer` | 5 | API | 26 endpoints QBO + web search + docs |
| `journal` | 2 | Asientos | Journal entry, transferencia |
| `web_code` | 1 | Ejecución | Ejecutar Python dinámicamente |
| `bank_feed` | 5 | Bank Feed | Clasificación inteligente + CSV processor |
| **TOTAL** | **43** | | |

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
- **[`dexter/tools/README.md`](../dexter/tools/README.md)** — 🆕 v4.0: Registry modular de 43 tools en 14 dominios

---

## 🆕 Cambios en v4.0 (Refactor modular)

**2026-06-04 — Fases 0-7 del refactor main.py → dexter/tools/**

### Antes (v3.7)
- 32 tools hardcoded en `main.py` monolítico (~3,000 líneas)
- `get_relevant_tools()` con 27 keywords hardcoded (no escalable)
- Agregar un tool nuevo = editar `main.py` en 4+ lugares

### Ahora (v4.0)
- 43 tools en 14 módulos de `dexter/tools/` (registry limpia)
- `get_relevant_tools()` data-driven (KEYWORDS en cada módulo, cobertura 100%)
- Agregar un tool = crear/editar un módulo (1-2 lugares)
- `dexter/tools/__init__.py` es el registry agregador (`ALL_SCHEMAS`, `ALL_FUNCTIONS`, `KEYWORDS_BY_MODULE`)
- **0 líneas removidas de main.py** — backward compat 100%

### Mapeo: tools anteriores → módulos

| Categoría v3.7 | Módulo v4.0 |
|----------------|-------------|
| Búsquedas (4) + Transacciones (4) + Reportes (3+2) | `search` + `transactions` + `reports` |
| Web Search (2) + API Explorer (5) + Code (1) | `api_explorer` (5) + `web_code` (1) + `journal` (2) |
| Bank Feed Intelligence (4) + Procesar CSV (1) | `bank_feed` (5) |
| User Behavior Learning (4) | `behavior` (4) |
| Dynamic Report Generator (2) | `report_custom` (2) |
| Multi-empresa (1) | `admin` (2, incluye `refrescar_chart_accounts`) |
| *(nuevo)* | `batch` (3) — `procesar_csv_depositos`, `crear_template_csv`, `depositar_lote_csv` |
| *(nuevo)* | `reconciliation` (3) — BNK-RECON tag-only |
| *(nuevo)* | `ocr` (1) — `procesar_lote_bills` |
| *(nuevo)* | `tokens` (2) — `obtener_estadisticas_tokens`, `generar_informe_tokens` |

**Para más detalles técnicos, ver [`dexter/tools/README.md`](../dexter/tools/README.md)**.
