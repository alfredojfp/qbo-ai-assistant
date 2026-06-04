# QuickBooks Online API — Gaps en Dexter y Plan de Implementación

> **Documento derivado de**: [`qbo_api_research.md`](qbo_api_research.md)
>
> **Objetivo**: Listar priorizadamente TODAS las capacidades de la QBO API que
> Dexter aún NO expone, con plan de implementación concreto para cada gap.
>
> **Estado**: Dexter tiene 46 tools en 14 módulos. La QBO API expone ~100+
> capacidades únicas (create/read/update/delete/query por cada entidad +
> reportes + operaciones especiales). **Cobertura actual: ~45%**.

---

## Resumen ejecutivo

| Prioridad | # gaps | Bloquean | Esfuerzo total |
|---|---|---|---|
| **P0** (crítico) | 16 | Flujos de firma contable y mantenibilidad | 1-2 semanas |
| **P1** (importante) | 17 | Cobertura razonable | 2-3 semanas |
| **P2** (nice-to-have) | 10 | Features avanzadas | 3-4 semanas |

---

## P0 — CRÍTICO (sprint 1, 1-2 semanas)

### Bloqueantes: sin estos, no se puede hacer mantenimiento ni workflow A/P

#### 1. `crear_vendor` (Vendor)

- **Por qué**: sin vendor no se pueden crear bills. Es la mitad del workflow contable.
- **Entidad**: `Vendor` (línea 96-118 de research)
- **API**: `POST /v3/company/{realmId}/vendor`
- **Esfuerzo**: 1 día
- **Patrón**: idéntico a `crear_cliente` (TDD, schema, helper en main.py, wrapper, registro)
- **Campos clave**:
  - `DisplayName` (requerido) — nombre visible
  - `CompanyName` (opcional) — razón social
  - `PrimaryAddr` (opcional) — dirección
  - `PrimaryPhone`, `PrimaryEmailAddr` (opcional)
  - `Vendor1099` (boolean) — si es contractor 1099
  - `BillRate` (opcional) — tarifa por hora
  - `TermRef` (opcional) — plazo de pago
  - `Active` (default true)

#### 2. `crear_cuenta` (Account)

- **Por qué**: setup inicial del chart of accounts via API. Hoy solo se puede hacer manualmente.
- **Entidad**: `Account` (línea 100-122 de research)
- **API**: `POST /v3/company/{realmId}/account`
- **Esfuerzo**: 1 día
- **Campos clave**:
  - `Name` (requerido) — nombre de la cuenta
  - `AccountType` (requerido) — enum: Bank, AccountsReceivable, OtherCurrentAsset, FixedAsset, OtherAsset, AccountsPayable, CreditCard, OtherCurrentLiability, LongTermLiability, Equity, Income, CostOfGoodsSold, Expense, OtherIncome, OtherExpense
  - `AccountSubType` (opcional) — más específico
  - `Description` (opcional)
  - `Active` (default true)
  - `OpeningBalance` + `OpeningBalanceDate` (opcional, solo al crear)

#### 3. `actualizar_*` (UPDATE sparse) — genérico

- **Por qué**: corregir errores, cambiar términos, actualizar info de clientes.
- **Patrón**: usar `?operation=sparseUpdate` o sin query param para full update
- **Esfuerzo**: 1-2 días (implementar un genérico + 3 específicos críticos)
- **Tools a crear**:
  - `actualizar_cliente` (Customer)
  - `actualizar_factura` (Invoice — para cambiar DueDate, Memo, etc.)
  - `actualizar_bill` (Bill)
- **Detalles técnicos**:
  - Siempre enviar `Id` + `SyncToken` (optimistic locking)
  - Si SyncToken no coincide, error 409 → re-leer entidad y reintentar
  - Sparse: enviar solo los campos a cambiar (más eficiente)

#### 4. `eliminar_transaccion` (DELETE)

- **Por qué**: corregir errores. Hoy no se puede borrar nada.
- **Patrón**: `POST /v3/company/{realmId}/{entity}?operation=delete`
- **Esfuerzo**: 0.5 día (1 tool genérico + dispatch por entity)
- **Tool a crear**:
  - `eliminar_transaccion(tipo, id)` — para Invoice, Bill, Payment, etc.
- **Para las 12 entidades que soportan simplified delete** (Bill, BillPayment, CreditMemo, Estimate, Invoice, JournalEntry, Payment, Purchase, PurchaseOrder, RefundReceipt, SalesReceipt, TimeActivity, VendorCredit):
  - Body: solo `Id` + `SyncToken`

#### 5. `void_transaccion` (VOID)

