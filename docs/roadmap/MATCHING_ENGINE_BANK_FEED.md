# 🏦 Módulo: Matching Engine para Bank Feed

**Fecha:** 23 de Enero, 2026  
**Documento Relacionado:** ANALISIS_FINANCIERO_PRO.md, MEMORIA_Y_ARQUITECTURA.md  
**Estado:** Propuesto / Fase de Diseño

---

## 📋 VISIÓN GENERAL
Este módulo busca automatizar la tarea diaria más crítica de un contador en QuickBooks: la conciliación y el "matching" de transacciones del banco con registros contables existentes (Checks, Bill Payments, Sales Receipts, etc.).

Debido a limitaciones técnicas de la API pública de QuickBooks (V3), Dexter no puede acceder directamente a la pestaña de "Banking" de la interfaz web. Este documento propone una arquitectura alternativa para emular y superar esa funcionalidad.

---

## 🛠️ DESAFÍOS TÉCNICOS Y LIMITACIONES
1.  **Bloqueo de API de Bank Feed**: La API de Intuit no expone las transacciones pendientes en el "Bank Feed" (aquellas que no han sido aceptadas en los libros).
2.  **Imposibilidad de Scraping**: El uso de herramientas de automatización web (Selenium/Playwright) es descartado por su fragilidad ante cambios de UI y bloqueos por MFA (Multi-Factor Authentication).

---

## 💡 PROPUESTA DE SOLUCIÓN: "DEXTER EYE"
La solución consiste en delegar la "visión" del banco a un archivo CSV/Excel proporcionado por el usuario, permitiendo que Dexter realice el razonamiento contable.

### Flujo de Trabajo
1.  **Input de Datos**: El usuario coloca el CSV del estado de cuenta bancario en una carpeta monitoreada (ej: `/Bank Reconciliation/Pending/`).
2.  **Escaneo Proactivo**: Al iniciar la sesión, Dexter detecta el archivo e inicia automáticamente la tarea de "Matching".
3.  **Algoritmo de Matching Inteligente**:
    *   **Monto**: Búsqueda de coincidencia exacta.
    *   **Fecha**: Ventana de coincidencia de +/- 5 días.
    *   **Payee/Vendor**: Uso de similitud de texto (Fuzzy Matching) para identificar proveedores incluso con nombres truncados en el banco (ej: "AMZN MKTP" -> "Amazon").
4.  **Categorización de Coincidencias**:
    *   **Match Directo**: Existe un Cheque o Gasto ya registrado.
    *   **Cruce de Deuda**: Existe un Bill pendiente para el mismo proveedor y monto.
    *   **Entrada de Venta**: Existe un Invoice pendiente o un Payment Received.
5.  **Interacción Natural**: Dexter presenta los hallazgos:
    > "Alfredo, encontré un cargo de $228.75. En QuickBooks ya existe el **Check #75**. ¿Lo conciliamos?"

---

## 🚀 IMPACTO PARA EL CONTADOR
*   **Eliminación de Duplicados**: Evita registrar manualmente gastos que ya fueron creados previamente (como cheques emitidos).
*   **Velocidad de Cierre**: Reduce el tiempo de conciliación de horas a minutos.
*   **Criterio de IA**: Dexter puede sugerir aplicaciones de pagos a facturas pendientes basadas en montos, algo que el matching automático de QBO a veces ignora.

---

## 📅 PLAN DE IMPLEMENTACIÓN
1.  **Herramienta `tool_detectar_coincidencias`**: Función para buscar en las tablas `Purchase`, `BillPayment`, `Payment`, `Deposit`.
2.  **Módulo de Inicio**: Hook en `main.py` para disparar el análisis al cargar la empresa.
3.  **Lógica de Diferencias**: Manejo de pequeñas diferencias por comisiones bancarias o tasas de cambio.

---

**Elaborado por:** Dexter (vía Alfredo)  
**Aprobado por:** Alfredo  
