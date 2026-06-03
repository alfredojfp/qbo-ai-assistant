# 🚀 Plan de Acción: Evolución de Dexter (QuickBooks AI Assistant)

**Fecha:** 23 de Enero, 2026  
**Versión del Plan:** 1.0  
**Estado Actual:** v3.7 (Guía Interactiva, Matching Engine) — base v3.5 (Multi-Empresa) + v3.6 (Híbrido/Bilingüe)

---

## 📋 INTRODUCCIÓN
Este documento define la hoja de ruta estratégica para transformar a **Dexter** de un asistente basado en terminal en un ecosistema de gestión contable autónomo, proactivo y multiplataforma.

---

## 🛠️ FASE 1: ACCESIBILIDAD Y MOVILIDAD (UX/UI)
*Objetivo: Sacar a Dexter de la terminal y llevarlo al bolsillo del usuario.*

1.  **Integración con WhatsApp/Telegram API**:
    *   Permitir el envío de consultas de texto y fotos de facturas vía mensajería.
    *   Notificaciones push sobre saldos bancarios o alertas de facturas por pagar.
2.  **Dashboard Visual (Streamlit/Next.js)**:
    *   Interfaz web para visualizar gráficos de P&L, balance general y KPI financieros.
    *   Selector visual de empresas y gestión de tokens.
3.  **OCR en Tiempo Real**:
    *   Procesamiento instantáneo de fotos de tickets y facturas desde el móvil con registro automático en QBO.

---

## 📊 FASE 2: INTELIGENCIA CONTABLE PROACTIVA (Funcionalidad)
*Objetivo: Automatizar el criterio contable y mejorar la precisión de los datos.*

1.  **Matching Inteligente (OCR ↔ Bank Feed ↔ Libros)**:
    *   **Tarea Diaria Proactiva**: Al iniciar, Dexter analiza el estado de cuenta bancario (CSV) y busca coincidencias con registros existentes (Checks, Bill Payments, Payments).
    *   Cruzar datos de facturas extraídas por OCR con transacciones pendientes en el banco para evitar duplicados.
    *   Sugerencias de conciliación automática inteligente basada en monto, fecha y vendor.
2.  **Módulo de Forecasting (Flujo de Caja)**:
    *   Análisis predictivo de ingresos y gastos para los próximos 30/60/90 días.
    *   Alertas tempranas de falta de liquidez.
3.  **Gestión de Adjuntos Digitales**:
    *   Subida automática del archivo PDF/Imagen a la transacción correspondiente en QuickBooks para auditorías "paperless".
4.  **Módulo de Análisis Avanzado (CFO Virtual)**:
    *   **Reportes Multi-Periodo**: Capacidad de comparar P&L y balances entre múltiples períodos (mensuales, trimestrales, anuales) con cálculo automático de variaciones (Accrual/Cash).
    *   **Excel Premium Multicapa**: Generación de archivos .xlsx con múltiples pestañas (Resumen Ejecutivo, P&L Comparativo, Análisis de Proveedores, Gráficos Dinámicos).
    *   **Análisis de Drill-down de Gastos**: Identificación proactiva de aumentos de precios por proveedor y relación gasto vs ventas.
    *   **Memoria de Reportes (Presets)**: Guardado de configuraciones de análisis favoritas para ejecución recurrente con un solo comando.

---

## 🧠 FASE 3: COGNICIÓN SUPERIOR Y MEMORIA (IA)
*Objetivo: Hacer que Dexter sea "sabio" y aprenda del pasado de Alfredo.*

1.  **Memoria de Largo Plazo (Vector Database)**:
    *   Implementación de ChromaDB o Pinecone para almacenar decisiones históricas.
    *   Capacidad de recordar contextos de hace meses (ej: "Clasificamos esto como X el año pasado").
2.  **Personalidad Proactiva y Analítica**:
    *   Dexter dejará de ser reactivo. Iniciará conversaciones si detecta anomalías (ej: "Alfredo, detecté un gasto duplicado").
3.  **Refinamiento Multilingüe (Hybrid Language Handling)**:
    *   Entendimiento perfecto de instrucciones en "es-en" simultáneo (Spanglish técnico-contable).

---

## ⚡ FASE 4: OPTIMIZACIÓN Y ESCALABILIDAD (Técnico)
*Objetivo: Reducir costos operativos y mejorar la velocidad de respuesta.*

1.  **Implementación de QuickBooks Batch API**:
    *   Migrar de creación individual de transacciones a envíos agrupados (hasta 50 por llamado).
2.  **Enrutador de Modelos (Model Router)**:
    *   Uso de modelos ligeros (Llama 3/Haiku) para tareas de baja complejidad.
    *   Reserva de DeepSeek V3/GPT-4o solo para análisis profundo y generación de reportes.
3.  **Validaciones Pre-Flight**:
    *   Comprobación de reglas de negocio antes de llamar a la API para ahorrar tiempo de red y fallos de crédito.

---

## 📈 MÉTRICAS DE ÉXITO ESPERADAS
- **Reducción de tiempo manual**: -90% en registro de gastos minoristas.
- **Precisión contable**: >98% en clasificación automática.
- **Costos operativos**: Reducción del 30% en uso de tokens mediante optimización de modelos.

---

**Elaborado por:** Dexter (vía Alfredo)  
**Aprobado por:** Alfredo  
