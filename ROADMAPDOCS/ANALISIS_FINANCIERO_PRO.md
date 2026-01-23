# 📊 Arquitectura: Módulo de Análisis Financiero Pro (CFO Virtual)

**Fecha:** 23 de Enero, 2026  
**Documento de Especificación Técnica**  
**Versión:** 1.0

---

## 1. Visión General
Transformar a **Dexter** en un analista financiero capaz de interpretar datos crudos de QuickBooks y transformarlos en reportes ejecutivos de alto valor en formato Excel (.xlsx), orientados a la toma de decisiones gerenciales.

## 2. Pilares de la Implementación

### A. Motor de Reportes Multicapa (Excel Engine)
*   **Librería Principal:** `openpyxl` fusionada con `pandas`.
*   **Estructura del Output:**
    *   **Pestaña 1: Resumen Ejecutivo:** Generado por el LLM (DeepSeek V3). Redacción profesional sobre la salud financiera, advertencias y recomendaciones.
    *   **Pestaña 2: Análisis Comparativo (P&L):** Tablas dinámicas que comparan el período actual vs períodos anteriores (Mes, 3 meses, o Año Anterior).
    *   **Pestaña 3: Inteligencia de Gastos (Drill-down):** Análisis detallado de proveedores, detectando variaciones de precios y concentración de gastos.
    *   **Pestaña 4: Gráficos:** Visualizaciones nativas de Excel (Barras para ingresos/gastos, Líneas para tendencias, Circular para distribución de costos).

### B. Análisis de Variaciones (Horizontal Analysis)
*   Cálculo automático de **Delta Absoluto** ($) y **Delta Porcentual** (%) entre períodos.
*   Análisis de la métrica **Gasto vs Ingreso Bruto** para determinar la eficiencia operativa.
*   Clasificación de variaciones: Identificación de cambios "Anómalos" (ej: un aumento del 20% en una cuenta de gasto recurrente).

### C. Sistema de Memoria de Reportes (Presets)
Para evitar la fricción de configurar el reporte cada vez, se implementará un `TemplateManager`:
*   **Parámetros guardados:** Método contable (Accrual/Cash), Cuentas clave, Filtros de proveedores, Tipos de gráficos.
*   **Comando de Voz/Texto:** *"Dexter, ejecuta mi reporte mensual estándar"*.

## 3. Flujo de Trabajo (Interaction Design)
1.  **Petición del Usuario:** Consulta general o específica de análisis.
2.  **Clarificación Proactiva:** Dexter pregunta por el "Benchmark" (contra qué comparar) y el nivel de detalle deseado.
3.  **Extracción de Datos:** Llamados múltiples a la API de QBO (`ProfitAndLoss`, `BalanceSheet`, `TransactionList`).
4.  **Procesamiento:** Uso de `pandas` para lógica matemática y `openpyxl` para construcción del archivo.
5.  **Entrega Final:** Link de descarga/ubicación del archivo final "Listo para el cliente".

## 4. Estratégia de Rentabilidad (SaaS/Licencia)
Esta funcionalidad permite posicionar a Dexter en un rango de precio de **Consultoría de Negocios**, no solo de Herramienta de Software. Es un "CFO as a Service" que escala con un costo marginal cercano a cero.

---

**Elaborado por:** Dexter (vía Alfredo)
