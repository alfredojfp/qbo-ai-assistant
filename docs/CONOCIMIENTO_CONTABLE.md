# Base de Conocimiento Contable — Dexter QBO Agent

> **Propósito:** Referencia rápida inyectable en el system prompt de Dexter. Cubre los conceptos contables esenciales, las relaciones entre entidades de QBO, y la sintaxis de queries. Dexter DEBE consultar este conocimiento antes de responder a preguntas contables o ejecutar operaciones en QBO.

---

## 1. CONCEPTOS CONTABLES ESENCIALES

### 1.1. Signos contables
- **Positivo (+):** Ingreso, venta, cobro recibido, depósito, crédito a income.
- **Negativo (-):** Gasto, compra, pago realizado, débito a expense.
- **Débito vs Crédito:**
  - **Débito** (izquierda): Aumenta activos y gastos, disminuye pasivos e ingresos.
  - **Crédito** (derecha): Aumenta pasivos e ingresos, disminuye activos y gastos.

### 1.2. Cuentas contables — las 5 categorías
| Tipo | Ejemplos | Signo normal |
|------|----------|-------------|
| **ACTIVO** (Asset) | Caja, Bancos, Clientes (AR), Inventario, Equipo | Débito (+) |
| **PASIVO** (Liability) | Cuentas por Pagar (AP), Préstamos, Impuestos por Pagar | Crédito (-) |
| **PATRIMONIO** (Equity) | Capital, Ganancias Retenidas | Crédito (-) |
| **INGRESO** (Income/Revenue) | Ventas, Servicios Prestados, Ingresos Financieros | Crédito (-) |
| **GASTO** (Expense) | Salarios, Renta, Servicios, Depreciación | Débito (+) |

### 1.3. Ecuación contable fundamental
```
ACTIVO = PASIVO + PATRIMONIO
```

### 1.4. Método de partida doble
Cada transacción contable afecta al menos 2 cuentas — una con débito y otra con crédito. La suma de débitos SIEMPRE debe igualar la suma de créditos.

### 1.5. Períodos y acumulaciones
- **Fiscal Year (Año fiscal)** — puede no coincidir con año calendario. Se configura en QBO Company Settings.
- **Devengado (Accrual):** Ingresos/gastos se reconocen cuando se generan, no cuando se cobran/pagan.
- **Caja (Cash):** Ingresos/gastos se reconocen cuando se cobran/pagan. Menos común.

---

## 2. RELACIONES ENTRE ENTIDADES (QBO DATA MODEL)

### 2.1. Flujo completo: Customer → Estimate → Invoice → Payment

```
Customer (Cliente)
  ├── Estimate (Cotización/Presupuesto)
  │     └── se convierte en → Invoice (Factura)
  │           └── se paga con → Payment (Cobro/Pago recibido)
  │                 └── deposita en → Deposit (Depósito bancario)
  │
  ├── Invoice (Factura directa, sin estimate previo)
  ├── SalesReceipt (Recibo de venta — pago inmediato)
  ├── CreditMemo (Nota de crédito — devolución/reembolso)
  └── RefundReceipt (Recibo de reembolso)
```

### 2.2. Flujo: Vendor → Purchase Order → Bill → BillPayment

```
Vendor (Proveedor)
  ├── PurchaseOrder (Orden de compra)
  │     └── se convierte en → Bill (Cuenta por pagar)
  │           └── se paga con → BillPayment (Pago de factura)
  │
  ├── Bill (Cuenta por pagar directa)
  ├── VendorCredit (Crédito de proveedor — devolución)
  └── Purchase (Compra/Gasto directo)
```

### 2.3. Flujo: Bank → BankFeed → Classification → Deposit/Bill

```
Bank Account (Cuenta bancaria en QBO)
  └── BankFeed (Transacción bancaria importada)
        └── Clasificación contable
              ├── Income (positivo) → Deposit con split por cliente
              └── Expense (negativo) → Bill o Purchase
```

