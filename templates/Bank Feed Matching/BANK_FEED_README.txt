# 📋 BANK FEED CSV - FORMATO Y DOCUMENTACIÓN

## 📥 Archivos Disponibles

1. **bank_feed_template.csv** - Template simple con ejemplos básicos
2. **bank_feed_ejemplo_completo.csv** - Ejemplos completos con todos los escenarios

---

## 📊 FORMATO DEL CSV

### Columnas Requeridas (8 columnas)

| Columna | Descripción | Formato | Ejemplo |
|---------|-------------|---------|---------|
| **bank_feed_date** | Fecha del depósito en el banco | YYYY-MM-DD | 2026-01-15 |
| **bank_feed_amount** | Monto NETO depositado | Decimal | 218.75 |
| **deposit_id** | ID único del depósito | Texto único | STRIPE-001 |
| **line_type** | Tipo de línea | income o fee | income |
| **customer_name** | Nombre del cliente | Texto | John Doe |
| **amount** | Monto de esta línea | Decimal (+/-) | 250.00 o -31.25 |
| **account** | Cuenta contable | Texto | Design Income |
| **memo** | Descripción | Texto | Payment for services |

---

## 🔑 REGLAS IMPORTANTES

### 1. Agrupación por deposit_id
- Todas las líneas con el **mismo deposit_id** se combinan en UN solo depósito
- `bank_feed_date` y `bank_feed_amount` deben ser **iguales** para mismo deposit_id

### 2. Validación de Sumas
```
La suma de todos los 'amount' DEBE igualar 'bank_feed_amount'
Tolerancia: 1 centavo

Ejemplo:
  bank_feed_amount = 218.75
  Líneas:
    + 250.00 (income)
    -  31.25 (fee)
    --------
    = 218.75 ✅
```

### 3. Line Types
- **`income`** = Ingreso (monto **positivo**)
- **`fee`** = Comisión/Fee (monto **negativo**)

### 4. Customer Name
- Debe existir en QuickBooks
- El sistema buscará automáticamente por fuzzy matching
- Puede estar **vacío** si no aplica a un cliente específico

### 5. Account
- Nombre de la cuenta contable en QuickBooks
- El sistema buscará por fuzzy matching
- Ejemplos: `"Design Income"`, `"Stripe Fees"`, `"Consulting Income"`

---

## 💡 EJEMPLOS PRÁCTICOS

### Ejemplo 1: Pago Simple con Fee (Stripe)

```csv
bank_feed_date,bank_feed_amount,deposit_id,line_type,customer_name,amount,account,memo
2026-01-15,218.75,STRIPE-001,income,John Doe,250.00,Design Income,Payment for logo
2026-01-15,218.75,STRIPE-001,fee,John Doe,-31.25,Stripe Fees,Stripe fee 12.5%
```

**Resultado en QuickBooks:**
- Depósito a Checking Account por **$218.75**
- Línea 1: +$250.00 → Design Income (cliente: John Doe)
- Línea 2: -$31.25 → Stripe Fees (cliente: John Doe)

---

### Ejemplo 2: Multiple Clientes Mismo Día

```csv
bank_feed_date,bank_feed_amount,deposit_id,line_type,customer_name,amount,account,memo
2026-01-16,1140.50,BATCH-002,income,Tech LLC,800.00,Development Services,Website dev
2026-01-16,1140.50,BATCH-002,fee,Tech LLC,-40.00,Stripe Fees,Stripe fee
2026-01-16,1140.50,BATCH-002,income,Marketing Co,400.00,Design Income,Brand package
2026-01-16,1140.50,BATCH-002,fee,Marketing Co,-19.50,Stripe Fees,Stripe fee
```

**Resultado:**
- UN depósito por **$1,140.50**
- 4 líneas (2 clientes, cada uno con su fee)

---

### Ejemplo 3: Transferencia Sin Fee (ACH/Wire)

```csv
bank_feed_date,bank_feed_amount,deposit_id,line_type,customer_name,amount,account,memo
2026-01-17,1500.00,ACH-003,income,Enterprise Inc,1500.00,Consulting Income,Retainer payment
```

**Resultado:**
- Depósito por **$1,500.00**
- Sin fees (monto completo)

---

### Ejemplo 4: International con Múltiples Fees

```csv
bank_feed_date,bank_feed_amount,deposit_id,line_type,customer_name,amount,account,memo
2026-01-18,1175.50,INTL-004,income,Global Client,1250.00,Consulting Income,International project
2026-01-18,1175.50,INTL-004,fee,Global Client,-62.50,Stripe Fees,Stripe int fee
2026-01-18,1175.50,INTL-004,fee,Global Client,-12.00,FX Fees,Currency conversion
```

