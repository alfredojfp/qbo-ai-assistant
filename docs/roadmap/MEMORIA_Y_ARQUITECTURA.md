# 🧠 Consulta Técnica: Memoria de Largo Plazo y Estrategias de Evolución

**Tema:** Implementación de Memoria Vectorial vs. Lógica Estructurada en Dexter  
**Fecha:** 23 de Enero, 2026  
**Proyecto:** QuickBooks AI Assistant (v3.7 — análisis basado en v3.5)

---

## 💬 Transcripción de la Consulta

### 1. El Desafío de la Memoria de Largo Plazo
**Usuario:** "Memoria de Largo Plazo (Vector DB): En lugar de solo recordar los últimos 5 turnos, usar una base de datos vectorial (como ChromaDB) para que Dexter recuerde decisiones que tomaste hace meses. Ejemplo: '¿Recuerdas que la última vez clasificamos este gasto de Amazon como Suministros de Oficina? He aplicado lo mismo hoy'. NO modifiques el codigo, como funcionaria esta opcion? haria falta implementar alguna base de datos?"

**Dexter:** Explicó que se requiere una **Base de Datos Vectorial** (como ChromaDB) para implementar un sistema de **Recuperación Aumentada por Generación (RAG)**.
*   **Funcionamiento:** Se crean "Embeddings" (representaciones numéricas del significado) de cada decisión pasada.
*   **Flujo:** Dexter busca en la DB recuerdos similares antes de responder, inyectando ese contexto histórico en el prompt actual.

### 2. Infraestructura y Conectividad
**Usuario:** "Ok, pero tendria que conectar mi programa a alguna base de datos u otro servicio?"

**Dexter:** Presentó dos alternativas:
*   **Opción Local (Recomendada):** Usar **ChromaDB**. Es una librería de Python que guarda los datos en una carpeta del proyecto. Cero servidores externos, máxima privacidad y sin costo.
*   **Opción Cloud:** Servicios como Pinecone. Los datos viven en la nube y se accede vía API. Es más fácil de escalar pero requiere internet y enviar datos fuera.

### 3. La Necesidad del Embedding
**Usuario:** "Pero seria necesario el embedding correcto?"

**Dexter:** Confirmó que el **Embedding es obligatorio**. Es la "traducción" de texto a matemáticas que la base de datos puede entender para buscar por "similitud" en lugar de palabras exactas.
*   **Localmente:** Usando la librería `sentence-transformers` (Gratis e infinito).
*   **Vía API:** Usando OpenAI o Google Gemini (Costo ínfimo, muy rápido).

### 4. Comparativa: v3.7 (actual) vs. Implementación Vectorial
**Usuario:** "Cual seria la diferencia de funcionamiento, ventajas y desventajas de esa implementacion vs la version actual?"

**Dexter:** Comparó la memoria de corto plazo actual (basada en sesiones/JSON) con la vectorial:
*   **Actual:** Limitada a lo reciente, búsqueda por palabras exactas, aumenta el gasto de tokens en charlas largas.
*   **Vectorial:** Memoria de años, entiende sinónimos/contexto, ahorra tokens al recuperar solo lo relevante, pero es más compleja de programar.

### 5. Alternativas sin Vector DB (Opciones Ligeras)
**Usuario:** "Y de que otra manera podrias mejorar ese apartado de mi app sin realizar esta implementacion, que opciones recomiendas?"

**Dexter:** Sugirió 5 estrategias de bajo impacto técnico y alta efectividad:
1.  **Lite-RAG (Keyword Memory):** Búsqueda simple de texto en los JSONs de historial actuales.
2.  **Reglas de Comportamiento:** Guardar "patrones confirmados" en un archivo JSON (ej: si Amazon se clasifica 3 veces como X, se vuelve regla).
3.  **Checkpoints de Conversación:** Párrafos cortos que resuman acuerdos previos para no cargar todo el historial.
4.  **Perfil de Preferencias (User Persona):** Definir el estilo de trabajo de Alfredo directamente en el System Prompt.
5.  **Categorización por Clusters:** Agrupar memorias por categorías contables de QBO en lugar de por proveedor.

---

## 📈 Conclusión del Plan de Acción
El proyecto puede evolucionar gradualmente. Se recomienda iniciar con la **Fase de Reglas de Comportamiento (Basada en Lógica)** para mejorar la personalización inmediata y, en una etapa futura de escala masiva, migrar hacia la **Arquitectura Vectorial con ChromaDB** para obtener una memoria semántica completa y autónoma.

---
*Este documento ha sido generado por Dexter como parte del archivo ROADMAPDOCS para consulta técnica futura.*