- **Por qué**: anular una transacción sin eliminarla del histórico.
- **Aplica a**: Payment, BillPayment, Invoice, SalesReceipt
- **Patrón**: en QBO, voided se hace con `POST /v3/company/{realmId}/{entity}?include=void` + body con `sparse=true` y agregar `"void": true` o `PrivateNote="[VOID]"`. **Verificar mecánica exacta**.
- **Esfuerzo**: 0.5 día
- **Tool a crear**:
  - `anular_transaccion(tipo, id, motivo)` — void (no delete)

#### 6. `desactivar_cliente` y `desactivar_vendor` (DELETE soft para master data)

- **Por qué**: cerrar un cliente/vendor sin perder histórico. Soft delete via `Active=false`.
- **API**: `POST /v3/company/{realmId}/{entity}?operation=delete` con body `{Id, SyncToken, Active: false}`
- **Esfuerzo**: 0.5 día
- **Tools a crear**:
  - `desactivar_cliente(cliente_id)`
  - `desactivar_vendor(vendor_id)`

#### 7. `enviar_factura` (Send Invoice)

- **Por qué**: enviar invoices por email directamente desde Dexter.
- **API**: `POST /v3/company/{realmId}/invoice/{id}/send?sendTo=email@example.com`
- **Esfuerzo**: 0.5 día
- **Tool a crear**:
  - `enviar_factura(invoice_id, email_destino?)` — si no se pasa, usa el del cliente

#### 8. `enviar_orden_compra` (Send Purchase Order)

- **API**: `POST /v3/company/{realmId}/purchaseorder/{id}/send?sendTo=...`
- **Esfuerzo**: 0.25 día
- **Tool a crear**:
  - `enviar_orden_compra(po_id, email_destino?)`

#### 9. `reporte_trial_balance` (Trial Balance)

- **Por qué**: usuario lo pide y falla en `detect_report_type`.
- **API**: `GET /v3/company/{realmId}/reports/TrialBalance?start_date=...&end_date=...&accounting_method=Accrual`
- **Esfuerzo**: 0.5 día
- **Tool a crear**:
  - `reporte_trial_balance(fecha_inicio, fecha_fin, metodo='Accrual')`

#### 10. `reporte_ar_aging` (AgedReceivables)

- **Por qué**: **CRÍTICO para firma contable** — reporte de cobranzas.
- **API**: `GET /v3/company/{realmId}/reports/AgedReceivables?report_date=...&aging_method=ReportDate&aging_period=4`
- **Esfuerzo**: 0.5 día
- **Tool a crear**:
  - `reporte_ar_aging(fecha_corte, num_periodos=4)`

#### 11. `reporte_ap_aging` (AgedPayables)

- **Por qué**: **CRÍTICO para firma contable** — reporte de pagos pendientes.
- **API**: `GET /v3/company/{realmId}/reports/AgedPayables?report_date=...&aging_method=DueDate&aging_period=4`
- **Esfuerzo**: 0.5 día
- **Tool a crear**:
  - `reporte_ap_aging(fecha_corte, num_periodos=4)`

#### 12. `reporte_general_ledger` (GeneralLedger)

- **Por qué**: auditoría, revisión detallada de una cuenta.
- **API**: `GET /v3/company/{realmId}/reports/GeneralLedger?start_date=...&end_date=...&accounting_method=Accrual&account=...`
- **Esfuerzo**: 0.5 día
- **Tool a crear**:
  - `reporte_general_ledger(fecha_inicio, fecha_fin, cuenta_id?)`

#### 13. `consulta_avanzada` (Custom Query)

- **Por qué**: el LLM necesita hacer queries SQL-like arbitrarias. Hoy solo hay `buscar_*` hardcoded.
- **API**: `POST /v3/company/{realmId}/query` con body = query SQL-like
- **Esfuerzo**: 1 día
- **Tool a crear**:
  - `consulta_avanzada(query, start_position=1, max_results=100)` — acepta SELECT statements
- **Validaciones de seguridad**:
  - Whitelist de entidades permitidas (no `SELECT` sobre tablas internas)
  - Whitelist de operadores (no `DROP`, no `DELETE`, no `UPDATE` en query)
  - Limitar MAXRESULTS a 1000
  - Confirmar acción si query es > 500 chars

#### 14. `leer_companyinfo` (CompanyInfo)

- **Por qué**: el LLM debe saber datos de la empresa (nombre legal, dirección fiscal, año fiscal, etc.)
- **API**: `GET /v3/company/{realmId}/companyinfo/{realmId}`
- **Esfuerzo**: 0.25 día
- **Tool a crear**:
  - `leer_companyinfo()` — retorna CompanyInfo completa
