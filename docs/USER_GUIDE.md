# 📖 Guía de Usuario: Dexter (v3.5)
*Tu Asistente de IA Inteligente para QuickBooks*

> **Nota histórica:** Este documento es la versión expandida de `MANUAL_USUARIO.md` (v3.5), reorganizado y renombrado a `USER_GUIDE.md` como parte de la organización de documentación realizada el 2026-06-03.

---

## 📑 Contenido

1. [Introducción: ¿Qué es Dexter?](#1-introducción-qué-es-dexter)
2. [Primeros pasos](#2-primeros-pasos)
3. [Gestión Multi-Empresa](#3-gestión-multi-empresa)
4. [Módulo OCR: Procesamiento de Facturas](#4-módulo-ocr-procesamiento-de-facturas)
5. [Módulo de Bancos: Reconciliación y Matching](#5-módulo-de-bancos-reconciliación-y-matching)
6. [Reportes y Análisis Financiero](#6-reportes-y-análisis-financiero)
7. [Consultas Naturales (CFO Virtual)](#7-consultas-naturales-cfo-virtual)
8. [Glosario de Términos](#8-glosario-de-términos)
9. [FAQ - Preguntas Frecuentes](#9-faq---preguntas-frecuentes)
10. [Ayuda Contextual: Comandos Rápidos](#10-ayuda-contextual-comandos-rápidos)

---

## 1. Introducción: ¿Qué es Dexter?

**Dexter** es un agente contable con inteligencia artificial diseñado para automatizar las tareas repetitivas en QuickBooks Online. Utiliza modelos de IA avanzados (DeepSeek V3 / GPT-4) para entender tus instrucciones en español y ejecutarlas directamente en tus libros contables.

A diferencia de otros asistentes, Dexter:

- ✅ Entiende terminología contable latinoamericana (anticipo, prepago, retainer, etc.)
- ✅ Tiene acceso directo a tu QBO (no es solo un chatbot)
- ✅ Aprende de tus patrones con el tiempo
- ✅ Puede ejecutar código Python para análisis avanzados
- ✅ Gestiona múltiples empresas de forma independiente

### ¿Para quién es?

- **Contadores** que quieren automatizar tareas repetitivas
- **Emprendedores** que llevan su propia contabilidad
- **Despachos contables** con múltiples clientes

---

## 2. Primeros pasos

### Antes de empezar

1. **Instalación completada:** Si aún no has instalado Dexter, sigue [`INSTALL.md`](INSTALL.md)
2. **Empresa configurada:** Al menos una empresa de QBO autorizada
3. **Conexión a internet:** Stable, para acceso a QBO y al LLM

### Tu primer comando

```bash
python main.py
```

Verás algo como:

```
============================================================
   🏢  DEXTER - QuickBooks AI Assistant v3.5
============================================================

🔐 Selecciona empresa:
  1. ⭐ Acme Corp (por defecto)
  2. Tech Inc
  3. Design Co

Empresa [1]: _
```

Selecciona la empresa con la que quieres trabajar (o presiona Enter para la por defecto).

### Tu primera conversación

```
👤 Tú: Busca el cliente de prueba

🤖 Dexter: 🔍 Buscando "cliente de prueba"...
   ✅ Encontré: ACME Test Client (ID: 123, balance: $0.00)
   ¿Quieres ver más detalles?
```

¡Listo! Ya estás hablando con Dexter.

---

## 3. Gestión Multi-Empresa

Dexter puede manejar múltiples empresas de QuickBooks de forma independiente.

### Al iniciar

Si tienes más de una empresa registrada, Dexter te preguntará con cuál deseas trabajar.

### Cambio en caliente

Puedes cambiar de empresa en cualquier momento:

```
👤: "cambia a Tech Inc"

🤖: ✅ Cambiado a Tech Inc
   📊 Chart de cuentas recargado: 87 cuentas
   🔑 Tokens actualizados
```

### Contexto aislado

Cada empresa mantiene:
- Su propio Chart of Accounts
- Sus propias configuraciones de reportes
- Su propio historial de bank feed
- Sus propios tokens de acceso

> **Más detalles:** Ver [`MULTI_EMPRESA.md`](MULTI_EMPRESA.md)

---

## 4. Módulo OCR: Procesamiento de Facturas

Esta herramienta extrae datos de PDFs o imágenes de facturas y los crea en QuickBooks automáticamente.

### Procedimiento

1. **Coloca las facturas** (PDF/JPG/PNG) en la carpeta `/Pending bills/`
2. **Dile a Dexter:** *"Procesa las facturas pendientes"* o *"Haz el OCR de los recibos"*
3. **Dexter analiza** cada archivo, identifica proveedor, monto, fecha y cuenta contable
4. **Validación:** Si Dexter no está seguro, te preguntará antes de crear el registro
5. **Finalización:** Los archivos procesados se mueven a `/Processed bills/`

### Ejemplo real

```
👤: "Procesa los PDFs en Pending bills"

🤖: 📂 Escaneando carpeta Pending bills/...
   📄 3 PDFs encontrados

   🔄 Procesando acme_jan.pdf...
   ✅ Vendor: ACME Corp
   ✅ Total: $1,250.00

   🔄 Procesando utility_bill.pdf...
   ✅ Vendor: Electric Company
   ✅ Total: $345.80

   📊 CSV preview: Pending bills/preview_bills.csv
   ¿Apruebo la creación de los bills? (sí/no)
```

### Costos

- ~$0.0006 USD por factura
- Usa Gemini Flash 2.0 (modelo económico)

---

## 5. Módulo de Bancos: Reconciliación y Matching

Dexter ayuda a que tu banco y tus libros coincidan perfectamente.

### Reconciliación por CSV

1. Coloca tu estado de cuenta (CSV) en `/Bank Reconciliation/`
2. Dile a Dexter: *"Reconcilia el banco con este archivo"*
3. Dexter validará que la suma cuadre y creará los depósitos o gastos faltantes

Dos modos disponibles:
- **Con balance:** validación matemática completa
- **Sin balance:** más rápido, solo identifica transacciones

### Matching Engine (Bank Feed Intelligence)

Dexter busca proactivamente si un cargo del banco ya existe en QuickBooks:

```
👤: "Tengo un cargo de $500 de Office Depot en el banco"

🤖: 🔍 Buscando coincidencias...
   ⚠️ Encontré: Ya existe un bill de Office Depot por $498.50 del 15/01
   (diferencia de $1.50, posiblemente el mismo cargo)

   ¿Quieres que use el bill existente o cree uno nuevo?
```

### Evita duplicados

Antes de registrar algo, Dexter te dirá si ya existe una transacción similar.

---

## 6. Reportes y Análisis Financiero

### Reportes predefinidos

```
👤: "Dame el P&L de este mes"
🤖: [genera Profit & Loss de enero 2026]

👤: "¿Cómo está mi balance hoy?"
🤖: [genera Balance Sheet al día actual]

👤: "Compara el P&L de enero vs diciembre"
🤖: [genera ambos y muestra comparación]
```

### Reportes personalizados (CFO Virtual)

Dexter interpreta lenguaje natural para queries complejas:

```
👤: "¿Cuánto le debo al proveedor ACME?"
🤖: 🔍 Buscando bills pendientes de ACME...
   💰 Total adeudado: $3,450.00 (3 bills)
   • Bill #001: $1,250.00 (vence 15/02)
   • Bill #005: $1,500.00 (vence 28/02)
   • Bill #008: $700.00 (vencido desde 10/01)

👤: "¿Cuáles fueron mis gastos más altos del mes pasado?"
🤖: [analiza bills y agrupa por categoría]
   📊 Top 5 categorías de gasto (diciembre):
   1. Payroll: $45,000
   2. Rent: $12,000
   3. Marketing: $8,500
   ...

👤: "¿Tenemos facturas vencidas hoy?"
🤖: [busca invoices con due_date < hoy y balance > 0]
   ⚠️ 4 facturas vencidas, total: $7,850.00
```

### Guardar configuración

Si haces un reporte recurrente:

```
👤: "Genera este P&L y guárdalo como 'Quincenal'"

🤖: ✅ P&L generado y guardado como "Quincenal"
   Para cargarlo en el futuro: "carga el reporte Quincenal"
```

---

## 7. Consultas Naturales (CFO Virtual)

Puedes hablar con Dexter como si fuera tu contador personal:

- *"¿Cuánto le debo al proveedor X?"*
- *"¿Cuáles fueron mis gastos más altos de publicidad el mes pasado?"*
- *"Busca el cliente que más nos ha comprado este año."*
- *"¿Tenemos facturas vencidas hoy?"*
- *"Dame el flujo de caja del trimestre."*
- *"¿Cuál es mi margen bruto?"*

Dexter decide qué herramientas invocar para responder.

---

## 8. Glosario de Términos

| Término | Significado en QBO |
|---------|-------------------|
| **Anticipo** | Customer Deposit (pasivo) - dinero recibido antes de facturar |
| **Prepago** | Prepaid Expense (activo) - gasto pagado por adelantado |
| **Retainer** | Sin equivalente directo, se maneja como Customer Deposit |
| **Proveedor** | Vendor |
| **Factura** | Invoice (cuenta por cobrar) |
| **Cuenta por pagar** | Bill |
| **Depósito** | Bank Deposit |
| **Asiento** | Journal Entry |
| **Libro mayor** | Chart of Accounts |
| **Estado de cuenta** | Bank Statement |
| **Conciliación** | Reconciliation |

---

## 9. FAQ - Preguntas Frecuentes

### ¿Cuánto cuesta usar Dexter?

~$0.006 USD por sesión de 45 minutos. Ver [CAPACIDADES.md](CAPACIDADES.md#-tabla-resumen-costo-por-operación) para detalles.

### ¿Mis datos están seguros?

Sí:
- Credenciales en `.env` (no en código)
- Comunicación con QBO vía OAuth 2.0
- Datos aislados por empresa

### ¿Funciona sin internet?

No. Requiere conexión para:
- Llamadas a QBO API
- Llamadas al LLM (DeepSeek V3)
- OCR (Gemini, opcional)

### ¿Puedo agregar mis propios tools?

Sí, pero requiere conocimientos de Python. Ver [ARCHITECTURE.md](ARCHITECTURE.md#-extensibilidad) para la guía de extensibilidad.

### ¿Qué pasa si cambio de empresa a mitad de conversación?

Dexter guarda el contexto y carga el de la nueva empresa. No se pierde información.

### ¿Cuántas empresas puedo registrar?

Sin límite técnico, pero cada empresa requiere autorización OAuth separada.

### ¿Funciona con QuickBooks Desktop?

No, solo QuickBooks Online (QBO).

### ¿Puedo usar otro LLM en lugar de DeepSeek?

El sistema está optimizado para DeepSeek V3, pero teóricamente puedes cambiar el modelo modificando la configuración en `main.py`.

---

## 10. Ayuda Contextual: Comandos Rápidos

Si en algún momento te sientes perdido, usa estos comandos (no consumen tokens):

| Comando | Función |
|---------|---------|
| `ayuda` | Muestra ayuda general |
| `ayuda ocr` | Paso a paso del OCR de facturas |
| `ayuda bancos` | Guía para reconciliación |
| `ayuda reportes` | Ejemplos de análisis que puedes pedir |
| `refrescar chart` | Recarga el Chart of Accounts desde QBO |
| `template csv` | Genera plantilla de depósitos en CSV |
| `listar reportes` | Muestra reportes guardados |
| `¿cuánto he gastado?` | Estadísticas de tokens de la sesión |
| `salir` | Termina la sesión |

---

## 🆘 ¿Necesitas más ayuda?

1. **Revisa la documentación:** [`docs/`](.)
2. **Busca en Troubleshooting:** [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
3. **Mira ejemplos:** [`EXAMPLES.md`](EXAMPLES.md)
4. **Si es un bug:** Contacta al desarrollador (Alfredo)

---

**Elaborado por:** Dexter AI Assistant
**Propietario:** Alfredo J.
**Versión del documento:** 3.5
**Última actualización:** 2026-06-03
