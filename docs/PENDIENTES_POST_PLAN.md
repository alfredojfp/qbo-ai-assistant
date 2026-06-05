# PENDIENTES POST-PLAN — Items diferidos (5-Jun-2026)

Documento vivo con items que quedaron fuera del plan principal de debug (49 bugs + 11 refactors) por decisión explícita del usuario, prioridad baja, o dependencia externa.

---

## ⏳ Refactors diferidos (Iter 5)

### R-3 — Refactor `procesar_reconciliacion_bancaria` a batch engine

**Estado:** ⏳ CANCELADO a pedido del usuario (5-Jun-2026).

**Descripción original:**
Refactorizar `procesar_reconciliacion_bancaria` (`main.py:2490-2700` aprox) para usar el nuevo batch engine (`dexter/core/batch/`), pasando de 3 niveles de indirección a 2 (similar a R-4 con `process_deposits_csv`).

**Razón de cancelación:**
Usuario explícitamente instruyó "No no lo aplicaremos" durante la sesión de cierre del plan. La función actual funciona correctamente tras:
- HIGH-5 (hoist del vendor lookup, commit `78658e3`) — eliminó N+1 query
- MED-11 (commit `f3e9546`) — fix de return `Decimal` accidental

No hay evidencia de bugs en producción ni tests fallidos relacionados.

**Impacto:** Ninguno en funcionalidad. Era nice-to-have de consistencia arquitectónica, no fix funcional.

**Prioridad:** Baja. Solo retomar si en el futuro se quiere uniformidad con `tool_depositar_lote_csv` (R-4).

**Pasos para retomar (si en el futuro):**
1. Analizar `procesar_reconciliacion_bancaria` actual y mapear operaciones a `dexter/core/batch/deposits.py`
2. TDD: extraer casos de test de `tests/test_high5_*.py` → `tests/test_r3_recon_batch.py`
3. Crear `tool_reconciliar_lote_csv` en `dexter/tools/reconciliation.py` (similar a `tool_depositar_lote_csv` de R-4)
4. Refactorizar `procesar_reconciliacion_bancaria` a llamar `tool_reconciliar_lote_csv` directo (3 niveles → 2)
5. Mantener `procesar_reconciliacion_bancaria` como shim de backward compat (1 línea: `return tool_reconciliar_lote_csv(...)`)
6. Verificar 635/635 tests + suite E2E live
7. Commit atómico con prefijo `refactor(r-3): ...`

**Estimación:** 2-3 horas (plantilla R-4 probada, baja incertidumbre).

---

## ⏳ Bug follow-ups

### HIGH-5b — Rollback en reconciliación
**Estado:** ⏳ Pendiente (mencionado en Iter 2 tabla).
**Descripción:** Si un paso de la reconciliación falla a mitad, no hay rollback automático.
**Impacto:** Bajo (la reconciliación es normalmente read-only o crea transacciones idempotentes).
**Prioridad:** Media — implementar si se observa fallo real en sandbox/producción.

### MED-10b — Extender validación `line_items` a 6+ `create_*` tools
**Estado:** ⏳ Pendiente (mencionado en Iter 3 tabla).
**Descripción:** MED-10 validó `line_items` solo en `create_invoice`. Falta extender a `create_bill`, `create_estimate`, `create_salesreceipt`, `create_purchase`, `create_creditmemo`, `create_refundreceipt`, `create_vendorcredit`.
**Impacto:** Bajo (cada tool ya tiene sus propias validaciones parciales).
**Prioridad:** Baja — cubrir si se observa fallo real con `line_items=[]` en estos tools.

---

## 🔐 Seguridad

### Rotación de credenciales sandbox
**Estado:** ⚠️ RECOMENDADO
**Descripción:** Las credenciales del sandbox QBO (Client ID + Secret) fueron expuestas en el chat durante la sesión de debugging. Aunque son credenciales de SANDBOX (no producción), es buena práctica rotarlas.
**Acción:** Ir a https://developer.intuit.com → App Settings → Regenerate Client Secret → actualizar `~/.config/dexter/CREDENTIALS`.
**Prioridad:** Alta para buenas prácticas; baja para impacto real (sandbox aislado).

---

## 📊 Métricas del plan (5-Jun-2026)

| Categoría | Total | Completado | Pendiente |
|---|---|---|---|
| 🟥 CRITICAL | 6 | 6 (100%) | 0 |
| 🟧 HIGH | 9 | 9 (100%) | 0 |
| 🟨 MEDIUM | 14 | 14 (100%) | 0 |
| 🟦 LOW | 9 | 9 (100%) | 0 |
| 🟪 Refactors | 11 | 10 (90.9%) | 1 (R-3) |
| **TOTAL** | **49** | **48 (77.6%)** | **1** |

**Tests añadidos:** 244 (391 → 635) — **+62.4%**
**main.py growth:** +696 líneas (5,294 → 5,990) — **+13.1%** (principalmente helpers testeables + safeguards)
**Commits atómicos:** 48 pusheados a `main`
**Suite E2E live:** 11/11 OK contra QBO Sandbox

---

## 🛣️ Roadmap post-plan (futuras sesiones)

1. **Sesión de validación manual** — ejecutar `python main.py` contra sandbox y correr flujos reales (no automatizados) para detectar issues que solo se ven con interacción humana.
2. **Performance audit** — perfil de cuellos de botella (e.g., `procesar_csv_bank_feed` con 1000+ filas).
3. **Documentación de usuario** — `USER_GUIDE.md` vivo basado en preguntas reales de Alfredo.
4. **Backup & restore** — script para backup de `companies/` + `chartofaccounts.json` + `savedreports.json` antes de updates.
5. **Web UI** — reemplazar `input()` loop con Streamlit/Flask (nice-to-have a largo plazo).
6. **Multi-idioma avanzado** — traducción dinámica de respuestas del LLM (no solo keywords).
