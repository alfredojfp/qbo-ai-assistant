# DEBUG RUNBOOK — Dexter QBO Assistant

**Propósito:** Documento vivo con el plan de debug exhaustivo, progreso por iteración, tests agregados y commits generados.

**Última actualización:** Iteración 1 (CRITICAL) en progreso

---

## 🎯 Objetivo

Resolver **47 bugs** identificados en auditoría estática (4-Jun-2026) en `main.py`, `dexter/tools/`, `dexter/core/`, y `autonomia/`, para que el usuario pueda usar Dexter en producción sin crashes, data corruption ni bugs latentes.

**Metodología:** TDD estricto (RED→GREEN→REFACTOR) + 1 commit atómico por bug + suite E2E con QBO Sandbox.

---

## 📊 Resumen Ejecutivo

| Iteración | Severidad | # Bugs | Estado | Commits | Tests añadidos |
|---|---|---|---|---|---|
| **Iter 1** | 🟥 CRITICAL | 6 | ✅ **COMPLETADO** | 6/6 | 32 |
| Iter 2 | 🟧 HIGH | 8 | ⏳ Pendiente | 0/8 | 0 |
| Iter 3 | 🟨 MEDIUM | 14 | ⏳ Pendiente | 0/14 | 0 |
| Iter 4 | 🟦 LOW | 9 | ⏳ Pendiente | 0/9 | 0 |
| Iter 5 | 🟪 Refactors | 11 | ⏳ Pendiente | 0/11 | 0 |
| **TOTAL** | | **48** | | **6/48** | **32** |

---

## 🟥 ITERACIÓN 1 — CRITICAL ✅ COMPLETADO

**Objetivo:** Eliminar crashes y data loss. ✅ Logrado.
**Tests añadidos:** 32 (de 359 → 391).
**Commits:** 6 atómicos (5cfd727, a0c180f, 9a8145d, 644faaa, c57dc6c, 1c6840e).
**Resultado:** 391/391 tests passing, safeguard OK.

### CRIT-1: `qbo_request()` sin timeout → hang indefinido ✅
- **Commit:** `5cfd727 fix(crit-1): add timeout=30 + retry on Timeout/ConnectionError in qbo_request`
- **Tests:** 4 (`test_get_request_uses_timeout`, `test_post_request_uses_timeout`, `test_timeout_raises_within_bounded_time`, `test_connection_error_raises`)
- **Resultado:** 4/4 GREEN

### CRIT-2: `conversation_history` unbounded → OOM en sesión larga ✅
- **Commit:** `a0c180f fix(crit-2): cap conversation_history to 200 entries to prevent OOM`
- **Tests:** 3 (`test_conversation_history_is_bounded_deque`, `test_append_beyond_maxlen_drops_oldest`, `test_slice_in_call_llm_works_with_deque`)
- **Resultado:** 3/3 GREEN
- **Adaptación:** `call_llm` actualizado a `list(conversation_history)[-N:]` (deque no soporta slicing)

### CRIT-5: `json.dumps` falla con Decimal/datetime → error genérico al LLM ✅
- **Commit:** `9a8145d fix(crit-5): safe_dumps with custom JSONEncoder for Decimal/datetime/Path`
- **Tests:** 10 (`test_serializes_decimal_as_float`, `test_serializes_datetime_as_isoformat`, `test_serializes_date_as_isoformat`, `test_serializes_path_as_str`, `test_serializes_uuid_as_str`, `test_serializes_set_as_list`, `test_nested_structures`, `test_ensure_ascii_false_preserves_unicode`, `test_falls_back_to_str_for_unknown_types`, `test_dispatch_handles_decimal_return`)
- **Resultado:** 10/10 GREEN
- **Nuevo archivo:** `dexter/core/safe_json.py`

### CRIT-4: Token refresh solo en 401 → silent failure en 429/503 ✅
- **Commit:** `644faaa fix(crit-4): retry on 429/503/Timeout with exponential backoff in qbo_request`
- **Tests:** 5 (`test_429_triggers_retry_and_succeeds`, `test_503_triggers_retry_and_succeeds`, `test_429_after_max_retries_returns_last`, `test_backoff_is_exponential`, `test_400_does_not_retry`)
- **Resultado:** 5/5 GREEN
- **Nuevo archivo:** `dexter/core/retry.py` (refactoriza retry manual de CRIT-1)

