# QuickBooks Online API v3 — Investigación Exhaustiva

> **Propósito**: Documento de referencia completa de la QBO API para identificar
> gaps en Dexter (46 tools actuales) y guiar el roadmap de cobertura.
>
> **Fecha**: 4 de Junio, 2026
> **Autor**: Investigación asistida por opencode
> **Versión del API investigada**: minorversion 70+ (producción) y 75+ (sandbox)
> **Fuentes**:
> - [Intuit Developer — QBO Accounting API](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities)
> - [API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting)
> - [REST API features](https://developer.intuit.com/app/developer/qbo/docs/learn/rest-api-features)
> - [Data queries](https://developer.intuit.com/app/developer/qbo/docs/learn/explore-the-quickbooks-online-api/data-queries)
> - [Run reports](https://developer.intuit.com/app/developer/qbo/docs/workflows/run-reports)
> - [Attach images and notes](https://developer.intuit.com/app/developer/qbo/docs/workflows/attach-images-and-notes)
> - [Satva Solutions — QBO API Guide 2026](https://satvasolutions.com/blog/quickbooks-online-api-guide)
> - [Knit — QBO API Integration Guide 2026](https://getknit.dev/blog/quickbooks-online-api-integration-guide-in-depth)
> - [QuickBooks REST API Reference](https://quickbooks.rest/)
> - Documentación SDK oficial de Intuit (PHP, .NET, Java, Node.js)

---

## 1. Resumen ejecutivo

La **QuickBooks Online Accounting API v3** expone un modelo de datos completo
de contabilidad con:

- **~70+ entidades** distribuidas en 3 categorías (transaccionales, listas de
  nombres, entidades de soporte).
- **30+ tipos de reportes** financieros y operacionales.
- **7 operaciones CRUD-like** por entidad: Create, Read, Update, Delete (soft
  o hard), Query, Void (transacciones), Send (facturas/POs).
- **Operaciones especiales**: Batch (multi-acción), Recurring Transactions
  (plantillas), Attachments (upload/download), Webhooks (eventos),
  Preferences (configuración de empresa), CompanyInfo (datos fiscales).
- **Query language SQL-like** con paginación, ordenamiento, COUNT.
- **Rate limits**: 500 req/min/realm, 40 concurrent, batch max 30 payloads.
- **Minor versions** (actualmente ~70-75) que agregan campos incrementalmente.

**Cobertura actual de Dexter**: 46 tools en 14 módulos — **aproximadamente
un 35-40% de la superficie útil de la API**. Hay brechas importantes
especialmente en: creación de master data (Vendor, Employee, Item, Account,
Class, Department, Term, PaymentMethod), void/delete, reportes operacionales
(A/R Aging, A/P Aging, Trial Balance, General Ledger), y operaciones
especiales (batch, recurring, attachments, webhooks).

---

## 2. Modelo de datos — Las 3 categorías de entidades

### 2.1. Entidades transaccionales (15)

Operan con dinero. Soportan Create/Read/Update/Query/**Delete (hard) o Void**.

| # | Entidad | Español | Operaciones | Notas |
|---|---|---|---|---|
| 1 | `Invoice` | Factura | C/R/U/D/Send/Email | Soporta **SendEmail** (`POST /invoice/{id}/send`) |
| 2 | `Bill` | Cuenta por pagar | C/R/U/D | Soporta attach + payment |
| 3 | `BillPayment` | Pago de bill | C/R/U/D/**Void** | Vincula bills a pagar |
| 4 | `Payment` | Pago de cliente | C/R/U/D/**Void** | Aplica a invoices |
| 5 | `CreditMemo` | Nota de crédito | C/R/U/D | Reduce balance de cliente |
| 6 | `RefundReceipt` | Recibo de reembolso | C/R/U/D | Reembolso a cliente |
| 7 | `SalesReceipt` | Recibo de venta | C/R/U/D/**Void** | Venta inmediata con pago |
| 8 | `Estimate` | Cotización | C/R/U/D | Puede convertirse a Invoice |
| 9 | `Purchase` | Compra genérica | C/R/U/D | Check / CC / Cash expense |
| 10 | `PurchaseOrder` | Orden de compra | C/R/U/D/Send | **SendEmail** (`POST /purchaseorder/{id}/send`) |
| 11 | `VendorCredit` | Crédito de proveedor | C/R/U/D | Reduce balance de vendor |
| 12 | `Deposit` | Depósito bancario | C/R/U/D | Multi-línea con splits |
| 13 | `Transfer` | Transferencia | C/R/U/D | Entre cuentas |
| 14 | `JournalEntry` | Asiento contable | C/R/U/D | Débito/crédito manual |
| 15 | `TimeActivity` | Registro de tiempo | C/R/U/D | Horas trabajadas (para facturación) |

**Cobertura Dexter actual**:

| Entidad | Tool | Status |
|---|---|---|
| Invoice | `crear_invoice` | ✅ |
| Bill | `crear_bill` | ✅ |
| BillPayment | — | ❌ **FALTA** |
| Payment | `crear_pago` | ✅ |
| CreditMemo | — | ❌ **FALTA** |
| RefundReceipt | — | ❌ **FALTA** |
| SalesReceipt | — | ❌ **FALTA** |
| Estimate | — | ❌ **FALTA** |
| Purchase | — | ❌ **FALTA** |
| PurchaseOrder | — | ❌ **FALTA** |
| VendorCredit | — | ❌ **FALTA** |
| Deposit | `crear_deposito` | ✅ |
| Transfer | `creartransferencia` | ✅ |
| JournalEntry | `crearasientodiario` | ✅ |
| TimeActivity | — | ❌ **FALTA** |

**Gap crítico**: 9 de 15 entidades transaccionales **no tienen tool de creación**.
Especialmente importante: **BillPayment** (pagar bills), **SalesReceipt** (ventas
mostrador), **CreditMemo** (devoluciones), **Estimate** (cotizaciones).

**Delete/Void** no están implementados para NINGUNA transacción (Dexter solo
puede crear/consultar, no eliminar). Esto es un gap importante de mantenibilidad.

### 2.2. Name list entities — Master data (15)

Datos maestros. Soportan Create/Read/Update/Query/**Delete (soft: Active=false)**.
No se pueden hard-deletear en producción (preservar integridad contable).

| # | Entidad | Español | Operaciones | Notas |
|---|---|---|---|---|
| 1 | `Customer` | Cliente | C/R/U/Q/D(soft) | Base de A/R |
| 2 | `Vendor` | Proveedor | C/R/U/Q/D(soft) | Base de A/P, campo `Vendor1099` |
| 3 | `Employee` | Empleado | C/R/U/Q/D(soft) | Para nóminas y time tracking |
| 4 | `Item` | Producto/Servicio | C/R/U/Q/D(soft) | Inventario, type=Inventory/Service/NonInventory |
| 5 | `Account` | Cuenta contable | C/R/U/Q/D(soft) | 5 tipos: Asset/Liability/Equity/Income/Expense |
| 6 | `Class` | Clase | C/R/U/Q/D(soft) | Segmento de P&L |
| 7 | `Department` | Departamento | C/R/U/Q/D(soft) | Segmento de P&L |
| 8 | `Term` | Plazo de pago | C/R/U/Q/D(soft) | Net 30, Due on receipt, etc. |
| 9 | `PaymentMethod` | Método de pago | C/R/U/Q/D(soft) | Cash, Check, Credit Card, etc. |
| 10 | `TaxCode` | Código de impuesto | C/R/U/Q | NON, TAX (los 2 principales) |
| 11 | `TaxRate` | Tasa de impuesto | C/R/U/Q | Detalle de un TaxCode |
| 12 | `TaxAgency` | Agencia tributaria | C/R/U/Q | Quién cobra el impuesto |
| 13 | `TaxService` | Servicio de tax | C/R/Q | Cálculo automático de tax |
| 14 | `CompanyCurrency` | Moneda de la empresa | C/R/U/Q | Multi-moneda |
| 15 | `JournalCode` | Código de journal | C/R/U/Q | Para journal entries |
| 16 | `OtherName` | Otro nombre | C/R/U/Q | Nombre genérico no-Customer/Vendor/Employee |

**Cobertura Dexter actual**:

| Entidad | Tool crear | Tool buscar | Status |
|---|---|---|---|
| Customer | `crear_cliente` ✅ (recién) | `buscar_cliente` ✅ | Completo |
| Vendor | — | `buscar_vendor` ✅ | **Falta crear** |
| Employee | — | — | **Falta todo** |
| Item | — | `buscar_item` ✅ | **Falta crear** |
| Account | — | `buscar_cuenta` ✅ | **Falta crear** (importante para setup) |
| Class | — | — | **Falta todo** |
| Department | — | — | **Falta todo** |
| Term | — | — | **Falta todo** |
| PaymentMethod | — | — | **Falta todo** |
| TaxCode / TaxRate | — | — | **Falta todo** |
| TaxAgency | — | — | **Falta todo** |
| CompanyCurrency | — | — | **Falta todo** |
| JournalCode | — | — | **Falta todo** |
| OtherName | — | — | **Falta todo** |

**Gap crítico**: Master data es **la base de cualquier transacción**. Sin poder
crear Vendor, Account, Item, Class, etc., el usuario tiene que entrar a la UI
de QBO manualmente para setup, lo que rompe la automatización.

### 2.3. Entidades de soporte (3)

Datos que complementan las otras entidades. No se crean/eliminan usualmente
vía API por el usuario; el sistema los gestiona.

| # | Entidad | Operaciones | Notas |
|---|---|---|---|
| 1 | `Attachable` | C/R/U/D | Adjuntos: PDFs, imágenes, notas. Upload vía `POST /upload` (multipart). Download vía `GET /download/{id}` (URL temporal 15min). |
| 2 | `CompanyInfo` | R/U | Datos fiscales de la empresa. NO se puede crear. |
| 3 | `Preferences` | R/U | Configuración de la empresa. NO se puede crear. |
| 4 | `Budget` | C/R/U/D | Presupuesto. Subentidad de CompanyInfo. |

**Cobertura Dexter actual**: ❌ 0 de 4. **Gap importante**:
- **Attachable** (vincular PDF de factura al bill — feature clave para audit trail)
- **CompanyInfo** (mostrar datos de empresa al LLM)
- **Preferences** (configurar fiscal year, accounting method, etc.)
- **Budget** (presupuestos vs real)

### 2.4. Entidades especiales

| # | Entidad | Operaciones | Notas |
|---|---|---|---|
| 1 | `RecurringTransaction` | C/R/U/D | Plantilla que genera transacciones automáticas. Soporta Invoice, Bill, JournalEntry, etc. Campos clave: `RecurType` (Automated/Reminder), `ScheduleInfo` (StartDate, IntervalType, NumInterval, etc.) |
| 2 | `Batch` | POST | Operación multi-acción. Hasta 30 payloads por request. Combina C/U/D en un solo roundtrip. |
| 3 | `CDC` (Change Data Capture) | POST | Reporta qué entidades cambiaron desde un timestamp. Útil para sync. |
| 4 | `ExchangeRate` | R | Tasas de cambio de moneda en una fecha dada. |
| 5 | `Webhooks` | (configuración en portal) | Notificaciones push cuando una entidad cambia (Create, Update, Delete, Void, Merge). Configurar URL endpoint en intuit developer portal. |

**Cobertura Dexter actual**: ❌ 0 de 5. **Gap crítico**:
- **RecurringTransaction** (automatizar invoices mensuales — feature clave)
- **Batch** (performance + rate limit compliance para CSV batch)
- **Attachable** (audit trail + vincular PDFs de OCR a bills)

---

## 3. Reportes — 30+ tipos

### 3.1. Reportes financieros principales (4)

| Reporte | Endpoint | Tool Dexter | Status |
|---|---|---|---|
| Balance Sheet | `GET /reports/BalanceSheet` | `generar_balance_sheet` | ✅ |
| Profit and Loss | `GET /reports/ProfitAndLoss` | `generar_reporte_pl` | ✅ |
| Profit and Loss Detail | `GET /reports/ProfitAndLossDetail` | — | ❌ FALTA |
| Statement of Cash Flows | `GET /reports/CashFlow` | — | ❌ FALTA |
| Trial Balance | `GET /reports/TrialBalance` | — | ❌ **FALTA** (usado en nuestro `detect_report_type`) |

### 3.2. Reportes para contadores (4)

| Reporte | Endpoint | Status |
|---|---|---|
| General Ledger | `GET /reports/GeneralLedger` | ❌ FALTA |
| Journal Report | `GET /reports/JournalReport` | ❌ FALTA |
| Account List (Detail) | `GET /reports/AccountListDetail` | ❌ FALTA |
| Tax Summary (solo FR) | `GET /reports/TaxSummary` | ❌ FALTA (no aplica a US) |

### 3.3. Reportes de A/R — Cuentas por cobrar (5)

| Reporte | Endpoint | Status |
|---|---|---|
| Customer Balance Summary | `GET /reports/CustomerBalance` | ❌ FALTA |
| Customer Balance Detail | `GET /reports/CustomerBalanceDetail` | ❌ FALTA |
| A/R Aging Summary | `GET /reports/AgedReceivables` | ❌ **FALTA** (crítico) |
| A/R Aging Detail | `GET /reports/AgedReceivableDetail` | ❌ FALTA |
| Invoice List | `GET /reports/InvoiceList` (QBO UI) | ❌ FALTA |

### 3.4. Reportes de A/P — Cuentas por pagar (3)

| Reporte | Endpoint | Status |
|---|---|---|
| Vendor Balance Summary | `GET /reports/VendorBalance` | ❌ FALTA |
| Vendor Balance Detail | `GET /reports/VendorBalanceDetail` | ❌ FALTA |
| A/P Aging Summary | `GET /reports/AgedPayables` | ❌ **FALTA** (crítico) |
| A/P Aging Detail | `GET /reports/AgedPayableDetail` | ❌ FALTA |

### 3.5. Reportes de ventas (4)

| Reporte | Endpoint | Status |
|---|---|---|
| Sales by Customer Summary | `GET /reports/CustomerSales` | ❌ FALTA |
| Sales by Product/Service Summary | `GET /reports/ItemSales` | ❌ FALTA |
| Sales by Department Summary | `GET /reports/DepartmentSales` | ❌ FALTA |
| Sales by Class Summary | `GET /reports/ClassSales` | ❌ FALTA |
| Income by Customer Summary | `GET /reports/CustomerIncome` | ❌ FALTA |

### 3.6. Reportes de gastos e inventario (3)

| Reporte | Endpoint | Status |
|---|---|---|
| Expenses by Vendor Summary | `GET /reports/VendorExpenses` | ❌ FALTA |
| Inventory Valuation Summary | `GET /reports/InventoryValuationSummary` | ❌ FALTA |
| Inventory Valuation Detail | `GET /reports/InventoryValuationDetail` | ❌ FALTA |

### 3.7. Reportes misceláneos (3)

| Reporte | Endpoint | Status |
|---|---|---|
| Transaction List | `GET /reports/TransactionList` | ❌ FALTA |
| Transaction List with Splits | `GET /reports/TransactionListWithSplits` | ❌ FALTA |
| Transaction Detail by Account | `GET /reports/TransactionDetailByAccount` | ❌ FALTA |
| General Ledger Detail | `GET /reports/GeneralLedgerDetail` | ❌ FALTA |
| Recurring Template List | `GET /reports/RecurringTemplateList` | ❌ FALTA |
| Recent Transactions | `GET /reports/RecentTransactions` | ❌ FALTA |
| Reconciliation Reports | (QBO UI) | ❌ FALTA |

### 3.8. Parámetros de reportes (todos)

Todos los reportes aceptan estos query params (de [`ReportService.php`](https://github.com/intuit/QuickBooks-V3-PHP-SDK/blob/master/src/ReportService/ReportService.php)):

```
report_date          → fecha del reporte (singular date)
start_date, end_date → rango
date_macro           → "Today", "This Week", "This Month", "This Quarter",
                       "This Year", "Last Week", "Last Month", etc.
accounting_method    → "Accrual" | "Cash"
account              → filtrar por cuenta(s)
account_type         → filtrar por tipo
summarize_column_by  → "Total", "Customers", "Vendors", "Classes", "Departments",
                       "Items", "Employees", "TaxCodes", "Time", "Locations", "PaymentMethods"
customer, vendor, item → filtrar por entidad
classid, department  → filtrar por segmento
aging_period         → número de períodos (1-12) para aging reports
aging_method         → "Report Date" | "Due Date"
num_periods          → alterno a aging_period
term                 → filtrar por plazo
columns              → "All", "TotalOnly", etc.
sort_by, sort_order  → "Asc" | "Desc"
group_by             → agrupar resultados
createdate_macro     → filtros de fecha de creación
moddate_macro        → filtros de fecha de modificación
payment_method       → filtrar
name                 → filtrar por nombre
transaction_type     → filtrar por tipo de txn
cleared, arpaid, printed → filtros booleanos
both_amount          → mostrar débito y crédito
memo, doc_num        → buscar por memo o número
```

**Cobertura Dexter actual**: 4/30+ reportes (13%). Gap importante para
firma contable que necesita A/R Aging, A/P Aging, Trial Balance, General Ledger.

---

## 4. Operaciones especiales

### 4.1. CRUD — semántica de QBO

**Update (full)**: `POST /v3/company/{realmId}/{entity}` con body = entidad
completa + `SyncToken` (optimistic locking). Si SyncToken no coincide con
la versión actual, error 409 (concurrencia).

**Update (sparse)**: `POST /v3/company/{realmId}/{entity}` con
`?operation=sparseUpdate` y body = solo los campos a cambiar + Id + SyncToken.
Más eficiente, evita race conditions.

**Delete (soft)**: name list entities → `POST /v3/company/{realmId}/{entity}`
con `?operation=delete` y body con solo `Id`, `SyncToken`, `Active=false`.
La entidad queda desactivada pero no se borra del histórico.

**Delete (hard)**: transaction entities → `POST /v3/company/{realmId}/{entity}`
con `?operation=delete` y body con `Id` y `SyncToken` (simplified delete).
Para Bill, BillPayment, CreditMemo, Estimate, Invoice, JournalEntry, Payment,
Purchase, PurchaseOrder, RefundReceipt, SalesReceipt, TimeActivity, VendorCredit.

Para otras transacciones: incluir el payload completo en el body.

**Void**: solo para Payment, BillPayment, Invoice, SalesReceipt. Cambia el
status a "voided" sin eliminar.

### 4.2. Query language

**Sintaxis** (SQL-like):
```
SELECT * | count(*)
FROM EntityName
[WHERE PropertyName Operator Value [AND ...]]
[ORDERBY PropertyName [ASC|DESC]]
[STARTPOSITION N]
[MAXRESULTS N]
```

**Operadores**: `=`, `<>`, `<`, `>`, `<=`, `>=`, `IN`, `LIKE`

**Limitaciones**:
- `OR` no soportado (usar `IN` o múltiples queries)
- Wildcard `LIKE`: solo `*` al inicio/fin del string
- Strings en comillas simples
- Paginación: `STARTPOSITION` (1-indexed) y `MAXRESULTS` (default 100, max 1000)
- `count(*)` retorna solo el número, no los registros

**Endpoints especiales**:
- `GET /query` (con query en query string, max 4096 chars)
- `POST /query` (con query en body, recomendado para queries largas)

### 4.3. Batch operations

**Endpoint**: `POST /v3/company/{realmId}/batch`

**Payload**:
```json
{
  "BatchItemRequest": [
    {
      "bId": "bid1",
      "operation": "create" | "update" | "delete" | "query",
      "Entity": {...} | "Query": "SELECT..."
    },
    ...
  ]
}
```

**Límites**:
- Max 30 payloads por batch
- 40 batch requests/minuto por realm
- 120 batch requests/minuto por realm+app
- Cada payload se procesa independientemente; un fallo no aborta el batch

**Cobertura Dexter actual**: ❌ 0. Gap importante para CSV batch y para
ahorrar rate limits.

### 4.4. Recurring transactions

**Crear**: `POST /v3/company/{realmId}/recurringtransaction` con
`RecurringInfo` embebido en la transacción base.

**ScheduleInfo**:
```json
{
  "RecurType": "Automated" | "Reminder",
  "ScheduleInfo": {
    "StartDate": "2026-01-01",
    "IntervalType": "Monthly" | "Weekly" | "Daily" | "Yearly",
    "NumInterval": 1,
    "DayOfMonth": 1,
    "DaysBefore": 2,
    "MaxOccurrences": 12,
    "NextDate": "2026-01-01"
  }
}
```

**Cobertura Dexter actual**: ❌ 0. Feature crítica para automatizar
suscripciones, alquileres, payrolls.

### 4.5. Attachments (Attachable)

**Upload** (multipart, base64):
```
POST /v3/company/{realmId}/upload
Content-Type: multipart/form-data; boundary=xxx

--xxx
Content-Disposition: form-data; name="file_metadata_01"; filename="meta.json"
Content-Type: application/json

{"AttachableRef":[{"EntityRef":{"type":"Bill","value":"123"}}], "FileName":"factura.pdf", "ContentType":"Document"}
--xxx
Content-Disposition: form-data; name="file_content_0"; filename="factura.pdf"
Content-Type: application/pdf
Content-Transfer-Encoding: base64

<base64>
--xxx--
```

**Tipos de archivo soportados** (16): PDF, JPG, PNG, GIF, TIFF, DOC, DOCX, XLS, XLSX, CSV, TXT, RTF, XML, ODS, AI, EPS.

**Max**: 100MB total por upload, múltiples archivos por request.

**Download**: `GET /v3/company/{realmId}/download/{attachableId}` retorna URL temporal (15min expiración).

**Cobertura Dexter actual**: ❌ 0. Integración con OCR (`Pending bills/`) + Attachable = workflow completo "PDF → OCR → Bill con PDF adjunto".

### 4.6. Webhooks

**Configuración**: en Intuit Developer Portal, registrar URL endpoint y
seleccionar entidades + eventos (create, update, delete, void, merge).

**Payload de notificación** (no incluye los datos modificados):
```json
{
  "eventNotifications": [
    {
      "realmId": "123146...",
      "dataChangeEvent": {
        "entities": [
          {"name": "Customer", "id": "1", "operation": "Create", "lastUpdated": "2026-06-04T11:30:00Z"}
        ]
      }
    }
  ]
}
```

**Verificación**: validar el header `intuit-signature` con HMAC-SHA256
usando el verifier token del portal.

**Cobertura Dexter actual**: ❌ 0. Útil para sync reactivo en lugar de polling.

### 4.7. Minor versions

**Cómo especificar**: agregar `?minorversion=70` (o el número que sea) en
todas las requests. Sin este param, usa la versión base (campos viejos).

**Última versión actual**: 75+ (sandbox), 70+ (producción).

**Estrategia recomendada**:
- En producción: pinear a una versión específica (e.g. `minorversion=70`)
- En sandbox: probar primero con la última (`minorversion=75`)
- Monitorear Intuit changelog para breaking changes

**Cobertura Dexter actual**: ❌ No pineado. Probablemente usa base version.

---

## 5. Autenticación y scopes

### 5.1. OAuth 2.0

**Authorization URL** (producción):
```
https://appcenter.intuit.com/connect/oauth2
  ?client_id=...
  &redirect_uri=...
  &response_type=code
  &scope=com.intuit.quickbooks.accounting
  &state=CSRF_TOKEN
```

**Token URL**:
```
https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer
```

**Scopes**:
- `com.intuit.quickbooks.accounting` — acceso completo a la API Accounting
- `com.intuit.quickbooks.payment` — acceso a la API de Payments
- `openid profile email phone address` — info del usuario

**Token lifecycle**:
- Access token: 1 hora de duración
- Refresh token: 100 días de duración, se renueva en cada uso
- Realm ID: devuelto en la query string del callback

**Cobertura Dexter**: ✅ Implementado en `scripts/refresh_token.py` y `scripts/oauth_flow.py` (recién creado).

### 5.2. Environment switching

- **Production**: `https://quickbooks.api.intuit.com/v3/company/{realmId}/`
- **Sandbox**: `https://sandbox-quickbooks.api.intuit.com/v3/company/{realmId}/`

---

## 6. Rate limits (crítico para producción)

| Límite | Valor | Notas |
|---|---|---|
| Requests/minuto/realm | 500 | Fijo |
| Concurrent requests/realm | 40 | Producción. Sandbox: 10 |
| Batch size | 30 payloads | Por request |
| Batch requests/minuto/realm | 40 | |
| Batch requests/minuto/realm+app | 120 | |
| Emails/día/realm (sandbox) | 40 | Limitado |
| Minor version timeout | 120 seg | Más allá → error |
| Throttle response | HTTP 429 | Esperar 60s y reintentar |

**Estrategia recomendada**:
- Implementar exponential backoff con jitter
- Usar batch operations para reducir roundtrips
- Cachear resultados que no cambian (Chart of Accounts, Customer list, etc.)
- Tracking de tokens en sesión para evitar recálculos

**Cobertura Dexter**: ⚠️ Parcial. Cache de Chart ✅. Exponential backoff ❌. Batch operations ❌.

---

## 7. Análisis de gaps — Dexter vs QBO API

### 7.1. Gaps críticos (P0) — Bloquean flujos importantes

| Gap | Entidad | Impacto | Esfuerzo |
|---|---|---|---|
| ❌ `crear_vendor` | Vendor | No se pueden pagar bills sin vendor. **CRÍTICO** para workflow A/P. | Bajo (paralelo a `crear_cliente`) |
| ❌ `crear_cuenta` | Account | No se puede personalizar chart of accounts via API. | Bajo |
| ❌ `crear_item` | Item | No se pueden crear productos/servicios. Necesario para invoices con items. | Medio |
| ❌ `crear_billpayment` | BillPayment | No se pueden pagar bills programáticamente. | Medio |
| ❌ `crear_estimate` | Estimate | No se pueden cotizar. | Bajo |
| ❌ `crear_salesreceipt` | SalesReceipt | No se pueden registrar ventas de mostrador. | Medio |
| ❌ `crear_creditmemo` | CreditMemo | No se pueden emitir notas de crédito. | Medio |
| ❌ `eliminar_transaccion` (DELETE) | All txn | No se puede corregir errores. **CRÍTICO** para mantenibilidad. | Bajo (usar `?operation=delete`) |
| ❌ `void_transaccion` | Payment, BillPayment, Invoice, SalesReceipt | No se puede anular (≠ eliminar). | Bajo |
| ❌ `actualizar_*` (UPDATE sparse) | Customer, Invoice, etc. | No se pueden modificar transacciones o master data. **CRÍTICO**. | Medio |
| ❌ `enviar_factura` (send) | Invoice, PurchaseOrder | No se pueden enviar por email. | Bajo (POST /invoice/{id}/send) |
| ❌ `reporte_trial_balance` | TrialBalance | Falla en `detect_report_type` cuando usuario pide "balance de prueba". | Bajo |
| ❌ `reporte_ar_aging` | AgedReceivables | **CRÍTICO** para firma contable (cobranzas). | Bajo |
| ❌ `reporte_ap_aging` | AgedPayables | **CRÍTICO** para firma contable (pagos). | Bajo |
| ❌ `reporte_general_ledger` | GeneralLedger | Auditoría. | Bajo |
| ❌ `consulta_avanzada` (query con SQL custom) | Any | El LLM no puede hacer queries arbitrarias. | Medio |

### 7.2. Gaps importantes (P1) — Mejoran cobertura

| Gap | Entidad | Impacto | Esfuerzo |
|---|---|---|---|
| ❌ `crear_empleado` | Employee | Nóminas, time tracking. | Bajo |
| ❌ `crear_clase` | Class | Segmentación P&L. | Bajo |
| ❌ `crear_departamento` | Department | Segmentación P&L. | Bajo |
| ❌ `crear_termino` | Term | Plazos de pago (Net 30, etc.). | Bajo |
| ❌ `crear_paymentmethod` | PaymentMethod | Métodos de pago. | Bajo |
| ❌ `crear_recurringtransaction` | RecurringTransaction | **CRÍTICO** para suscripciones, alquileres. | Alto |
| ❌ `crear_purchaseorder` | PurchaseOrder | Órdenes de compra. | Medio |
| ❌ `crear_refundreceipt` | RefundReceipt | Reembolsos. | Medio |
| ❌ `crear_purchase` | Purchase | Compras genéricas (CC, cash). | Medio |
| ❌ `crear_vendorcredit` | VendorCredit | Créditos de proveedor. | Medio |
| ❌ `crear_timeactivity` | TimeActivity | Horas trabajadas. | Bajo |
| ❌ `crear_transfer` ya existe ✅ | Transfer | — | — |
| ❌ `reporte_cash_flow` | CashFlow | Estado de flujos. | Bajo |
| ❌ `reporte_customer_balance` | CustomerBalance | Estado de cuenta por cliente. | Bajo |
| ❌ `reporte_vendor_balance` | VendorBalance | Estado de cuenta por vendor. | Bajo |
| ❌ `adjuntar_archivo` (Attachable) | Attachable | **CRÍTICO** para audit trail + integrar con OCR. | Alto (multipart) |
| ❌ `verificar_batch` (batch operations) | Batch | Performance, rate limits. | Alto |

### 7.3. Gaps opcionales (P2) — Nice-to-have

| Gap | Entidad | Impacto | Esfuerzo |
|---|---|---|---|
| ❌ `crear_taxcode` | TaxCode | Configuración de impuestos. | Bajo |
| ❌ `crear_taxrate` | TaxRate | Tasas de impuestos. | Bajo |
| ❌ `crear_companycurrency` | CompanyCurrency | Multi-moneda. | Medio |
| ❌ `crear_budget` | Budget | Presupuestos vs real. | Alto |
| ❌ `leer_companyinfo` | CompanyInfo | Mostrar info de empresa al LLM. | Bajo |
| ❌ `leer_preferences` | Preferences | Configuración actual. | Bajo |
| ❌ `actualizar_preferences` | Preferences | Cambiar config. | Medio |
| ❌ `webhook_setup` | Webhooks | Notificaciones push. | Alto (requiere HTTPS endpoint) |
| ❌ `cdc_query` | CDC | Sync incremental. | Medio |
| ❌ `exchange_rate` | ExchangeRate | Tasas de cambio. | Bajo |

### 7.4. Resumen de cobertura

| Categoría | Cubierto | Total | % |
|---|---|---|---|
| Transacciones (create) | 6 | 15 | 40% |
| Transacciones (delete/void) | 0 | 15 | 0% |
| Transacciones (update) | 0 | 15 | 0% |
| Master data (create) | 1 | 16 | 6% |
| Master data (read/search) | 4 | 16 | 25% |
| Reportes | 4 | 30+ | 13% |
| Operaciones especiales | 0 | 5 | 0% |
| Soporte | 0 | 4 | 0% |
| **TOTAL (herramientas)** | **~46** | **~100+** | **~45%** |

---

## 8. Recomendaciones de roadmap

### Sprint 1 (P0 crítico) — 1-2 semanas
1. `crear_vendor` (paralelo a `crear_cliente`)
2. `crear_cuenta` (chart of accounts setup)
3. `actualizar_*` (UPDATE sparse para Customer, Invoice, Vendor)
4. `eliminar_transaccion` (DELETE para todas las transacciones)
5. `void_transaccion` (para Payment, Invoice, etc.)
6. `enviar_factura` (POST /invoice/{id}/send)
7. `reporte_trial_balance`
8. `reporte_ar_aging` y `reporte_ap_aging`
9. `consulta_avanzada` (query SQL-like arbitraria)

### Sprint 2 (P1 importante) — 2-3 semanas
1. Master data restantes: `crear_item`, `crear_empleado`, `crear_clase`, `crear_departamento`, `crear_termino`, `crear_paymentmethod`
2. Transacciones restantes: `crear_billpayment`, `crear_estimate`, `crear_salesreceipt`, `crear_creditmemo`, `crear_purchase`, `crear_purchaseorder`
3. `crear_recurringtransaction` (alta prioridad)
4. Reportes adicionales: `reporte_cash_flow`, `reporte_customer_balance`, `reporte_vendor_balance`
5. `adjuntar_archivo` (Attachable — integración con OCR)

### Sprint 3 (P2 opcional) — 3-4 semanas
1. Batch operations (performance)
2. Webhooks (sync reactivo)
3. Multi-moneda (CompanyCurrency, ExchangeRate)
4. Budget
5. CDC (Change Data Capture)
6. CompanyInfo, Preferences

### Quick wins (1-2 días cada uno)
- `leer_companyinfo` (5 min de implementación)
- `leer_preferences` (5 min)
- `reporte_cash_flow` (10 min, paralelo a `reporte_pl`)

---

## 9. Próximos pasos para este documento

1. ✅ Documento de investigación exhaustiva (este archivo)
2. ⏭️ Generar `docs/qbo_api_gaps.md` con tabla priorizada y planes de implementación
3. ⏭️ Implementar al menos los gaps P0 críticos (sprint 1)
4. ⏭️ Cuando el usuario pueda autenticar NotebookLM, subir este documento como fuente del cuaderno

---

## 10. Referencias

### Documentación oficial
- [Intuit Developer Portal](https://developer.intuit.com/app/developer/qbo/docs/api/accounting)
- [API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)
- [REST API features](https://developer.intuit.com/app/developer/qbo/docs/learn/rest-api-features)
- [Query language](https://developer.intuit.com/app/developer/qbo/docs/learn/explore-the-quickbooks-online-api/data-queries)
- [Run reports](https://developer.intuit.com/app/developer/qbo/docs/workflows/run-reports)
- [Attach images](https://developer.intuit.com/app/developer/qbo/docs/workflows/attach-images-and-notes)
- [Webhooks](https://developer.intuit.com/app/developer/webhooks/docs)
- [Minor versions](https://developer.intuit.com/app/developer/qbo/docs/learn/rest-api-features#Minor-versions)

### Guías de terceros (2026)
- [Satva Solutions — QBO API Guide 2026](https://satvasolutions.com/blog/quickbooks-online-api-guide)
- [Knit — QBO API Integration Guide 2026](https://getknit.dev/blog/quickbooks-online-api-integration-guide-in-depth)
- [Zuplo — QuickBooks API](https://zuplo.com/learning-center/quickbooks-api)

### SDKs oficiales
- [QuickBooks-V3-PHP-SDK](https://github.com/intuit/QuickBooks-V3-PHP-SDK)
- [QuickBooks-V3-DotNET-SDK](https://github.com/intuit/QuickBooks-V3-DotNET-SDK)
- [QuickBooks-V3-Java-SDK](https://static.developer.intuit.com/sdkdocs/qbv3doc/ipp-v3-java-devkit-javadoc)
- [node-quickbooks (community)](https://github.com/mcohen01/node-quickbooks)

### Referencias de XSD (todos los enums)
- [Finance.xsd (PHP SDK)](https://github.com/intuit/QuickBooks-V3-PHP-SDK/blob/master/src/XSD/Finance.xsd)
- [Finance.xsd (.NET SDK)](https://github.com/intuit/QuickBooks-V3-DotNET-SDK/blob/master/IPPDotNetDevKitCSV3/Tools/XsdExtension/Intuit.Ipp.XsdExtension/Schema/Finance.xsd)
