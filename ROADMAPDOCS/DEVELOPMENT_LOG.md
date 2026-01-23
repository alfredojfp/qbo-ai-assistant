# 📜 Registro de Desarrollo (Changelog) - Dexter v3.5/v3.6

**Fecha:** 23 de Enero, 2026  
**Proyecto:** QuickBooks AI Assistant

---

## 🚀 Cambios Realizados Hoy (23-01-2026)

### 1. Restauración de Identidad y Estética
*   **Identidad:** Se fijó oficialmente el nombre del asistente como **Dexter** (anteriormente Alfredo/TMP AI).
*   **Banner:** Se reemplazó el banner ASCII complejo por uno minimalista y profesional para evitar errores de renderizado en terminal.
*   **Prompt del Sistema:** Rediseño total del `SYSTEM_PROMPT` para incluir reglas de comportamiento claras, terminología contable específica y validaciones críticas.

### 2. Estabilización de Lógica Core
*   **Función `call_llm`:** Se corrigió una variable no definida (`system_content`) y se optimizó el paso del historial de conversación para evitar pérdida de contexto.
*   **Loop Principal:** Actualización de mensajes de inicio y cierre, reflejando la nueva identidad del asistente.

### 3. Sistema Multi-Empresa PRO (v3.5)
*   **Módulo `company_manager.py`:** Creación de un motor independiente para gestionar múltiples cuentas de QuickBooks.
*   **Registro Dinámico:** Nueva herramienta `gestionar_empresas` que permite registrar empresas pegando directamente un link de QBO.
*   **Hot-Swap:** Capacidad de cambiar de empresa "en caliente" sin reiniciar el script.
*   **Aislamiento de Tokens:** Los tokens de acceso y refresco ahora se guardan por separado en `companies/[Nombre]/meta.json`.

### 4. Soporte Bilingüe (v3.6 Pre-release)
*   **Idiomas:** Implementación de soporte oficial para **Español** e **Inglés**.
*   **Comando Rápido:** Añadida lógica para cambiar de idioma instantáneamente escribiendo "cambiar idioma".
*   **Persistencia:** El idioma preferido se guarda por empresa, permitiendo tener clientes en diferentes lenguas.

### 5. Documentación Estratégica
*   **`CONTEXT.md`**: Actualizado a la versión 3.5 con toda la nueva arquitectura.
*   **`ROADMAP.md`**: Creación de la hoja de ruta para futuras fases (Movilidad, IA Proactiva, Optimización).
*   **`ROADMAPDOCS/`**: Nueva carpeta para documentación técnica detallada.
*   **`MEMORIA_Y_ARQUITECTURA.md`**: Análisis profundo sobre la futura implementación de Memoria Vectorial y Embeddings.

---

## 🛠️ Próximos Pasos (En Desarrollo)
*   **Implementación de Enrutador de Modelos (Hybrid LLM):** Integración de Llama 3.1 8B para tareas simples y reserva de DeepSeek V3 para análisis complejo (Optimización de costos en OpenRouter).
*   **Backup preventivo realizado.**