### 2.4. Flujo: Chart of Accounts → Journal Entry

```
Chart of Accounts (Plan de cuentas)
  └── JournalEntry (Asiento contable manual)
        ├── Debit lines (débitos)
        └── Credit lines (créditos)
        └── Suma débitos == Suma créditos (OBLIGATORIO)
```

### 2.5. Referencias entre entidades (IDs)
- `CustomerRef.value` → apunta a `Customer.Id`
- `VendorRef.value` → apunta a `Vendor.Id`
- `ItemRef.value` → apunta a `Item.Id`
- `AccountRef.value` → apunta a `Account.Id`
- `TxnTaxDetail` → apunta a `TaxCode`/`TaxRate`
- `LinkedTxn` → vincula Payment↔Invoice, BillPayment↔Bill
- `Deposit.Line.LinkedTxn` → vincula Deposit↔Payment

---

## 3. ENTIDADES QBO — CAMPOS CLAVE POR ENTIDAD

### 3.1. Customer (Cliente)
| Campo | Tipo | Descripción |
|-------|------|------------|
| `Id` | string | ID único en QBO |
| `DisplayName` | string | Nombre para mostrar |
| `GivenName`, `FamilyName` | string | Nombre, Apellido |
| `CompanyName` | string | Razón social |
| `Balance` | decimal | Saldo pendiente (AR) |
| `Active` | bool | ¿Está activo? |
| `PrimaryEmailAddr.Address` | string | Email principal |

### 3.2. Invoice (Factura)
| Campo | Tipo | Descripción |
|-------|------|------------|
| `Id` | string | ID único |
| `DocNumber` | string | Número de factura |
| `TxnDate` | date | Fecha de transacción |
| `DueDate` | date | Fecha de vencimiento |
| `CustomerRef.value` | string | ID del cliente |
| `Line` | array | Líneas de la factura |
| `TotalAmt` | decimal | Total |
| `Balance` | decimal | Saldo pendiente |
| `EmailStatus` | string | `NotSent`, `NeedToSend`, `EmailSent` |

### 3.3. Estimate (Cotización)
| Campo | Tipo | Descripción |
|-------|------|------------|
| `Id` | string | ID único |
| `DocNumber` | string | Número de estimación |
| `TxnDate` | date | Fecha |
| `ExpirationDate` | date | Fecha de expiración |
| `CustomerRef.value` | string | ID del cliente |
| `Line` | array | Líneas |
| `TotalAmt` | decimal | Total estimado |
| `TxnStatus` | string | Estado (`Accepted`, `Closed`, `Pending`, `Rejected`) |

### 3.4. Bill (Cuenta por pagar)
| Campo | Tipo | Descripción |
|-------|------|------------|
| `Id` | string | ID único |
| `DocNumber` | string | Número |
| `TxnDate` | date | Fecha |
| `DueDate` | date | Vencimiento |
| `VendorRef.value` | string | ID del proveedor |
| `Line` | array | Líneas |
| `TotalAmt` | decimal | Total |
| `Balance` | decimal | Saldo pendiente (AP) |

### 3.5. Payment (Cobro recibido)
| Campo | Tipo | Descripción |
|-------|------|------------|
| `Id` | string | ID único |
| `TxnDate` | date | Fecha |
| `CustomerRef.value` | string | ID del cliente |
| `TotalAmt` | decimal | Monto recibido |
| `UnappliedAmt` | decimal | Monto no aplicado |
| `Line` | array | Invoices que se están pagando |

### 3.6. Account (Cuenta contable)
| Campo | Tipo | Descripción |
|-------|------|------------|
| `Id` | string | ID único |
| `Name` | string | Nombre de la cuenta |
| `AcctNum` | string | Número de cuenta (opcional) |
| `AccountType` | string | Bank, AR, AP, Income, Expense, etc. |
| `AccountSubType` | string | Subtipo |
| `Classification` | string | Asset, Liability, Equity, Revenue, Expense |
| `CurrentBalance` | decimal | Balance actual |
| `Active` | bool | Activa |

