# 📜 Registro de Desarrollo (Changelog) - Dexter v3.5/v3.6

**Fecha:** 23 de Enero, 2026  
**Proyecto:** QuickBooks AI Assistant

---

## 🚀 Cambios Realizados Hoy (23-01-2026)

### 1. Restauración de Identidad y Estética
*   **Identidad:** Se fijó oficialmente el nombre del asistente como **Dexter** (anteriormente Alfredo/TMP AI).
*   **Banner:** Se reemplazó el banner ASCII complejo por uno minimalista y profesional para evitar errores de renderizado en terminal.
*   **Prompt del Sistema:** Rediseño total del `SYSTEM_PROMPT` para incluir reglas de comportamiento claras, terminología contable específica y validaciones críticas.

### 2. Estabilización Técnica y Refactorización (Critical Fixes)
*   **Restauración de Código Corrupto:** Se recuperó el bloque `SYSTEM_PROMPT` que se había perdido o corrompido, devolviendo la lógica base al agente.
*   **Corrección de Sintaxis:** Se resolvieron múltiples `SyntaxError` en las definiciones de funciones clave, particularmente en `call_llm`.
*   **Manejo de Imports:** Se limpiaron imports duplicados y se agregaron librerías faltantes como `pandas` y las funciones específicas de `company_manager`.
*   **Eliminación de Redundancias:** Se eliminaron llamadas duplicadas al `main_loop()` al final del script que causaban ejecuciones dobles.
*   **Lógica de Costos:** Se refactorizó `update_token_usage` y `calculate_session_cost` para transicionar de un precio fijo a un cálculo dinámico basado en el modelo utilizado (Hybrid LLM).

### 3. Sistema Multi-Empresa PRO (v3.5)
*   **Módulo `company_manager.py`:** Creación de un motor independiente para gestionar múltiples cuentas de QuickBooks de forma aislada.
*   **Registro Dinámico:** Nueva herramienta `gestionar_empresas` que permite registrar empresas pegando directamente un link de QBO o un Realm ID.
*   **Hot-Swap:** Capacidad de cambiar de empresa "en caliente" sin reiniciar el script, gestionando contextos de forma segura.
*   **Tokens Independientes:** Almacenamiento cifrado/aislado de tokens por empresa en `./companies/[Nombre]/meta.json`.

### 4. Soporte Bilingüe y Optimización de Modelos (v3.6)
*   **Idiomas:** Implementación de soporte oficial para **Español** e **Inglés**, con persistencia de idioma guardada por empresa.
*   **Comando Rápido:** Lógica simplificada para cambiar de idioma instantáneamente escribiendo "cambiar idioma".
*   **Enrutador de Modelos (Hybrid LLM):** Dexter ahora decide dinámicamente:
    *   **Llama 3.1 8B:** Para tareas administrativas y consultas simples (Ahorro de costos).
    *   **DeepSeek V3:** Para análisis financiero, clasificación contable y lógica compleja.

### 5. Documentación y Control de Calidad
*   **`CONTEXT.md`**: Actualizado a la versión 3.5 reflejando la nueva arquitectura híbrida.
*   **`ROADMAPDOCS/`**: Creación de esta carpeta centralizada para planificación y logs de desarrollo.
*   **`MEMORIA_Y_ARQUITECTURA.md`**: Documento de consulta técnica sobre futuras implementaciones de Vector DB y Embeddings.
*   **Testing:** Actualización de `test_suite.py` para validar la integridad de las nuevas herramientas y estructuras de datos.

---

## 🛠️ Estado del Proyecto
*   **Versión Actual:** v3.6 (Hybrid Model Ready)
*   **Estabilidad:** Alta (Sintaxis verificada y compilada)
*   **Backup preventivo:** Realizado exitosamente en `Backup/`.

**Elaborado por:** Dexter (vía Alfredo)
