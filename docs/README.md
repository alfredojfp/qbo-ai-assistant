# 📚 Documentación de QuickBooks AI Assistant (Dexter)

Bienvenido a la documentación de **Dexter**, tu asistente de IA para QuickBooks Online.

> **Versión:** 3.7.0
> **Identidad del asistente:** Dexter
> **Total de function tools:** 32 (13 básicas + 18 autonomía + 1 multi-empresa)
> **Módulos de autonomía:** 6

---

## 📑 Índice de documentos

| Documento | Para quién | Descripción |
|-----------|-----------|-------------|
| 📄 [**README.md**](../README.md) (raíz) | Todos | Hub principal del proyecto, índice rápido |
| 📘 [**USER_GUIDE.md**](USER_GUIDE.md) | Usuarios / Contadores | Cómo usar Dexter paso a paso, sin jerga técnica |
| 📗 [**EXAMPLES.md**](EXAMPLES.md) | Todos | 10+ ejemplos reales de conversaciones con Dexter |
| 📕 [**TROUBLESHOOTING.md**](TROUBLESHOOTING.md) | Todos | Solución de problemas comunes |
| 📙 [**CONTEXT.md**](CONTEXT.md) | Desarrolladores / LLMs | Contexto completo del proyecto (32 KB) |
| 🏗️ [**ARCHITECTURE.md**](ARCHITECTURE.md) | Desarrolladores | Diagramas, dataflow, patrones de diseño |
| 🔧 [**CAPACIDADES.md**](CAPACIDADES.md) | Desarrolladores | Catálogo de los 32 tools y 6 módulos de autonomía |
| 🏢 [**MULTI_EMPRESA.md**](MULTI_EMPRESA.md) | Todos | Guía específica de la feature v3.5 multi-empresa |
| 🚀 [**INSTALL.md**](INSTALL.md) | Desarrolladores | Instalación detallada paso a paso |
| 📜 [**CHANGELOG.md**](CHANGELOG.md) | Todos | Historial versionado v1.0 → v3.5 |
| 🗺️ [**roadmap/**](roadmap/) | Todos | Roadmap y documentos estratégicos |

---

## 🚀 Inicio rápido

1. **Nuevo usuario (contador):** Lee [`USER_GUIDE.md`](USER_GUIDE.md)
2. **Nuevo desarrollador:** Lee [`../README.md`](../README.md) → [`INSTALL.md`](INSTALL.md) → [`ARCHITECTURE.md`](ARCHITECTURE.md)
3. **Quieres ver qué puede hacer:** Lee [`EXAMPLES.md`](EXAMPLES.md) → [`CAPACIDADES.md`](CAPACIDADES.md)
4. **Tienes un problema:** Revisa [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
5. **Quieres entender la historia:** Lee [`CHANGELOG.md`](CHANGELOG.md) → [`roadmap/ROADMAP.md`](roadmap/ROADMAP.md)

---

## 🆕 Novedades v3.5 (Multi-Empresa PRO)

- **Multi-empresa** con tokens aislados por empresa
- **Cambio en caliente** sin reiniciar la app
- **Identidad "Dexter"** (antes "Asistente TMP AI")
- **32 function tools** (1 nuevo: `gestionar_empresas`)
- Persistencia por empresa en `companies/<nombre>/meta.json`

Ver [`MULTI_EMPRESA.md`](MULTI_EMPRESA.md) para detalles completos.

---

## 🏗️ Estructura del proyecto

```
Qbo Scripts/
├── README.md                 ← Hub principal
├── docs/                     ← Estás aquí
│   ├── README.md             ← Este archivo (índice)
│   ├── USER_GUIDE.md
│   ├── EXAMPLES.md
│   ├── TROUBLESHOOTING.md
│   ├── CONTEXT.md
│   ├── ARCHITECTURE.md
│   ├── CAPACIDADES.md
│   ├── MULTI_EMPRESA.md
│   ├── INSTALL.md
│   ├── CHANGELOG.md
│   ├── requirements.txt
│   ├── roadmap/              ← Roadmap y docs estratégicos
│   └── superpowers/
│       └── specs/            ← Specs de diseño
├── main.py                   ← Aplicación principal
├── company_manager.py        ← Multi-empresa (v3.5)
├── ocr_bills.py              ← OCR de facturas
├── gitmanager.py             ← Utilidad de versionado
├── install.sh                ← Instalación automatizada
├── autonomia/                ← 6 módulos de autonomía
├── scripts/                  ← Scripts auxiliares
├── Pending bills/            ← PDFs a procesar (OCR)
├── Processed bills/          ← PDFs ya procesados
├── Bank Reconciliation/      ← CSVs de reconciliación
├── Backup/                   ← Respaldos
├── outputs/                  ← Archivos generados
├── templates/                ← Plantillas
└── Test/                     ← Pruebas
```

---

## 🔗 Recursos externos

- [QuickBooks Online API v3](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)
- [OpenRouter](https://openrouter.ai/docs) (DeepSeek V3)
- [Google Gemini](https://ai.google.dev/docs) (OCR)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Mantenedor:** Alfredo
**Asistente:** Dexter
**Última actualización de este índice:** 2026-06-03
