# 📖 MANUAL DE USUARIO: DEXTER (v3.5)
*Tu Asistente de IA Inteligente para QuickBooks*

---

## 📑 CONTENIDO
1. [Introducción](#1-introducción)
2. [Gestión Multi-Empresa](#2-gestión-multi-empresa)
3. [Módulo OCR: Procesamiento de Facturas](#3-módulo-ocr-procesamiento-de-facturas)
4. [Módulo de Bancos: Reconciliación y Matching](#4-módulo-de-bancos-reconciliación-y-matching)
5. [Reportes y Análisis Financiero](#5-reportes-y-análisis-financiero)
6. [Consultas Naturales (CFO Virtual)](#6-consultas-naturales-cfo-virtual)
7. [Guía de "Ayuda Contextual"](#7-guía-de-ayuda-contextual)

---

## 1. INTRODUCCIÓN
Dexter es un agente contable diseñado para automatizar las tareas repetitivas en QuickBooks Online. Utiliza modelos de inteligencia artificial avanzados (DeepSeek/GPT-4) para entender tus instrucciones en español y ejecutarlas directamente en tus libros contables.

---

## 2. GESTIÓN MULTI-EMPRESA
Dexter puede manejar múltiples empresas de QuickBooks de forma independiente.
*   **Al Iniciar**: Dexter te preguntará con qué empresa deseas trabajar.
*   **Contexto**: Cada empresa mantiene su propio historial, Chart of Accounts y reglas de clasificación.
*   **Seguridad**: Los tokens de acceso se gestionan automáticamente por empresa.

---

## 3. MÓDULO OCR: PROCESAMIENTO DE FACTURAS
Esta herramienta extrae datos de PDFs o imágenes de facturas y los crea en QuickBooks.

**Procedimiento:**
1.  Coloca las facturas (PDF/JPG/PNG) en la carpeta `/Pending bills/`.
2.  Dile a Dexter: *"Procesa las facturas pendientes"* o *"Haz el OCR de los recibos"*.
3.  Dexter leerá los archivos, identificará al proveedor, monto, fecha y cuenta contable.
4.  **Validación**: Si Dexter no está seguro de la clasificación, te preguntará antes de crear el registro.
5.  **Finalización**: Los archivos procesados se moverán a la carpeta `/Processed bills/`.

---

## 4. MÓDULO DE BANCOS: RECONCILIACIÓN Y MATCHING
Dexter ayuda a que tu banco y tus libros coincidan perfectamente.

### Reconciliación por CSV:
1.  Coloca tu estado de cuenta en `/Bank Reconciliation/`.
2.  Dile a Dexter: *"Reconcilia el banco con este archivo"*.
3.  Dexter validará que la suma cuadre y creará los depósitos o gastos faltantes.

### Matching Engine (Nuevo):
*   Dexter busca proactivamente si un cargo del banco ya existe en QuickBooks como un cheque o factura pagada.
*   **Evita Duplicados**: Antes de registrar algo, Dexter te dirá: *"Encontré un match para este monto, ¿quieres que lo use en lugar de crear uno nuevo?"*

---

## 5. REPORTES Y ANÁLISIS FINANCIERO
Dexter puede generar visión panorámica de tu negocio.
*   **Profit & Loss (P&L)**: *"Genera un P&L de este mes"* o *"Compara el P&L de enero vs diciembre"*.
*   **Balance Sheet**: *"¿Cómo está mi balance al día de hoy?"*.
*   **Análisis Pro**: Dexter puede generar archivos Excel multicapa con gráficos y comparativas detalladas.

---

## 6. CONSULTAS NATURALES (CFO VIRTUAL)
Puedes hablar con Dexter como si fuera tu contador personal:
*   *"¿Cuánto le debo al proveedor X?"*
*   *"¿Cuáles fueron mis gastos más altos de publicidad el mes pasado?"*
*   *"Busca el cliente que más nos ha comprado este año."*
*   *"¿Tenemos facturas vencidas hoy?"*

---

## 7. GUÍA DE "AYUDA CONTEXTUAL"
Si en algún momento te sientes perdido, usa estos comandos:
*   `ayuda ocr`: Te explicará el paso a paso de las facturas.
*   `ayuda bancos`: Te guiará en la carga de archivos bancarios.
*   `ayuda reportes`: Te dará ejemplos de qué análisis puedes pedir.

---

**Elaborado por:** Dexter AI Assistant  
**Propietario:** Alfredo J.  
**Ubicación de Documentación:** `/ROADMAPDOCS/` y `docs/`
