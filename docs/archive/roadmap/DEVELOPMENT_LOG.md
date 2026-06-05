# 📜 Registro de Desarrollo (Changelog) - Dexter v3.5/v3.7
**Fecha de última actualización:** 23 de Enero, 2026  
**Proyecto:** QuickBooks AI Assistant

---

## 🚀 Cambios Realizados Ayer (22-01-2026)

### 1. Instalación Automatizada e Infraestructura
*   **Script de Instalación (`install.sh`):** Creación de un motor de instalación 100% automatizado con detección de SO (Linux/macOS), gestión de entornos virtuales y configuración interactiva de `.env`.
*   **Estructura de Carpetas Contables:** Estandarización del proyecto mediante la creación de carpetas críticas (`Backup/`, `Bank Reconciliation/`, `Pending bills/`, etc.) aseguradas con `.gitkeep`.
*   **Gestión de Dependencias:** Configuración de `requirements.txt` y validación de librerías esenciales para el procesamiento de datos y OCR.

### 2. Consolidación de Código
*   **Migración Masiva:** Integración de más de 30 archivos Python y ~42,000 líneas de código en la estructura actual del asistente, sentando las bases de la versión 3.x.
*   **Optimización de Git:** Reajuste del `.gitignore` para proteger información sensible y tokens mientras se mantiene la estructura operativa del proyecto.

---

## 🚀 Cambios Realizados Hoy (23-01-2026)

### 1. Reconstrucción Estructural (The Great Fix)
*   **Auditoría de Sintaxis:** Reparación íntegra de `main.py` eliminando bloques truncados y resolviendo múltiples `SyntaxError` que impedían la ejecución.
*   **Restauración de Lógica AI:** Reconstrucción manual del `SYSTEM_PROMPT` y la función `call_llm`, recuperando la orquestación de herramientas (Tool Calls) que estaba corrompida.
*   **Limpieza de Ejecución:** Eliminación de llamadas recursivas y código duplicado ("Ghost Code") al final del script, estabilizando el bucle principal de conversación.
*   **Normalización de Imports:** Centralización y limpieza de la zona de encabezados, vinculando correctamente el módulo `company_manager.py` con el núcleo de la aplicación.
*   **Gestión de Sesión:** Refactorización de `session_state` para un rastreo dinámico de tokens y costos basado en el modelo (Hybrid Routing).

### 2. Identidad y Personalidad
*   **Fijación de Branding:** Nombre oficial del asistente: **Dexter**.
*   **Banner Minimalista:** Rediseño del banner de inicio para máxima compatibilidad con terminales Linux y macOS.
*   **Tono Dinámico:** Ajuste del comportamiento para ser más proactivo, educativo y cercano al usuario.

### 3. Sistema Multi-Empresa PRO (v3.5)
*   **Aislamiento de Contexto:** Cada empresa en QuickBooks ahora tiene su propia base de datos de contexto (`context.json`) y tokens (`meta.json`) en subcarpetas aisladas bajo `./companies/`.
*   **Hot-Swap de Empresas:** Implementación de la herramienta `gestionar_empresas` que permite cambiar de compañía en tiempo real sin reiniciar la aplicación.

### 4. Inteligencia Híbrida y Bilingüe (v3.6)
*   **Model Routing:** Dexter ahora decide entre Llama 3 (tareas simples) y DeepSeek V3 (análisis contable) para optimizar costos y velocidad.
*   **Soporte ES/EN:** Sistema de traducción dinámica con persistencia de idioma guardada por empresa.

### 5. Guía Interactiva y Automatización de Bancos (v3.7)
*   **Matching Engine (Bank Feed):** Diseño técnico del motor de conciliación inteligente entre CSVs bancarios y registros existentes en QBO para evitar duplicidades.
*   **Sistema de Onboarding:** Dexter detecta el estado de las carpetas y ofrece guiar al usuario paso a paso en tareas complejas (OCR, Reconciliación).
*   **Manual de Usuario Vivo:** Creación de `MANUAL_USUARIO.md`, integrándolo como la base de conocimiento primaria del agente para su propia auto-explicación.

---

## 🛠️ Estado del Proyecto
*   **Versión Actual:** v3.7 (Interactive Guide Ready)
*   **Estabilidad:** Crítica estabilizada / Operativa.
*   **Seguridad:** Backups preventivos generados en `Backup/`.

**Elaborado por:** Dexter (vía Alfredo)