### CRIT-3: State global no se limpia al cambiar empresa → data leak ✅
- **Commit:** `c57dc6c fix(crit-3): reset session state on company switch (prevent data leak)`
- **Tests:** 6 (`test_reset_clears_conversation_history`, `test_reset_clears_last_search_results`, `test_reset_preserves_token_counters`, `test_reset_preserves_operations_counters`, `test_cambiar_calls_reset_session_state`, `test_cambiar_actually_clears_state`)
- **Resultado:** 6/6 GREEN
- **Nueva función:** `reset_session_state()` invocada desde `tool_gestionar_empresas("cambiar")`

### CRIT-6: `tool_cdc_query` payload incorrecto → siempre 4xx ✅
- **Commit:** `1c6840e fix(crit-6): reshape cdc_query payload to QBO CDC schema`
- **Tests:** 4 (`test_cdc_query_sends_tracked_entities_wrapper`, `test_cdc_query_entities_have_name_key`, `test_cdc_query_last_modified_preserved`, `test_cdc_query_endpoint_is_cdc`)
- **Resultado:** 4/4 GREEN

---

## 🟧 ITERACIÓN 2 — HIGH (pendiente)

| ID | Bug | File | Estado |
|---|---|---|---|
| HIGH-1 | `ZeroDivisionError` si `quantity=0` en 7 tools create_* | `main.py:683,1966,1057,1103,1139,1216,1253` | ⏳ |
| HIGH-2 | `update_transaction` mezcla `sparse` body/URL param | `qbo_client.py:135, main.py:1367` | ⏳ |
| HIGH-3 | `void_transaction` sobreescribe `PrivateNote` | `main.py:1397-1409` | ⏳ |
| HIGH-4 | `process_deposits_csv` crea real QBO sin rollback | `main.py:2232-2293` | ⏳ |
| HIGH-5 | `procesar_reconciliacion_bancaria` N+1 query + partial writes | `main.py:2569-2723` | ⏳ |
| HIGH-6 | `upload_attachment` bypassa `qbo_request` | `main.py:1880-1934` | ⏳ |
| HIGH-7 | `find_bank_account_id(category="BANK")` siempre retorna "" | `qbo_client.py:269, main.py:410` | ⏳ |
| HIGH-8 | `qbo_query` no pagina > 1000 | `main.py:312-319` | ⏳ |
| HIGH-9 | `create_*` no idempotente (18 tools) | `main.py:722-2092` | ⏳ |
| HIGH-10 | `manage_empresas` no limpia `last_search_results` | `main.py:4358-4392` | ⏳ (parte de CRIT-3) |

---

## 🟨 ITERACIÓN 3 — MEDIUM (pendiente)

| ID | Bug | File |
|---|---|---|
| MED-1 | `QB_BASE_URL` con `None` si env var missing | `main.py:98` |
| MED-2 | `parse_date` silenciosamente usa "today" en formato inválido | `main.py:176-200` |
| MED-3 | `save_session_to_csv` sin lock | `main.py:451-479` |
| MED-4 | `update_env_file` no atómico | `main.py:154-174` |
| MED-5 | `find_account` usa `acc["name"]` sin None guard | `main.py:414-425` |
| MED-6 | `_fetch_report` no resume → trunca en LLM | `main.py:1463-1663` |
| MED-7 | `execute_batch` no valida schema | `main.py:1821-1833` |
| MED-8 | `procesar_csv_bank_feed` mezcla prints y returns | `main.py:2502-2551` |
| MED-9 | `gestionar_empresas` switch no fuerza refresh chart | `main.py:4386` |
| MED-10 | `create_*` no valida `lineas=[]` | `main.py:665-720` |
| MED-11 | 5+ tools retornan Decimal accidentalmente | varios |
| MED-12 | Race condition mid-tool-call en company switch | `main.py:4376, 271-272` |
| MED-13 | `recent_hist` pasa tool results gigantes | `main.py:2754, 5054-5064` |
| MED-14 | `procesar_lote_bills` filtra absolute path | `main.py:4761-4768` |

---

## 🟦 ITERACIÓN 4 — LOW (pendiente)

