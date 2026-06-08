# Análisis de Tools — main.py

> ⚠️ **DOCUMENTO HISTÓRICO (Superseded).** Este análisis cubría el estado de `main.py` ANTES del refactor modular (Fases 0-7, 2026-06-04). Para el estado actual ver:
> - **Catálogo actual:** [`dexter/tools/README.md`](../dexter/tools/README.md) — 43 tools en 14 módulos
> - **Cambios:** [`CHANGELOG.md`](CHANGELOG.md) — entrada Unreleased 2026-06-04
> - **Arquitectura:** [`ARCHITECTURE.md`](ARCHITECTURE.md) — diagrama v4.0

---

> Estado del monolito `main.py` (3,063 líneas) en la rama `main`,
> basado en lectura directa del código. La numeración agrupa
> por categoría funcional, no por orden de definición.

## Inventario actual

`main.py` expone 21 tools a la API de function-calling de OpenAI
más 2 tools nuevos añadidos en v4.0:

| # | Tool | Categoría | Línea |
|---|------|-----------|-------|
| 1 | `buscar_cliente` | Buscar | 2327 |
| 2 | `buscar_vendor` | Buscar | 2339 |
| 3 | `buscar_cuenta` | Buscar | 2349 |
| 4 | `buscar_item` | Buscar | 2367 |
| 5 | `crear_invoice` | Crear | 2376 |
| 6 | `crear_bill` | Crear | 2380 |
| 7 | `crear_deposito` | Crear | 2385 |
| 8 | `crear_pago` | Crear | 2389 |
| 9 | `generar_reporte_pl` | Reporte | 2394 |
| 10 | `generar_balance_sheet` | Reporte | 2412 |
| 11 | `guardar_reporte` | Reporte | 2429 |
| 12 | `cargar_reporte` | Reporte | 2434 |
| 13 | `listar_reportes_guardados` | Reporte | 2443 |
| 14 | `procesar_csv_depositos` | Batch | 2456 |
| 15 | `crear_template_csv` | Batch | 2460 |
| 16 | `obtener_estadisticas_tokens` | Métrica | 2465 |
| 17 | `generar_informe_tokens` | Métrica | 2479 |
| 18 | `refrescar_chart_accounts` | Utilidad | 2484 |
| 19 | `gestionar_empresas` | Multi-empresa | 2495 |
| 20 | `procesar_bank_feed_csv` | Bank feed | 2558 |
| 21 | `procesar_reconciliacion_bancaria` | Reconciliación | 2562 |
| 22 | `taggear_reconciliacion` *(nuevo)* | BNK-RECON | 2567 |
| 23 | `limpiar_tags_reconciliacion` *(nuevo)* | BNK-RECON | — |
| 24 | `procesar_lote_bills` | OCR | 2652 |

(El tool #1 en `autonomia/` agrega otros 30 tools de autonomía
— ver `autonomia/` para detalle.)

## Gaps identificados y estado

### 1. `procesar_csv_depositos` (línea 2456)

**Estado actual**: Wrapper sobre `process_deposits_csv` legacy.
Sin persistencia, sin dry-run, sin disambiguation.

**Gap**: No usa el nuevo `DepositBatchSkill` (Sprint 2).

**Solución propuesta**: Crear un nuevo tool `depositar_lote_csv`
que use `DepositBatchSkill` con todas las garantías del motor batch.
Mantener el viejo intacto por compatibilidad hacia atrás.

**Prioridad**: Media. El Sprint 1+2 ya entrega el motor; este es
el wrapper.

### 2. `obtener_estadisticas_tokens` (línea 2465)

**Estado actual**: Solo soporta `periodo="sesion"`. Otros períodos
retornan error `"Periodo 'X' no implementado todavía"`.

**Gap**: Funcionalidad incompleta — promete más de lo que entrega.

**Solución propuesta**:
- `"dia"` → leer de `data/usage_log.jsonl` filtrando por fecha
- `"mes"` → igual, agrupando por mes
- `"sesion"` → igual que ahora

**Prioridad**: Baja. No bloquea nada.

### 3. `procesar_reconciliacion_bancaria` (línea 2562)

**Estado actual**: Flujo completo de 174 líneas con balance checks,
creación de transactions (Deposit, Bill, Transfer), y validación.

**Gap**: Crea transactions nuevas sin dry-run ni confirmación
estructurada. Si el CSV está mal armado, se crean transactions
basura que hay que borrar a mano.

**Solución propuesta**: Mantener como está (es la opción "agresiva"),
pero añadir el nuevo tool `taggear_reconciliacion` (BNK-RECON)
como opción "segura" que solo taggea, no crea.

**Prioridad**: Alta. **Resuelto en v4.0** con `taggear_reconciliacion`.

### 4. `generar_informe_tokens` (línea 2479)

**Estado actual**: Escribe CSV a disco. No retorna resumen
estructurado al LLM.