- **Optimización**: cachear el resultado (no cambia)

#### 15. `leer_preferences` (Preferences)

- **Por qué**: conocer la configuración de la empresa (accrual/cash, fiscal year, etc.)
- **API**: `GET /v3/company/{realmId}/preferences`
- **Esfuerzo**: 0.25 día
- **Tool a crear**:
  - `leer_preferencias()` — retorna config completa

#### 16. Pinear `minorversion` en qbo_request()

- **Por qué**: actualmente no se pinea, lo que significa que Intuit elige la versión default (vieja). Esto puede causar que campos nuevos no estén disponibles.
- **Esfuerzo**: 0.25 día
- **Cambio**: agregar `?minorversion=70` (o configurable via `.env`) a todas las llamadas en `qbo_request()`

---

## P1 — IMPORTANTE (sprint 2, 2-3 semanas)

### Master data restante

#### 17. `crear_item` (Item)

- **Por qué**: necesario para invoices con productos/servicios, no solo "AccountBasedExpenseLineDetail".
- **Esfuerzo**: 1 día
- **Campos clave**: `Name`, `Type` (Inventory/Service/NonInventory), `UnitPrice`, `IncomeAccountRef`, `AssetAccountRef` (para inventory), `TrackQuantityOnHand`, `QtyOnHand`, `InvStartDate`

#### 18. `crear_empleado` (Employee)

- **Por qué**: para nóminas, time tracking, gastos reembolsables.
- **Esfuerzo**: 0.5 día
- **Campos clave**: `DisplayName`, `GivenName`, `FamilyName`, `PrimaryAddr`, `PrimaryPhone`, `PrimaryEmailAddr`, `HiredDate`, `ReleasedDate`, `BillRate`

#### 19. `crear_clase` (Class)

- **Por qué**: segmentación P&L. Común en empresas multi-departamento.
- **Esfuerzo**: 0.25 día
- **Campos**: `Name`, `SubClass` (parent class), `Active`

#### 20. `crear_departamento` (Department)

- **Esfuerzo**: 0.25 día
- **Campos**: `Name`, `SubDepartment`, `Active`

#### 21. `crear_termino` (Term)

- **Esfuerzo**: 0.25 día
- **Campos**: `Name`, `DueDays`, `DiscountDays`, `DiscountPct`, `Active`

#### 22. `crear_paymentmethod` (PaymentMethod)

- **Esfuerzo**: 0.25 día
- **Campos**: `Name`, `Type` (CreditCard/Check/Cash/Other), `Active`

### Transacciones restantes

#### 23. `crear_billpayment` (BillPayment)

- **Por qué**: pagar bills programáticamente.
- **Esfuerzo**: 1 día
- **Campos clave**: `VendorRef`, `TotalAmt`, `PayType` (Check/CreditCard/Cash), `Line` (asociar a bills específicas), `CheckPayment` o `CreditCardPayment`

#### 24. `crear_estimate` (Estimate)

- **Esfuerzo**: 1 día (similar a Invoice pero más simple)
- **Campos**: `CustomerRef`, `Line` (items), `ExpirationDate`, `TotalAmt`

#### 25. `crear_salesreceipt` (SalesReceipt)

- **Esfuerzo**: 1 día
- **Campos**: `CustomerRef` (puede ser null), `Line`, `PaymentRef` (cómo se pagó), `DepositToAccountRef`

#### 26. `crear_creditmemo` (CreditMemo)

- **Esfuerzo**: 1 día
- **Campos**: `CustomerRef`, `Line`, `TotalAmt`, `RemainingCredit` (calculado)

#### 27. `crear_purchaseorder` (PurchaseOrder)

- **Esfuerzo**: 1 día
- **Campos**: `VendorRef`, `Line` (items), `TotalAmt`, `POEmail`, `ShipToAddr`, `VendorAddr`

#### 28. `crear_refundreceipt` (RefundReceipt)

- **Esfuerzo**: 1 día
- **Campos**: `CustomerRef`, `Line`, `TotalAmt`, `RefundReceiptPayment` (cómo se reembolsa)

#### 29. `crear_purchase` (Purchase genérica)

- **Esfuerzo**: 1 día
- **Campos**: `VendorRef`, `AccountRef` (para AccountBasedExpense), `Line`, `PaymentType`, `TotalAmt`

#### 30. `crear_vendorcredit` (VendorCredit)

- **Esfuerzo**: 1 día
- **Campos**: `VendorRef`, `Line`, `TotalAmt`

#### 31. `crear_timeactivity` (TimeActivity)