---

## 🎯 ESCENARIOS COMUNES

### Stripe Payments (5% fee típico)
```csv
...,income,Client Name,100.00,Service Income,Payment
...,fee,Client Name,-5.00,Stripe Fees,5% fee
```

### PayPal (5.5% fee típico)
```csv
...,income,Client Name,100.00,Service Income,Payment
...,fee,Client Name,-5.50,PayPal Fees,5.5% fee
```

### Square/POS (2.6% + $0.10)
```csv
...,income,Customer,100.00,Product Sales,Purchase
...,fee,Customer,-2.70,Merchant Fees,Square fee
```

### Subscriptions (múltiples en un día)
```csv
...,income,Subscriber A,99.00,Subscription Income,Monthly
...,fee,Subscriber A,-4.95,Stripe Fees,Fee
...,income,Subscriber B,99.00,Subscription Income,Monthly
...,fee,Subscriber B,-4.95,Stripe Fees,Fee
```

---

## ⚠️ ERRORES COMUNES

### ❌ Suma no cuadra
```
Error: Suma no cuadra - diferencia de $0.05
```
**Solución:** Verifica que la suma de amounts = bank_feed_amount

### ❌ Cliente no encontrado
```
Error: Cliente 'Jhon Doe' no encontrado
```
**Solución:** 
- Verifica ortografía (John vs Jhon)
- Crea el cliente en QuickBooks primero
- El sistema usa fuzzy matching (70% similitud)

### ❌ Cuenta no encontrada
```
Error: Cuenta no encontrada: Desing Income
```
**Solución:**
- Verifica ortografía (Design vs Desing)
- Usa el nombre exacto de QuickBooks
- Revisa Chart of Accounts

---

## 🔧 CUENTAS SUGERIDAS

### Para Ingresos
```
- Design Income
- Consulting Income
- Development Services
- Subscription Income
- Product Sales
- Freelance Income
- Service Revenue
```

### Para Fees
```
- Stripe Fees
- PayPal Fees
- Merchant Fees
- Payment Processing Fees
- Currency Conversion Fees
- Transaction Fees
```

**NOTA:** Crea estas cuentas en QuickBooks antes de procesar el CSV

---

## 🚀 CÓMO USAR

### 1. Preparar el CSV
```bash
# Descarga el template
bank_feed_template.csv

# Edita con tus datos
# Verifica: clientes, cuentas, sumas
```

### 2. Procesar con el Asistente
```
👤 Tú: "Procesa el archivo bank_feed_enero.csv"

🤖 Asistente: 
   📁 Procesando Bank Feed CSV...
   ✅ 10 depósitos encontrados
   🔄 Procesando STRIPE-001...
   ✓ Suma validada: $218.75
   ✅ Depósito creado (ID: 12345)
   ...
```

### 3. Verificar en QuickBooks
- Ve a Banking → Checking Account
- Verifica los depósitos nuevos
- Revisa que los splits sean correctos

---

## 📞 SOPORTE

### Si tienes problemas:

1. **Verifica el formato del CSV** (8 columnas, headers correctos)
2. **Valida las sumas** manualmente
3. **Confirma clientes** existen en QuickBooks
4. **Revisa nombres de cuentas** en Chart of Accounts
5. **Prueba con depósito simple** primero (1 income + 1 fee)

---

## 📝 TIPS PRO

### Naming Convention para deposit_id
```
STRIPE-YYYYMMDD-001    → Stripe payment
PAYPAL-YYYYMMDD-001    → PayPal
ACH-YYYYMMDD-001       → ACH transfer
WIRE-YYYYMMDD-001      → Wire transfer
SUB-YYYYMM             → Subscriptions batch
BATCH-YYYYMMDD         → Multiple clients
```

### Trackear Fees por Cliente
Asignar fees a clientes permite:
- Ver rentabilidad real por cliente
- Reportes de fees pagados
- Análisis de costo de adquisición

### Batch Processing
Agrupa depósitos del mismo día con mismo deposit_id para:
- Reducir cantidad de depósitos
- Coincidir con bank statement
- Simplificar reconciliación

---

## ✅ CHECKLIST PRE-PROCESAMIENTO

- [ ] CSV tiene exactamente 8 columnas
- [ ] Headers están correctos (sin espacios extra)
- [ ] Fechas en formato YYYY-MM-DD
- [ ] Sumas validadas por deposit_id
- [ ] Clientes existen en QuickBooks
- [ ] Cuentas existen en Chart of Accounts
- [ ] Fees son negativos, income positivo
- [ ] deposit_id únicos y descriptivos

---

**Versión:** 1.0  
**Última actualización:** Enero 2026  
**Desarrollado por:** Alfredo