**Gap**: El LLM no puede mostrar totales en chat sin re-leer el CSV.

**Solución propuesta**: Retornar también un dict con
`total_input`, `total_output`, `total_cost`, `num_sessions`.

**Prioridad**: Baja.

### 5. `procesar_lote_bills` (línea 2652)

**Estado actual**: Wrapper que ahora conecta a `procesar_lote_ocr`
real (refactor Sprint 0).

**Gap**: Ninguno funcional. Naming es inconsistente (tool dice
`procesar_lote_bills`, función interna es `procesar_lote_ocr`).

**Solución propuesta**: Renombrar función a `procesar_lote_bills`
internamente para coherencia, o documentar la diferencia.

**Prioridad**: Baja (cosmético).

### 6. `process_quick_command` (línea 2749)

**Estado actual**: Detecta 6 comandos rápidos en español/inglés
(refrescar, template, listar reportes, cambiar idioma, ayuda,
manual). NO detecta comandos batch ni BNK-RECON.

**Gap**: Si el usuario escribe "reconciliar el banco" en chat
sin pasar por el LLM, no se activa nada.

**Solución propuesta**: Añadir 2-3 triggers más:
- "reconciliar" / "recon" / "tag" → tool BNK-RECON (solo imprime guía)
- "depositar lote" / "lote csv" → tool deposits batch
- "procesar facturas" / "ocr" → tool procesar_lote_bills

**Prioridad**: Media. Mejora UX sin riesgo.

### 7. `get_relevant_tools` (línea 2807)

**Estado actual**: Filtra tools por keywords. Tiene rama
`"recon"` ya añadida en este commit.

**Gap**: No cubre las nuevas keywords batch (`"lote"`, `"batch"`).

**Solución propuesta**: Añadir rama para batch.

**Prioridad**: Media. **Parcialmente resuelto en este commit.**

### 8. `tool_gestionar_empresas` (línea 2495)

**Estado actual**: Maneja 4 acciones (listar, registrar, seleccionar,
eliminar). Tiene validación de empresa activa.

**Gap**: Cuando cambias de empresa, NO recarga el chart de cuentas
explícitamente. Lo hace implícitamente vía `load_company_context`,
pero podría haber race conditions.

**Solución propuesta**: Añadir `await refresh_chart()` después
del cambio de empresa, con manejo de error claro.

**Prioridad**: Baja (raro que pase en práctica).

### 9. `tool_refrescar_chart_accounts` (línea 2484)

**Estado actual**: Recarga chart desde QBO API. Cache a
`data/chart_of_accounts_cache.json`.

**Gap**: Si la API falla, retorna error pero no usa cache stale.
El usuario tiene que re-intentar.

**Solución propuesta**: Si falla, intentar con cache viejo
+ warning.

**Prioridad**: Baja.

### 10. `build_conversation_context` (línea 2852)

**Estado actual**: Construye contexto con últimos N turnos y
keywords de los últimos 4 mensajes. Limitado y poco flexible.

**Gap**: No usa el sistema de batches del Sprint 1+2 para dar
contexto sobre batches recientes.

**Solución propuesta**: Si hay batches recientes relevantes
(último PENDING, último EXECUTED del mismo tipo), mencionarlos
en el contexto.

**Prioridad**: Baja (nice-to-have).

## Plan de acción

### Sprint 3 (cerrado)

- [x] `taggear_reconciliacion` tool + `qbo_client.py` adapter + 22 tests
- [x] `limpiar_tags_reconciliacion` tool
- [x] `get_relevant_tools` actualizado para keywords `recon`/`tag`/`marcar`

### Sprint 4 (siguiente)

- [ ] `depositar_lote_csv` tool que use `DepositBatchSkill` (nuevo, no rompe viejo)
- [ ] `procesar_csv_bills_batch` tool que use `procesar_lote_ocr` con previsualización
- [ ] Arreglar `obtener_estadisticas_tokens` para soportar `"dia"` y `"mes"`
- [ ] Agregar 2-3 triggers a `process_quick_command` para BNK-RECON y batch

### Sprint 5 (refactor plan)

- [ ] Mover tools de main.py a `dexter/skills/*` (uno por dominio)
- [ ] Reducir main.py a shim de <500 líneas que solo carga skills y maneja chat loop
- [ ] Tests de integración por skill con mock QBO

## Métricas

- Tests: 166/166 pasando (27 bank_feed + 19 ocr_bills + 27 storage +
  24 engine + 18 disambiguator + 13 deposits + 16 recon_tagger + 22 qbo_client)
- Archivos `.py` en `dexter/`: 8 módulos
- Funciones refactorizadas: 3 (`procesar_lote_ocr`,
  `classify_transaction`, `ReconciliationTaggerSkill`)
- Tools nuevos en main.py: 2 (BNK-RECON)
- Líneas agregadas en main.py: ~150 (los 2 tools nuevos)
- Líneas removidas de main.py: 0 (backward compatible)
