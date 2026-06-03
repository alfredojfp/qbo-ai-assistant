# Spec: Organización y Documentación Integral — QuickBooks AI Assistant

**Fecha:** 2026-06-03
**Autor:** Proceso de brainstorming con Dexter
**Estado:** Diseño aprobado por el usuario — pendiente de revisión
**Versión del proyecto (al momento de la spec):** 3.5 (Dexter)
**Versión actual del proyecto:** 3.7.0 — ver [`../CHANGELOG.md`](../CHANGELOG.md) para el historial completo y las novedades de v3.6 y v3.7.
**Alcance:** Documentación y estructura. NO modifica código.

---

## 🎯 Objetivo

Convertir el proyecto QuickBooks AI Assistant (TMP AI / Dexter) en un repositorio autoexplicativo y bien organizado, mediante:

1. Un **README raíz** que sirva como hub principal y punto de entrada único para audiencias mixtas (desarrolladores + contadores).
2. **Sincronización a v3.5** de toda la documentación existente, eliminando contradicciones de versiones.
3. **Documentos especializados nuevos** que cubran vacíos actuales (arquitectura, catálogo de capacidades, multi-empresa, changelog, instalación, guía de usuario).
4. **Reorganización menor** de la estructura de carpetas (consolidar `ROADMAPDOCS/` dentro de `docs/`).

---

## 📐 Decisiones de diseño acordadas

| Decisión | Valor | Justificación |
|----------|-------|---------------|
| **Alcance** | Completo (organizar + sincronizar + crear) | Usuario eligió la opción más comprehensiva |
| **Audiencia** | Mixta (dev + contador) en un solo README con índice | Maximiza utilidad sin fragmentar |
| **Idioma** | Español únicamente | Consistencia con docs existentes |
| **Enfoque de organización** | Híbrido (mantener `docs/` + integrar `ROADMAPDOCS/`) | Mínima disruption, máxima claridad |
| **Modificación de código** | NO | Documentación pura |
| **Commit** | NO automático | Política: solo con confirmación explícita |

---

## 🗂️ Estructura de archivos — Antes vs. Después

### Estado actual (resumido)

```
Qbo Scripts/
├── README.md                    ❌ NO EXISTE
├── docs/
│   ├── README.md                (v1.0.0 desactualizado)
│   ├── CONTEXT.md               (v3.5)
│   ├── EXAMPLES.md              (¿v?)
│   ├── TROUBLESHOOTING.md
│   ├── MANUAL_USUARIO.md
│   └── requirements.txt
├── ROADMAPDOCS/                 (disperso en raíz)
│   ├── ROADMAP.md
│   ├── DEVELOPMENT_LOG.md
│   ├── MEMORIA_Y_ARQUITECTURA.md
│   ├── MATCHING_ENGINE_BANK_FEED.md
│   ├── ANALISIS_FINANCIERO_PRO.md
│   └── TODO.TEXT
├── main.py, company_manager.py, ocr_bills.py, install.sh, gitmanager.py
├── autonomia/  (6 módulos)
├── scripts/   (verify_setup.py, refresh_token.py)
├── Bank Reconciliation/, Pending bills/, Processed bills/, Backup/
└── outputs/, templates/, Test/
```

### Estado objetivo

```
Qbo Scripts/
├── README.md                          🆕 Hub principal (~600-700 líneas)
├── docs/
│   ├── README.md                      ♻️ Sincronizado a v3.5 + índice
│   ├── CONTEXT.md                     ♻️ Sincronizado
│   ├── EXAMPLES.md                    ♻️ Sincronizado
│   ├── TROUBLESHOOTING.md             ♻️ Sincronizado + sección multi-empresa
│   ├── USER_GUIDE.md                  🆕 Refactor de MANUAL_USUARIO.md
│   ├── ARCHITECTURE.md                🆕 Diagramas y dataflow
│   ├── CAPACIDADES.md                 🆕 Catálogo de tools y módulos
│   ├── MULTI_EMPRESA.md               🆕 Guía específica v3.5
│   ├── CHANGELOG.md                   🆕 Historial versionado
│   ├── INSTALL.md                     🆕 Guía detallada de instalación
│   ├── requirements.txt
│   ├── roadmap/                       🆕 Antes ROADMAPDOCS/
│   │   ├── ROADMAP.md                 📦 Movido
│   │   ├── DEVELOPMENT_LOG.md         📦 Movido
│   │   ├── MEMORIA_Y_ARQUITECTURA.md  📦 Movido
│   │   ├── MATCHING_ENGINE_BANK_FEED.md  📦 Movido
│   │   ├── ANALISIS_FINANCIERO_PRO.md 📦 Movido
│   │   └── TODO.TEXT                  📦 Movido
│   └── superpowers/
│       └── specs/
│           └── 2026-06-03-documentacion-organizacion-design.md  ← este spec
├── main.py, company_manager.py, ocr_bills.py, install.sh, gitmanager.py
├── autonomia/  (sin cambios)
├── scripts/   (sin cambios)
├── Bank Reconciliation/, Pending bills/, Processed bills/, Backup/  (sin cambios)
└── outputs/, templates/, Test/  (sin cambios)
```