- **Esfuerzo**: 0.5 día
- **Campos**: `EmployeeRef`, `CustomerRef`, `ItemRef`, `BillableStatus`, `Hours`, `Minutes`, `TxnDate`, `Description`

### Features avanzadas

#### 32. `crear_recurringtransaction` (RecurringTransaction)

- **Por qué**: **CRÍTICO** — automatizar invoices mensuales, alquileres, suscripciones.
- **Esfuerzo**: 2 días
- **Entidades soportadas como base**: Invoice, Bill, JournalEntry, SalesReceipt, etc.
- **Campos clave en RecurringInfo**: `Name`, `RecurType` (Automated/Reminder), `Active`, `ScheduleInfo` (StartDate, IntervalType, NumInterval, MaxOccurrences, etc.)
- **API**: `POST /v3/company/{realmId}/recurringtransaction`
- **Validación**: `RecurType=Automated` requiere `ScheduleInfo` completo; `Reminder` no requiere schedule
- **Edge cases**:
  - Si se crea a partir de un invoice existente, heredar `Line`, `CustomerRef`, `DueDate`
  - Soportar "NextDate" para programar la primera ocurrencia

#### 33. `adjuntar_archivo` (Attachable)

- **Por qué**: vincular PDF/imagen a bill, invoice, etc. Integración con `Pending bills/`.
- **Esfuerzo**: 1.5 días (multipart, base64)
- **API**: `POST /v3/company/{realmId}/upload` con multipart
- **Campos**: file (base64), metadata (Attachable con AttachableRef)
- **Workflow completo**:
  1. Usuario procesa PDFs en `Pending bills/` con OCR
  2. OCR extrae datos y crea bill
  3. `adjuntar_archivo()` vincula el PDF original al bill creado
  4. QBO muestra el PDF en la UI del bill

### Reportes adicionales

#### 34. `reporte_cash_flow` (CashFlow)
- **Esfuerzo**: 0.5 día

#### 35. `reporte_customer_balance` (CustomerBalance)
- **Esfuerzo**: 0.5 día

#### 36. `reporte_vendor_balance` (VendorBalance)
- **Esfuerzo**: 0.5 día

#### 37. `reporte_profit_loss_detail` (ProfitAndLossDetail)
- **Esfuerzo**: 0.5 día

#### 38. `reporte_journal` (JournalReport)
- **Esfuerzo**: 0.5 día

#### 39. `reporte_account_list` (AccountList)
- **Esfuerzo**: 0.5 día

---

## P2 — NICE-TO-HAVE (sprint 3, 3-4 semanas)

### Configuración de empresa

#### 40. `crear_taxcode` y `crear_taxrate` (TaxCode / TaxRate)
- **Esfuerzo**: 1 día
- **Por qué**: configurar impuestos automáticamente.

#### 41. `crear_companycurrency` (CompanyCurrency)
- **Esfuerzo**: 1 día
- **Por qué**: multi-moneda.

#### 42. `leer_exchange_rate` (ExchangeRate)
- **Esfuerzo**: 0.25 día
- **API**: `POST /v3/company/{realmId}/exchangerate` o vía query
- **Campos**: `SourceCurrencyCode`, `TargetCurrencyCode`, `AsOfDate`

#### 43. `crear_budget` (Budget)
- **Esfuerzo**: 2 días
- **Estructura jerárquica** (BudgetDetail por mes y cuenta)

### Operaciones avanzadas

#### 44. `ejecutar_batch` (Batch operations)
- **Por qué**: performance, rate limits, atomicidad lógica.
- **Esfuerzo**: 2 días
- **API**: `POST /v3/company/{realmId}/batch`
- **Patrón**: agrupar 30 operaciones del CSV batch en una sola request
- **Manejo**: una operación que falla no aborta el batch, pero se reporta
- **Beneficios**:
  - 10x más rápido que secuencial (30 ops en 1 request vs 30 requests)
  - 1/30 del rate limit
  - Mejor UX: el usuario ve "30/30" en lugar de esperar 30 segundos

#### 45. `cdc_query` (Change Data Capture)
- **Por qué**: sync incremental en lugar de polling.
- **Esfuerzo**: 1.5 días
- **API**: `POST /v3/company/{realmId}/cdc` con `entities`, `since`
- **Retorna**: lista de entidades modificadas con timestamp

#### 46. `webhook_setup` (Webhooks)
- **Por qué**: notificaciones push reactivas.
- **Esfuerzo**: 3 días
- **Requiere**:
  - Endpoint HTTPS público (no factible en local)
  - Verificación HMAC-SHA256
  - Manejo de reintentos
