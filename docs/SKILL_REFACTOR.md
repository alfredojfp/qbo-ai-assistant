# Refactor: Sistema de Skills + Reorganización

> **Fecha:** Junio 2026 | **Versión objetivo:** v5.0.0-dev
> **Propósito:** Reducir main.py de ~7K a ~3K líneas, sistema de skills auto-descubribles, compatible con agentskills.io

---

## Motivación

main.py tiene ~7,000 líneas. Cada nuevo tool toca 3 lugares:
1. `def tool_xxx` en main.py
2. `TOOL_FUNCTIONS` dict
3. `dexter/tools/xxx.py` SCHEMA + FUNCTIONS

Esto causó 2 errores hoy (docstring roto, params incorrectos). La raíz: el monolito.

---

## Arquitectura Objetivo

```
dexter/
├── main.py                    ← ~3K líneas (core loop, call_llm, auth, QBO client)
├── prompt.py                  ← SYSTEM_PROMPT extraído
├── core/                      ← API helpers, retry, safe_json, memory, console
├── skills/                    ← ⭐ NUEVO: sistema de skills
│   ├── search/
│   │   ├── SKILL.md           ← metadata: nombre, descripción, keywords, ejemplos
│   │   └── __init__.py        ← SCHEMA + FUNCTIONS (auto-descubiertos)
│   ├── transactions/
│   ├── reports/
│   ├── ocr/
│   ├── amortizacion/          ← skill nueva
│   │   ├── SKILL.md
│   │   └── __init__.py
│   └── admin/
├── tools/                     ← ⭐ refactorizado (wrapper → skills/)
│   ├── __init__.py            ← auto-descubre skills/
│   └── _schema_utils.py       ← helpers
├── testing/
├── error_log.py
└── console.py
```

---

## Fases de Implementación

### Fase 1: Extraer prompt + crear skill de amortización (~20 min)
- `dexter/prompt.py` ← `SYSTEM_PROMPT` completo
- `dexter/skills/amortizacion/__init__.py` ← `calcular_distribucion`, `ejecutar_distribucion` (prototipo del nuevo sistema)
- main.py: quitar SYSTEM_PROMPT + tools de amortización, importar de los nuevos lugares

### Fase 2: Migrar tools existentes a skills (~60 min)
- Cada módulo de `dexter/tools/` → `dexter/skills/{nombre}/`
- Agregar `SKILL.md` a cada skill con metadata
- `dexter/skills/__init__.py` auto-descubre skills del directorio
- main.py: TOOL_FUNCTIONS ya no se mantiene manual (auto-descubierto)

### Fase 3: Limpiar main.py + código legacy (~30 min)
- Eliminar TOOL_FUNCTIONS dict manual
- Eliminar tool wrappers redundantes
- Simplificar `get_relevant_tools()` para usar auto-descubrimiento
- Verificar 692 tests pasan

---

## Principios de No-Ruptura

1. **0 líneas removidas del comportamiento externo.** Toda función `tool_xxx` debe seguir importable desde `from main import tool_xxx`
2. **Shims en main.py** por 1 release. Después se deprecan.
3. **Tests: 692/692 deben pasar** en cada fase.
4. **Integridad del registry:** `verify_tool_integrity` sigue funcionando.
5. **Commits atómicos** por fase.

---

## Lo que NO cambia

- API de QBO (qbo_request, qbo_query)
- LLM call (call_llm)
- Sistema de memoria, perfil, bank feed
- Tests existentes
- run_dexter.sh
- Documentación