**Leyenda:**
- 🆕 = archivo nuevo
- ♻️ = actualizado/sincronizado
- 📦 = movido de ubicación

---

## 📄 README.md raíz — Esquema de contenido

| # | Sección | Audiencia | Líneas aprox. |
|---|---------|-----------|---------------|
| 1 | TL;DR + Badges | Ambos | 15-20 |
| 2 | 🚀 Características Principales (8 capacidades) | Ambos | 30-40 |
| 3 | 📸 Ejemplo de uso rápido (1-2 ejemplos) | Contador | 25-35 |
| 4 | 🏗️ Arquitectura (resumen + diagrama) | Dev | 40-50 |
| 5 | ⚙️ Stack Tecnológico (tabla) | Dev | 30-40 |
| 6 | 🚀 Instalación Rápida (6 pasos) | Dev | 40-50 |
| 7 | 🎯 Uso Básico + Comandos (5 ejemplos + comandos rápidos) | Ambos | 60-80 |
| 8 | 🔧 Catálogo de Capacidades (resumen 31+ tools + 6 módulos) | Dev | 50-70 |
| 9 | 🏢 Multi-Empresa v3.5 (quick guide) | Ambos | 30-40 |
| 10 | 📊 Optimización y Costos (tabla) | Dev | 30-40 |
| 11 | 🔒 Seguridad + Troubleshooting (resumen) | Dev | 25-35 |
| 12 | 🗺️ Roadmap + Contribución | Ambos | 30-40 |
| Anexo A | 📚 Índice de Documentación (tabla) | Ambos | 25-35 |
| Anexo B | 🏢 Empresas / Casos de Uso | Ambos | 15-25 |
| Anexo C | 📄 Licencia + Créditos | Ambos | 10-15 |

**Total estimado:** 500-700 líneas.

**Reglas:**
- ✅ Tabla de contenidos con anchors al inicio
- ✅ Badges: versión, Python, license, status, OpenRouter, QBO API
- ✅ Emojis consistentes
- ✅ Ejemplos en bloques de código
- ✅ Links relativos a `docs/*` para detalles
- ❌ NO duplica contenido de otros docs (los enlaza)
- ❌ NO incluye valoración económica (esa sección se mueve a un doc interno, fuera de la documentación pública)

---

## 📚 Documentos nuevos — Contenido

### 1. `docs/ARCHITECTURE.md` (~400 líneas)
**Audiencia:** Desarrolladores
**Propósito:** Documento técnico de referencia para entender el código.

**Secciones:**
- Diagrama ASCII completo de componentes y dataflow
- Mapa de archivos del proyecto y responsabilidad de cada uno
- Flujo de una solicitud: request → context optimization → LLM → tool execution → response
- Multi-empresa: aislamiento de tokens/chart/reports/bank feed
- Optimización de tokens: `get_relevant_tools`, `build_conversation_context`, `necesita_chart`
- Patrones de diseño: sliding window, dynamic system prompt, fuzzy matching, learning loop
- Estructura de carpetas `companies/<nombre>/` y `meta.json`

### 2. `docs/CAPACIDADES.md` (~500 líneas)
**Audiencia:** Desarrolladores y usuarios avanzados
**Propósito:** Catálogo exhaustivo de todas las herramientas y módulos.