### 3.7. Deposit (Depósito bancario)
| Campo | Tipo | Descripción |
|-------|------|------------|
| `Id` | string | ID único |
| `TxnDate` | date | Fecha |
| `DepositToAccountRef.value` | string | Cuenta bancaria destino |
| `TotalAmt` | decimal | Total depositado |
| `Line` | array | Líneas del depósito (referencias a payments) |

### 3.8. JournalEntry (Asiento contable)
| Campo | Tipo | Descripción |
|-------|------|------------|
| `Id` | string | ID único |
| `TxnDate` | date | Fecha |
| `DocNumber` | string | Número de póliza |
| `Line` | array | Débitos y créditos |
| `Line[].JournalLineDetail.PostingType` | string | `Debit` o `Credit` |
| `Line[].Amount` | decimal | Monto |
| `Line[].AccountRef.value` | string | Cuenta afectada |

---

## 4. QUERY LANGUAGE — SINTAXIS SQL-LIKE DE QBO

### 4.1. Estructura básica
```sql
SELECT [* | campo1, campo2] FROM Entidad
WHERE campo = 'valor' AND campo2 > 100
STARTPOSITION 1 MAXRESULTS 100
ORDERBY campo ASC
```

### 4.2. Entidades consultables
Todas las entidades del modelo: Account, Customer, Vendor, Item, Invoice, Bill, Payment, Estimate, BillPayment, SalesReceipt, CreditMemo, Purchase, PurchaseOrder, RefundReceipt, VendorCredit, JournalEntry, Deposit, Transfer, TaxCode, TaxRate, Class, Department, Employee, Term, PaymentMethod, TimeActivity, Budget, RecurringTransaction...

### 4.3. Operadores soportados
- **Comparación:** `=`, `<`, `>`, `<=`, `>=`, `!=`
- **Lógicos:** `AND`, `OR`, `NOT`
- **Boolean:** `WHERE Active = true` o `WHERE Active IN (true, false)`
- **Rango:** `WHERE TxnDate >= '2026-01-01' AND TxnDate <= '2026-06-30'`
- **LIKE limitado:** no soporta wildcards, usar `=` exacto

### 4.4. Ejemplos prácticos

```sql
-- Buscar cliente por nombre exacto (DisplayName usa = exacto, no LIKE)
SELECT * FROM Customer WHERE DisplayName = 'AlfredoTPM'

-- Buscar cliente por substring (usar consulta y filtrar en Python)
SELECT * FROM Customer MAXRESULTS 100

-- Estimates de un cliente específico
SELECT * FROM Estimate WHERE CustomerRef.value = '70' MAXRESULTS 10

-- Invoices pendientes de un cliente
SELECT * FROM Invoice WHERE CustomerRef.value = '70' AND Balance > '0'

-- Facturas del último mes
SELECT * FROM Invoice WHERE TxnDate >= '2026-05-01' MAXRESULTS 50

-- Bills pendientes de pago
SELECT * FROM Bill WHERE Balance > '0' MAXRESULTS 50

-- Depósitos recientes en cuenta bancaria específica
SELECT * FROM Deposit WHERE DepositToAccountRef.value = '123' AND TxnDate >= '2026-05-01'

-- Cuentas activas de tipo Bank
SELECT * FROM Account WHERE AccountType = 'Bank' AND Active = true

-- Contar clientes activos
SELECT COUNT(*) FROM Customer WHERE Active = true

-- Items activos
SELECT * FROM Item WHERE Active = true MAXRESULTS 200
```