| ID | Bug | File |
|---|---|---|
| LOW-1 | 18+ `create_*` duplican boilerplate | `main.py:665-2092` |
| LOW-2 | Token usage no se guarda en Ctrl+C | `main.py:434-446` |
| LOW-3 | `process_quick_command` matching sin word boundaries | `main.py:4921-5018` |
| LOW-4 | `load_chart_of_accounts` cache sin schema_version | `main.py:323-383` |
| LOW-5 | `EntityRef` con `name` que QBO rechaza | `main.py:2432-2440` |
| LOW-6 | `get_relevant_tools` keywords solo español | `main.py:5036-5043` |
| LOW-7 | Internal `generate_pl_report` retorna DataFrame | `main.py:2096-2147` |
| LOW-8 | `tool_execute_python` exec() sin sandbox | `autonomia/.../code_executor.py:15` |
| LOW-9 | `extract_realm_id` acepta cualquier 10+ dígitos | `company_manager.py:26-28` |

---

## 🟪 ITERACIÓN 5 — Refactors Estructurales (pendiente)

| Refactor | Descripción |
|---|---|
| R-1 | `tests/test_e2e_sandbox.py` suite con flows reales |
| R-2 | `dexter/core/api_helpers.py` con `post_entity`, `get_entity`, `query_with_pagination` |
| R-3 | Refactor `procesar_reconciliacion_bancaria` a usar batch engine |
| R-4 | Refactor `process_deposits_csv` a delegar a `tool_depositar_lote_csv` |
| R-5 | `ConversationHistory` class con `deque(maxlen=N)` |
| R-6 | `dexter/core/retry.py` con `@retry_on_qbo_error` decorator |
| R-7 | `dexter/core/safe_json.py` con `safe_dumps(obj)` |
| R-8 | `SessionState` class en lugar de globals |
| R-9 | Tests parametrizados para 18 `create_*` tools |
| R-10 | Mock LLM con deepseek para tests de conversación |
| R-11 | CI workflow `.github/workflows/test.yml` |

---

## 🧪 SUITE E2E CON SANDBOX (Iter 5, R-1)

Pendiente para Iteración 5. Cubre:
- Flujo completo cliente→invoice
- Batch deposits con rollback
- Loop conversacional con tool calls
- Switch de empresa limpia state
- Token expiry mid-batch
- QBO 5xx retry con backoff
- 429 rate limit handling

---

## 📁 Entregables (acumulativo)

- **48 commits atómicos** esperados
- **`docs/DEBUG_RUNBOOK.md`** (este archivo)
- **`dexter/core/api_helpers.py`** (R-2)
- **`dexter/core/retry.py`** (R-6)
- **`dexter/core/safe_json.py`** (R-7)
- **`dexter/core/session_state.py`** (R-8)
- **`tests/test_e2e_sandbox.py`** (R-1)
- **`.github/workflows/test.yml`** (R-11)
- **CHANGELOG.md** actualizado con cada fix

---

## 📈 Métricas

### Antes del plan (baseline)
- **Tests:** 359/359 pasando
- **main.py:** 5,294 líneas
- **dexter/tools/:** 23 archivos, 100 tools
- **Bugs conocidos:** 0 documentados

### Iter 1 (CRITICAL) — ✅ COMPLETADO
- **Tests:** 391/391 pasando (+32 nuevos)
- **Líneas añadidas:** ~600 (código + tests)
- **Commits:** 6 atómicos
- **Nuevos archivos:**
  - `dexter/core/safe_json.py` (DexterJSONEncoder, safe_dumps)
  - `dexter/core/retry.py` (retry_request con exp backoff)
  - `tests/test_crit1_timeout.py` (4 tests)
  - `tests/test_crit2_history.py` (3 tests)
  - `tests/test_crit3_company_switch.py` (6 tests)
  - `tests/test_crit4_retry.py` (5 tests)
  - `tests/test_crit5_safe_json.py` (10 tests)
  - `tests/test_crit6_cdc.py` (4 tests)
- **Funciones nuevas:**
  - `qbo_request()` con timeout=30
  - `_calculate_backoff()` y `retry_request()` en `dexter/core/retry.py`
  - `DexterJSONEncoder` y `safe_dumps()` en `dexter/core/safe_json.py`
  - `reset_session_state()` en main.py

---

## 🔄 Historial de Cambios

| Fecha | Iteración | Acción |
|---|---|---|
| 2026-06-04 | Pre-plan | Auditoría estática identificó 47 bugs |
| 2026-06-04 | Iter 1 | CRIT-1 → CRIT-2 → CRIT-5 → CRIT-4 → CRIT-3 → CRIT-6 ✅ |
| 2026-06-04 | Iter 1 | 391 tests passing, 6 commits atómicos |