**Secciones:**
- **31+ Function Tools** en 2 tablas (Básicas 13 + Autonomía 18)
- **6 Módulos de Autonomía** con descripción
- **OCR de Bills** — flujo paso a paso
- **Bank Feed Intelligence** — algoritmos de clasificación
- **User Behavior Learning** — qué aprende y cómo
- **Dynamic Report Generator** — lenguaje natural → queries
- Ejemplos "input → output" para cada categoría
- Tabla resumen "Tool → Categoría → Costo aprox."

### 3. `docs/MULTI_EMPRESA.md` (~200 líneas)
**Audiencia:** Usuarios y desarrolladores
**Propósito:** Guía específica de la feature v3.5.

**Secciones:**
- Concepto de `meta.json` por empresa
- Hot-swap sin reiniciar
- Diagrama de flujo de cambio de empresa
- Aislamiento de tokens, chart, reportes, bank feed
- Estructura de carpetas `companies/<nombre>/`
- Casos de uso y limitaciones
- Comandos relacionados (`gestionar_empresas`)

### 4. `docs/USER_GUIDE.md` (~350 líneas)
**Audiencia:** Contadores y usuarios finales
**Propósito:** Guía no técnica para usar el asistente.

**Secciones:**
- Bienvenida y "qué es Dexter"
- Primeros pasos sin jerga técnica
- 10 casos de uso comentados paso a paso
- Glosario de términos (anticipo, prepago, retainer, etc.)
- FAQ expandido
- Cuándo escalar al desarrollador
- Cambios vs versión anterior (changelog usuario)

### 5. `docs/CHANGELOG.md` (~150 líneas)
**Audiencia:** Todos
**Propósito:** Historial versionado.

**Secciones:**
- v3.5 (actual) — Multi-Empresa, Dexter, gestión de tokens aislada
- v3.0 — Optimización 57%, 6 módulos autonomía, OCR
- v2.0 — DeepSeek V3, function calling, 18 tools
- v1.0 — MVP inicial
- Formato Keep a Changelog
- Notas de migración entre versiones

### 6. `docs/INSTALL.md` (~150 líneas)
**Audiencia:** Desarrolladores
**Propósito:** Instalación detallada.

**Secciones:**
- Prerrequisitos (Python 3.9+, QBO sandbox, OpenRouter key, Gemini key)
- Pasos con comandos exactos (multiplataforma)
- Configuración de OAuth 2.0 con QBO
- Variables de entorno documentadas
- Verificación con `scripts/verify_setup.py`
- Troubleshooting de instalación

### 7. `docs/README.md` (sincronizado a v3.5)
**Audiencia:** Todos
**Propósito:** Índice navegable.

**Cambios vs versión actual:**
- Actualizar versión de "1.0.0" a "3.5"
- Actualizar conteo de tools de "18" a "31+"
- Añadir tabla de contenidos con descripción de cada doc
- Links cruzados actualizados
- Snippet de Dexter (identidad del asistente)

---

## 🔄 Sincronización de docs existentes a v3.5

| Doc | Acción |
|-----|--------|
| `docs/CONTEXT.md` | Verificar menciones (v3.5, Dexter, 31+ tools, multi-empresa). Corregir referencias a `chartofaccounts.json` → `chart_of_accounts.json` |
| `docs/EXAMPLES.md` | Añadir 3-5 ejemplos nuevos: multi-empresa, OCR bills, Dexter salutation, dynamic report, bank feed intelligence |
| `docs/TROUBLESHOOTING.md` | Añadir sección "Problemas multi-empresa" + verificación de tokens aislados |
| `docs/USER_GUIDE.md` (refactor de MANUAL_USUARIO.md) | Reestructurar como guía de usuario completa (ver Sección 3) |
| `docs/roadmap/*` (movidos) | Sin cambios de contenido, solo ubicación |

---

## 🐛 Inconsistencias detectadas que se corregirán