### 4.5. Limitaciones importantes
- **MAXRESULTS máximo:** 1000
- **COUNT(*):** Retorna `totalCount` como número, no como lista de entidades.
- **LIKE/Wildcards:** NO soportados. Usar `=` exacto y filtrar en Python.
- **Paginación:** `STARTPOSITION N MAXRESULTS M` — máximo 1000 por página.
- **Subconsultas:** NO soportadas.
- **JOINs:** NO soportados. Usar múltiples queries y relacionar por IDs.
- **Dates:** Formato ISO `'YYYY-MM-DD'`.
- **IDs:** Siempre entre comillas simples.

---

## 5. WORKFLOWS CONTABLES COMUNES

### 5.1. Crear un cliente y su primera factura
```
1. buscar_cliente("nombre") para verificar si ya existe
2. Si no existe: crear_cliente(nombre, ...)
3. crear_invoice con CustomerRef = ID del cliente
4. (Opcional) send_invoice si se requiere envío por email
```

### 5.2. Crear un estimate y convertirlo a invoice
```
1. crear_estimate(cliente_id=N, monto=M, fecha=...)
2. Cuando el cliente acepta:
   a. Ejecutar POST manual a /estimate/{id}/send (si se necesita)
   b. Crear invoice manualmente (no hay conversión automática en API)
```

### 5.3. Depositar un pago recibido
```
1. crear_pago(cliente_id=N, monto=M)
2. crear_deposito(cuenta_bancaria_id=X, pagos=[payment_id])
```

### 5.4. Reconciliación bancaria (BNK-RECON — tag-only)
```
1. procesar_csv_bank_feed(archivo_csv) — clasifica transacciones
2. El motor sugiere etiquetas según patrones históricos
3. procesar_reconciliacion_bancaria(archivo_csv, cuenta_id)
4. Solo etiqueta, NO crea transacciones en QBO
```

### 5.5. Procesar facturas PDF (OCR)
```
1. Colocar PDFs en carpeta "Pending bills/"
2. procesar_lote_bills(carpeta)
3. Revisar CSV preview generado
4. Confirmar o ajustar clasificaciones
5. crear_bill para cada factura válida
```

---

## 6. ESTADOS Y CICLO DE VIDA

### 6.1. Invoice
- `Balance > 0` → Pendiente de pago
- `Balance = 0` → Pagada completamente
- `EmailStatus = 'EmailSent'` → Enviada al cliente
- `Void` action → Anulada (no se elimina, se marca como void)

### 6.2. Estimate
- `Pending` → Recién creada, esperando respuesta
- `Accepted` → Cliente aceptó — listo para convertir a invoice
- `Closed` → Cerrada (convertida a invoice o expirada)
- `Rejected` → Rechazada por el cliente

### 6.3. Bill
- `Balance > 0` → Pendiente de pago
- `Balance = 0` → Pagada completamente
- VendorCredit se aplica contra Bills reduciendo el balance.

### 6.4. Payment
- `UnappliedAmt > 0` → Parte del pago no aplicado a ninguna invoice
- `TotalAmt = suma de Line[].Amount` → Pago completamente aplicado

---

## 7. PRINCIPIOS DE CONTABILIDAD PARA EL AGENTE

1. **Nunca asumas.** Si no sabes un dato, preguntá al usuario o consultá QBO.
2. **Verificá antes de crear.** Buscá si el cliente/vendor/item ya existe.
3. **Validá sumas.** En depósitos con splits: la suma de líneas debe igualar el total.
4. **No elimines, anulá.** Para invoices, bills, payments: usar Void, no Delete.
5. **El chart of accounts es la fuente de verdad.** No inventes cuentas contables.
6. **Respetá el orden de las operaciones.** Ej: no podés depositar un pago que no existe.
7. **Los IDs son opacos.** No asumas que son secuenciales ni numéricos.
8. **Usá el query language para buscar.** `SELECT * FROM Entidad WHERE campo = 'valor'`.
9. **Manejo de errores.** Si QBO retorna error, leé el mensaje, no reintentes ciegamente.
10. **Sé transparente.** Cuando uses un tool, decí qué estás haciendo y por qué.
