# 📚 QuickBooks AI Assistant - Ejemplos de Uso

Esta guía contiene ejemplos reales y detallados de cómo usar el asistente para diferentes tareas contables.

---

## 📑 Índice

1. [Búsquedas Básicas](#1-búsquedas-básicas)
2. [Depósitos Simples](#2-depósitos-simples)
3. [Depósitos Multi-Cliente](#3-depósitos-multi-cliente)
4. [Facturas (Invoices)](#4-facturas-invoices)
5. [Cuentas por Pagar (Bills)](#5-cuentas-por-pagar-bills)
6. [Pagos Recibidos](#6-pagos-recibidos)
7. [Reportes Financieros](#7-reportes-financieros)
8. [Procesamiento CSV Batch](#8-procesamiento-csv-batch)
9. [Gestión de Reportes Guardados](#9-gestión-de-reportes-guardados)
10. [Comandos de Sistema](#10-comandos-de-sistema)

---

## 1. Búsquedas Básicas

### Buscar un Cliente

```
👤 Tú: Busca el cliente Acme Corporation

🤖 Asistente:
   🔍 Encontré estos clientes:

   1. **Acme Corporation** (ID: 45)
      • Balance: $5,230.00
      • Activo: Sí
      • Similitud: 100%
```

### Buscar con Fuzzy Matching

```
👤 Tú: Busca cuenta "prepaid"

🤖 Asistente:
   📊 Encontré estas cuentas:

   1. **Prepaid Expenses** (ID: 123)
      • Número: 1200
      • Tipo: Other Current Asset
      • Categoría: ACTIVO
      • Balance: $3,500.00
      • Similitud: 95%

   2. **Prepaid Labour** (ID: 125)
      • Número: 1205
      • Tipo: Other Current Asset
      • Categoría: ACTIVO
      • Balance: $8,200.00
      • Similitud: 87%
```

### Buscar Vendor

```
👤 Tú: Busca el proveedor Office Depot

🤖 Asistente:
   🔍 Encontré:

   **Office Depot Inc.** (ID: 78)
   • Balance pendiente: $1,245.50
   • Activo: Sí
```

---

## 2. Depósitos Simples

### Mover Anticipo a Cuenta Bancaria

```
👤 Tú: Muéveme $2500 de Client Retainers de Tech Solutions a Checking Account

🤖 Asistente:
   🔍 Buscando cliente "Tech Solutions"...
   ✅ Cliente encontrado: Tech Solutions Inc. (ID: 52)

   🔍 Buscando cuentas...
   ✅ Cuenta origen: Client Retainers (ID: 89)
   ✅ Cuenta destino: Checking Account (ID: 35)

   💰 Creando depósito...

   ✅ **Depósito creado exitosamente**
      • Cliente: Tech Solutions Inc.
      • Monto: $2,500.00
      • Desde: Client Retainers
      • Hacia: Checking Account
      • Fecha: 2026-01-20
      • ID del depósito: 12345
```

### Mover Prepago de Servicios

```
👤 Tú: Mueve $1800 de Prepaid Labour del cliente Design Co a la cuenta Checking

🤖 Asistente:
   ✅ Depósito creado:
      • Design Co: $1,800.00
      • Desde: Prepaid Labour → Checking Account
      • Fecha: 2026-01-20
```

---

## 3. Depósitos Multi-Cliente

### Varios Clientes en un Solo Depósito

```
👤 Tú: Necesito mover anticipos a checking: $2500 de Client Retainers de Acme Corp,
       $1800 de Prepaid Labour de Tech Inc, y $3200 de Client Retainers de Design Co

🤖 Asistente:
   🔍 Procesando 3 clientes...

   ✅ **Depósito multi-cliente creado**

   Detalle de líneas:
   1. Acme Corp
      • $2,500.00 desde Client Retainers

   2. Tech Inc
      • $1,800.00 desde Prepaid Labour

   3. Design Co
      • $3,200.00 desde Client Retainers

   💰 **Total depositado:** $7,500.00
   📅 Fecha: 2026-01-20
   🏦 Destino: Checking Account
   📝 ID del depósito: 12346
```

---

## 4. Facturas (Invoices)

### Crear Factura Simple

```
👤 Tú: Crea una factura para Acme Corp por $5000 del servicio "Consulting Services"

🤖 Asistente:
   🔍 Buscando cliente...
   ✅ Cliente: Acme Corp (ID: 45)

   🔍 Buscando servicio...
   ✅ Item: Consulting Services (ID: 23, Precio: $150/hr)

   📄 Creando factura...

   ✅ **Factura creada**
      • Cliente: Acme Corp
      • Total: $5,000.00
      • Servicio: Consulting Services
      • Cantidad: 33.33 hrs
      • Número de factura: INV-1234
      • Balance pendiente: $5,000.00
```

### Factura con Múltiples Líneas

```
👤 Tú: Factura para Tech Solutions: $3000 de Consulting y $1200 de Design Work

🤖 Asistente:
   ✅ Factura creada:

   Cliente: Tech Solutions Inc.

   Líneas:
   1. Consulting Services - $3,000.00
   2. Design Work - $1,200.00

   Total: $4,200.00
   Número: INV-1235
```

---

## 5. Cuentas por Pagar (Bills)

### Crear Bill de Proveedor

```
👤 Tú: Crea un bill de Office Depot por $850 de "Office Supplies" con vencimiento
       en 30 días

🤖 Asistente:
   🔍 Buscando vendor...
   ✅ Vendor: Office Depot Inc. (ID: 78)

   🔍 Buscando cuenta de gasto...
   ✅ Cuenta: Office Supplies Expense (ID: 156)

   📝 Creando bill...

   ✅ **Bill creado**
      • Vendor: Office Depot Inc.
      • Monto: $850.00
      • Cuenta: Office Supplies Expense
      • Fecha: 2026-01-20
      • Vencimiento: 2026-02-19
      • Número: BILL-789
```

---

## 6. Pagos Recibidos

### Registrar Pago de Cliente

```
👤 Tú: Registra un pago de $2500 de Acme Corp que aplica a la factura INV-1234

🤖 Asistente:
   🔍 Buscando cliente...
   ✅ Cliente: Acme Corp (ID: 45)

   🔍 Buscando factura INV-1234...
   ✅ Factura encontrada (Balance: $5,000.00)

   💵 Registrando pago...

   ✅ **Pago registrado**
      • Cliente: Acme Corp
      • Monto: $2,500.00
      • Aplicado a: INV-1234
      • Balance restante factura: $2,500.00
      • Depositado en: Checking Account
```

---

## 7. Reportes Financieros

### Profit & Loss Mensual

```
👤 Tú: Dame un reporte de P&L de enero 2026

🤖 Asistente:
   📊 Generando Profit & Loss...

   **Período:** 01/01/2026 - 31/01/2026
   **Método:** Accrual

   **INGRESOS**
   • Consulting Income         $45,230.00
   • Design Services           $18,500.00
   • Other Income              $2,150.00
   ─────────────────────────────────────
   Total Ingresos              $65,880.00

   **GASTOS**
   • Salaries                 ($28,500.00)
   • Office Supplies          ($3,200.00)
   • Rent                     ($5,000.00)
   • Utilities                ($1,850.00)
   ─────────────────────────────────────
   Total Gastos              ($38,550.00)

   **UTILIDAD NETA**           $27,330.00

   ✅ 142 transacciones incluidas
```

### Balance Sheet

```
👤 Tú: Dame el balance general al 20 de enero

🤖 Asistente:
   📊 Generando Balance Sheet...

   **Al:** 20/01/2026

   **ACTIVOS**
   Activos Corrientes:
   • Checking Account          $45,230.50
   • Savings Account           $25,000.00
   • Accounts Receivable       $18,750.00
   • Prepaid Expenses          $3,500.00
   ─────────────────────────────────────
   Total Activos Corrientes    $92,480.50

   **PASIVOS**
   Pasivos Corrientes:
   • Accounts Payable          $12,340.00
   • Client Retainers          $8,500.00
   ─────────────────────────────────────
   Total Pasivos              $20,840.00

   **PATRIMONIO**              $71,640.50
```

### Guardar Reporte

```
👤 Tú: Guarda este reporte como "P&L Mensual Enero"

🤖 Asistente:
   ✅ Reporte guardado como "P&L Mensual Enero"

   Puedes cargarlo después con:
   "Carga el reporte P&L Mensual Enero"
```

---

## 8. Procesamiento CSV Batch

### Paso 1: Crear Template

```
👤 Tú: template csv

🤖 Asistente:
   ✅ Template CSV creado: **deposits_template.csv**

   Contiene ejemplos de formato correcto.
   Edítalo con tus datos y procésalo.
```

### Paso 2: Editar CSV

**Archivo `deposits_january.csv`:**
```csv
customer_name,amount,from_account,to_account,date,memo
Acme Corp,2500.00,Client Retainers,Checking Account,2026-01-15,Anticipo proyecto A
Tech Solutions,1800.00,Prepaid Labour,Checking Account,2026-01-16,Prepago servicios
Design Co,3200.00,Client Retainers,Checking Account,2026-01-17,Anticipo diseño web
Media Inc,1500.00,Client Retainers,Checking Account,2026-01-18,Retainer mensual
```

### Paso 3: Procesar

```
👤 Tú: Procesa el archivo deposits_january.csv

🤖 Asistente:
   📁 Procesando CSV...

   Fila 1/4: Acme Corp... ✅
   Fila 2/4: Tech Solutions... ✅
   Fila 3/4: Design Co... ✅
   Fila 4/4: Media Inc... ✅

   ✅ **Procesamiento completado**

   📊 Resumen:
   • Total filas: 4
   • Exitosos: 4
   • Errores: 0
   • Total procesado: $9,000.00
```

### Manejo de Errores en CSV

```
👤 Tú: Procesa deposits_with_errors.csv

🤖 Asistente:
   📁 Procesando CSV...

   Fila 1/5: Acme Corp... ✅
   Fila 2/5: XYZ Unknown... ❌
   Fila 3/5: Tech Solutions... ✅
   Fila 4/5: Design Co... ❌
   Fila 5/5: Media Inc... ✅

   📊 Resumen:
   • Total filas: 5
   • Exitosos: 3
   • Errores: 2
   • Total procesado: $5,800.00

   ❌ Errores encontrados:
   • Fila 2: Cliente "XYZ Unknown" no encontrado
   • Fila 4: Cuenta "Invalid Account" no encontrada

   💡 Corrige estos errores y vuelve a procesar solo esas filas.
```

---

## 9. Gestión de Reportes Guardados

### Listar Reportes

```
👤 Tú: listar reportes

🤖 Asistente:
   📋 **Reportes Guardados** (3)

   • **P&L Mensual Enero**
     Creado: 2026-01-15 | Último uso: 2026-01-20

   • **Balance Q1 2026**
     Creado: 2026-01-10 | Último uso: 2026-01-18

   • **Reporte Semanal**
     Creado: 2026-01-05 | Último uso: 2026-01-20
```

### Cargar Reporte Guardado

```
👤 Tú: Carga el reporte "P&L Mensual Enero"

🤖 Asistente:
   📂 Cargando configuración...
   📊 Generando reporte...

   **P&L Mensual Enero**
   Período: 01/01/2026 - 31/01/2026

   [... contenido del reporte ...]
```

---

## 10. Comandos de Sistema

### Estadísticas de Tokens

```
👤 Tú: ¿cuánto he gastado?

🤖 Asistente:
   📊 **Estadísticas de la Sesión Actual**

   ⏱️  Duración: 45 minutos
   🔢 Tokens: 28,340 (input: 21,200 | output: 7,140)
   💰 Costo: $0.0102

   📈 Operaciones realizadas:
      • searches: 15
      • deposits: 6
      • invoices: 2
      • reports: 3
      • csv_batches: 1

   💡 Usa 'dame el informe de tokens' para ver estadísticas
      detalladas en Excel
```

### Generar Informe Excel

```
👤 Tú: informe de tokens

🤖 Asistente:
   📊 Generando informe...

   ✅ Informe generado y sobrescrito: **token_usage_report.xlsx**

   Contiene estadísticas completas de todas tus sesiones:
   • Resumen Mensual
   • Detalle por Sesión
   • Estadísticas Generales
   • Distribución por Tipo de Operación

   📈 Resumen rápido:
   • Total gastado (histórico): $0.2450
   • Sesiones totales: 18
   • Proyección mensual: $0.32
```

### Refrescar Chart of Accounts

```
👤 Tú: refrescar chart

🤖 Asistente:
   📥 Descargando Chart of Accounts desde QuickBooks Online...

   ✅ Chart of Accounts actualizado
   📊 148 cuentas cargadas
      Activos: 46 | Pasivos: 29 | Ingresos: 33 | Gastos: 40
```

---

## 💡 Tips y Mejores Prácticas

### 1. Usa Lenguaje Natural

El asistente entiende español natural:

✅ **Bien:**
```
"Muéveme $2500 de anticipos de Acme a checking"
"Dame el P&L del mes pasado"
"Crea una factura para Tech Inc por $5000 de consulting"
```

❌ **No necesitas:**
```
"CREATE DEPOSIT FROM account_id=89 TO account_id=35 AMOUNT=2500"
```

### 2. El Asistente Pregunta si Falta Info

```
👤 Tú: Crea un depósito de $2500

🤖 Asistente:
   Para crear el depósito necesito:
   1. ¿De qué cliente es el dinero?
   2. ¿De qué cuenta origen? (ej: Client Retainers, Prepaid Labour)
   3. ¿A qué cuenta bancaria destino?
```

### 3. Fuzzy Matching es tu Amigo

No necesitas nombres exactos:

```
"prepaid" → encuentra "Prepaid Expenses", "Prepaid Labour"
"acme" → encuentra "Acme Corp", "Acme Corporation"
"check" → encuentra "Checking Account", "Checking - Backup"
```

### 4. Comandos Rápidos Ahorran Tokens

Estos NO consumen tokens LLM:
- `¿cuánto he gastado?`
- `informe de tokens`
- `refrescar chart`
- `template csv`
- `listar reportes`
- `salir`

---

## 🎯 Flujos de Trabajo Comunes

### Workflow: Procesar Anticipos Mensuales

1. **Generar template:** `template csv`
2. **Llenar CSV** con datos de clientes
3. **Procesar:** `procesa deposits_enero.csv`
4. **Verificar:** Revisar errores y corregir
5. **Generar reporte:** `Dame el P&L de enero`

### Workflow: Facturación Mensual

1. **Buscar cliente:** `Busca cliente Acme Corp`
2. **Crear factura:** `Factura para Acme Corp...`
3. **Registrar pago:** `Registra pago de $X de Acme Corp`
4. **Guardar reporte:** `Dame un reporte de cuentas por cobrar y guárdalo`

---

## 🆕 Ejemplos nuevos (v3.5) — Multi-Empresa, OCR, Dexter

### Ejemplo 11: Cambio de empresa en caliente

```
👤: "cambia a Tech Inc"

🤖: [gestionar_empresas("select", "Tech Inc")]

   ✅ Cambiado a Tech Inc
   📊 Chart de cuentas recargado: 87 cuentas
   🔑 Tokens actualizados correctamente

👤: "busca el cliente Acme en esta empresa"

🤖: 🔍 Buscando "Acme" en Tech Inc...
   ℹ️ Tech Inc no tiene clientes con "Acme" en el nombre
   💡 Sugerencia: ¿quizás querías buscar en Acme Corp? Usa "cambia a Acme Corp"
```

### Ejemplo 12: OCR de facturas PDF

```
👤: "Procesa los PDFs en Pending bills"

🤖: 📂 Escaneando carpeta Pending bills/...
   📄 3 PDFs encontrados

   🔄 Procesando acme_jan.pdf con Gemini Flash 2.0...
   ✅ Factura extraída:
      Vendor: ACME Corp
      Total: $1,250.00
      Fecha: 2026-01-15

   🔄 Procesando utility.pdf...
   ✅ Vendor: Electric Company - $345.80

   📊 CSV preview: Pending bills/preview_bills.csv

👤: "apruebo"

🤖: ✅ 2 bills creados en QuickBooks
   📁 Archivos movidos a: Processed bills/
```

### Ejemplo 13: Bank Feed Intelligence con matching

```
👤: "Tengo un cargo de $500 de Office Depot en el banco"

🤖: [analizarbankfeed]

   🔍 Buscando coincidencias...

   ⚠️ Match encontrado:
      • Bill existente: Office Depot #4521 ($498.50) del 15/01
      • Diferencia: $1.50 (probable mismo cargo, redondeo o fee)

   ¿Quieres que use el bill existente o cree uno nuevo?
```

### Ejemplo 14: Reporte personalizado con lenguaje natural

```
👤: "¿Cuáles fueron mis gastos más altos del último trimestre agrupados por categoría?"

🤖: [generarreportecustom]

   📊 Gastos Q4 2025 por categoría:

   1. Payroll:              $125,450 (42%)
   2. Rent & Occupancy:     $45,000  (15%)
   3. Marketing:            $28,900  (10%)
   4. Professional Services:$15,600  (5%)
   5. Insurance:            $12,500  (4%)

   💡 Insight: Marketing subió 22% vs Q3, revisa ROI.

   ¿Quieres que lo guarde como "Gastos Q4"?
```

### Ejemplo 15: Dexter saluda y se presenta

```
👤: "hola"

🤖: ¡Hola Alfredo! 👋 Soy Dexter, tu asistente para QuickBooks.

   📊 Estado actual:
   • Empresa activa: Acme Corp
   • Chart de cuentas: 142 cuentas (cache: 2 horas)
   • Sesión iniciada: 14:30

   ¿En qué te ayudo hoy?
```

---

## 🆘 ¿Necesitas Más Ayuda?

- **Problemas técnicos:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Configuración:** [QUICKSTART.md](QUICKSTART.md)
- **Documentación completa:** [CONTEXT.md](CONTEXT.md)

---

<div align="center">

[⬆ Volver arriba](#-quickbooks-ai-assistant---ejemplos-de-uso)

</div>