| # | Inconsistencia | Corrección |
|---|----------------|-----------|
| 1 | `docs/README.md` dice "v1.0.0" y "18 tools" | Reescrito a "v3.5" y "31+ tools" |
| 2 | Nombre `chart_of_accounts.json` vs `chartofaccounts.json` | Unificar a `chart_of_accounts.json` (snake_case) en todos los docs |
| 3 | `MANUAL_USUARIO.md` solo en español sin estandarizar nombre | Renombrar a `USER_GUIDE.md` (convención inglesa clara) |
| 4 | `docs/EXAMPLES.md` probablemente desactualizado | Revisar y sincronizar |
| 5 | Falta CHANGELOG | Crear |
| 6 | `ROADMAPDOCS/` disperso en raíz | Mover a `docs/roadmap/` |
| 7 | Modificaciones sin commit en `ROADMAPDOCS/*` y otros archivos | Capturar contenido actual y aplicar movimiento (no `git mv` para uncommitted) |
| 8 | `gitmanager.py` aparece en raíz pero no está documentado | Mencionar en ARCHITECTURE.md como utilidad de versionado |
| 9 | Falta índice navegable de docs | Crear en `docs/README.md` |
| 10 | Falta guía específica multi-empresa (feature v3.5 más importante) | Crear `MULTI_EMPRESA.md` |

---

## 📋 Orden de ejecución (12 pasos)

1. Mover `ROADMAPDOCS/` → `docs/roadmap/` (preservando contenido actual en disco)
2. Renombrar `docs/MANUAL_USUARIO.md` → `docs/USER_GUIDE.md`
3. Crear `docs/CHANGELOG.md`
4. Crear `docs/INSTALL.md`
5. Crear `docs/ARCHITECTURE.md`
6. Crear `docs/CAPACIDADES.md`
7. Crear `docs/MULTI_EMPRESA.md`
8. Actualizar `docs/README.md` a v3.5 + tabla de contenidos
9. Actualizar `docs/CONTEXT.md` (sincronizar menciones)
10. Actualizar `docs/EXAMPLES.md` (añadir ejemplos nuevos)
11. Actualizar `docs/TROUBLESHOOTING.md` (añadir sección multi-empresa)
12. Crear `README.md` raíz como hub principal

---

## 🚫 Out of scope explícito

- ❌ Modificar código Python (`main.py`, `company_manager.py`, `autonomia/*`, `ocr_bills.py`)
- ❌ Modificar `install.sh`, `scripts/*`, `.env`, `.gitignore`
- ❌ Crear tests nuevos
- ❌ Hacer commit (queda a decisión del usuario)
- ❌ Eliminar el `chart_of_accounts.json` real, solo se referencia correctamente en docs
- ❌ Eliminar archivos de `Backup/`, `Bank Reconciliation/`, `Pending bills/`, `Processed bills/`, `outputs/`, `templates/`, `Test/`

---

## ✅ Criterios de éxito

1. Existe un `README.md` en la raíz que sirve como punto de entrada claro, con índice y enlaces a todos los docs.
2. Toda la documentación referencia v3.5 / Dexter de forma consistente.
3. Un nuevo desarrollador puede: instalar el proyecto, entender su arquitectura y extenderlo, solo leyendo `README.md` + `docs/ARCHITECTURE.md` + `docs/CAPACIDADES.md` + `docs/INSTALL.md`.
4. Un contador puede: entender qué hace el sistema y cómo usarlo conversacionalmente, solo leyendo `README.md` + `docs/USER_GUIDE.md` + `docs/EXAMPLES.md`.
5. La estructura de carpetas está limpia: `docs/` contiene toda la documentación, sin `ROADMAPDOCS/` en la raíz.
6. Las inconsistencias detectadas en la sección anterior están corregidas.
7. El proyecto sigue funcionando exactamente igual (no se tocó código).

---

## 📊 Métricas estimadas

- **Archivos nuevos:** 7 (más este spec)
- **Archivos actualizados:** 4
- **Archivos movidos:** 6
- **Líneas estimadas de documentación nueva total:** ~2,200-2,500 líneas
  - Cálculo: ARCHITECTURE.md (400) + CAPACIDADES.md (500) + MULTI_EMPRESA.md (200) + USER_GUIDE.md (350) + CHANGELOG.md (150) + INSTALL.md (150) + README raíz (600-700) ≈ 2,350-2,450.
- **Tiempo estimado de ejecución:** Lectura + escritura secuencial, varias llamadas a herramientas.

---

## 🔜 Siguiente paso (post-aprobación)

Invocar el skill `writing-plans` para crear el plan de implementación detallado paso a paso.

---

**Aprobación del usuario:** Pendiente de revisión del spec escrito.