- **Alternativa**: usar ngrok o similar para desarrollo

#### 47. `actualizar_preferences` (Preferences)
- **Esfuerzo**: 1 día
- **Uso**: cambiar fiscal year, accounting method, etc.

#### 48. `actualizar_companyinfo` (CompanyInfo)
- **Esfuerzo**: 1 día
- **Uso**: actualizar dirección fiscal, razón social, etc.

### Reportes opcionales

#### 49. `reporte_inventory_valuation` (InventoryValuationSummary)
- **Esfuerzo**: 0.5 día

#### 50. `reporte_sales_by_customer` (CustomerSales)
- **Esfuerzo**: 0.5 día

#### 51. `reporte_expenses_by_vendor` (VendorExpenses)
- **Esfuerzo**: 0.5 día

#### 52. `reporte_transaction_list` (TransactionList)
- **Esfuerzo**: 0.5 día

#### 53. `reporte_class_sales` y `reporte_department_sales`
- **Esfuerzo**: 0.5 día c/u

---

## Plan de implementación sugerido

### Sprint 1 (P0) — 1-2 semanas
1. **Día 1-2**: `crear_vendor` (paralelo a `crear_cliente`, ambos con TDD)
2. **Día 3**: `crear_cuenta` (TDD)
3. **Día 4-5**: `actualizar_cliente`, `actualizar_factura`, `actualizar_bill` (UPDATE sparse)
4. **Día 6**: `eliminar_transaccion` (genérico) + `void_transaccion`
5. **Día 7**: `desactivar_cliente`, `desactivar_vendor` (soft delete)
6. **Día 8**: `enviar_factura`, `enviar_orden_compra`
7. **Día 9**: `reporte_trial_balance`, `reporte_ar_aging`, `reporte_ap_aging`
8. **Día 10**: `reporte_general_ledger`, `leer_companyinfo`, `leer_preferencias`
9. **Día 11**: `consulta_avanzada` (con validaciones de seguridad)
10. **Día 12**: pinear `minorversion=70` en `qbo_request()`

**Resultado sprint 1**: 16 nuevos tools → 62 tools totales. Cobertura ~62%.

### Sprint 2 (P1) — 2-3 semanas
- Master data: 6 tools (item, empleado, clase, departamento, termino, paymentmethod)
- Transacciones: 9 tools (billpayment, estimate, salesreceipt, creditmemo, purchase, purchaseorder, refundreceipt, vendorcredit, timeactivity)
- RecurringTransaction: 1 tool complejo
- Attachable: 1 tool (multipart)
- Reportes: 6 tools

**Resultado sprint 2**: +22 tools → 84 tools totales. Cobertura ~84%.

### Sprint 3 (P2) — 3-4 semanas
- Config: 4 tools (taxcode, taxrate, companycurrency, exchangerate)
- Batch: 1 tool
- CDC: 1 tool
- Webhooks: 1 tool
- Reports adicionales: 6 tools
- Budget: 1 tool

**Resultado sprint 3**: +14 tools → 98 tools totales. Cobertura ~98%.

### Maintenance (continuo)
- Tests: cada tool nuevo debe venir con TDD
- Documentación: actualizar CAPACIDADES.md, CHANGELOG.md, dexter/tools/README.md
- Cache: agregar caching donde aplique (CompanyInfo, Preferences)
- Rate limit handling: exponential backoff con jitter
- Webhooks: requiere deploy de endpoint público (no factible sin hosting)

---

## Métricas de éxito

- **Cobertura API**: 45% → 98% (sprint 3)
- **Tools totales**: 46 → 98
- **Tests**: 311 → 500+ (target)
- **Tiempo para setup de empresa nueva**: 30 min (manual en QBO) → 2 min (vía API)
- **Workflow A/P completo**: 0% (no se puede) → 100% (crear vendor + bill + billpayment)
- **Workflow A/R completo**: 50% (invoice + payment) → 100% (invoice + send + payment + creditmemo)
- **Reportes para firma contable**: 13% → 100% (P&L, BS, TB, GL, AR Aging, AP Aging, etc.)

---

## Próximos pasos inmediatos

1. ✅ Este documento (`qbo_api_gaps.md`)
2. ⏭️ Revisar con el usuario qué P0 priorizar
3. ⏭️ Implementar el sprint 1 siguiendo TDD
4. ⏭️ Cuando el usuario pueda autenticar NotebookLM, subir `qbo_api_research.md` como fuente del cuaderno
5. ⏭️ Iterar: cada sprint agrega 10-20 tools, mantener docs sincronizadas
