# Dry-Run Mode — Modo Simulación

> **Versión:** v4.1.0-dev
> **Commit:** `dry-run implementation`
> **Agregado:** Junio 2026

---

## ¿Qué es?

El modo dry-run permite simular cualquier operación de escritura en QBO sin ejecutarla realmente. Es como un "ensayo general" antes de crear/modificar/eliminar datos.

## ¿Cómo se usa?

Agregá `--dry-run` al final de tu mensaje:

```
❯ Tú: crea un estimate para Prueba2 por $1,000 --dry-run

  ⚡ buscar_cliente · nombre=Prueba2
    ✓ Cliente encontrado (ID 70)

  [DRY-RUN] Se simularía crear_estimate(cliente_id=70, monto=1000)
            No se ejecutó nada en QBO.

  Dexter · En modo simulación, crearía un estimate para Prueba2 (ID 70)
           por $1,000.00. No se hizo ningún cambio en QBO.

❯ Tú: ahora sí, crealo (sin --dry-run)

  ⚡ crear_estimate · cliente_id=70, monto=1000
    ✓ Estimate #91 creado — $1,000.00
```

## Comportamiento

| Tipo de tool | En dry-run |
|---|---|
| **Lectura** (buscar_cliente, qbo_query, reportes...) | ✅ Se ejecuta normalmente |
| **Escritura** (crear_*, delete, update, void...) | ⛔ Se simula, no toca QBO |
| **Confirmación** | ❌ No se pide (es simulación) |

## ¿Para qué sirve?

1. **Probar antes de ejecutar** — "¿Qué pasaría si creo 50 facturas?"
2. **Verificar que entendió** — "¿A quiénes les mandaría el invoice?"
3. **Aprender sin riesgo** — "Mostrame qué harías para reconciliar mayo"
4. **Debug** — "¿Qué tools llamarías para este comando?"

## Implementación

- `_parse_dry_run(msg)` — detecta y elimina el flag
- `_execute_tool(name, args)` — wrapper que respeta dry-run
- `_READ_ONLY_TOOLS` — set de 35 tools de solo-lectura
- `DRY_RUN_ACTIVE` — flag global, se resetea automáticamente cada iteración

## Tests

8 tests cubriendo:
- Detección del flag (normal, case-insensitive, mid-message)
- Simulación de tools de escritura
- Ejecución normal de tools de lectura
- Reset automático del flag
- Integración completa del flujo
