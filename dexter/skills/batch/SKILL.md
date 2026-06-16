# Motor Batch
**Versión:** 2.0.0 | **Dominio:** Dexter v5.0 | **HIGH-2**

Procesamiento por lotes de depósitos, reconciliación, y operaciones masivas. Dry-run obligatorio antes de ejecutar.

## Formato CSV para Depósitos (HIGH-2)

```csv
date,client_name,amount,bank_account,line_account,memo
2026-06-15,John Smith,1000.00,Business Account,Customer Deposits,Anticipo proyecto A
2026-06-15,Jane Doe,1000.00,Business Account,Customer Deposits,Prepago servicios
2026-06-15,Acme Corp,1000.00,Checking,Sales,Factura #1042
```

| Columna | Requerida | Descripción |
|---|---|---|
| `date` | Sí | Fecha del depósito (YYYY-MM-DD) |
| `client_name` | Sí | Nombre del cliente (fuzzy match ≥85%) |
| `amount` | Sí | Monto de esta línea (USD) |
| `bank_account` | No | Cuenta bancaria destino (DepositToAccountRef). Si se omite → auto-detecta primer Bank activo |
| `line_account` | No | Cuenta contable de la línea (AccountRef). Puede ser cualquier tipo: Income, Liability, Asset, etc. Si se omite → auto-detecta primer Income |
| `memo` | No | Nota privada |

**Backward compat:** CSV con solo `date,client_name,amount` sigue funcionando. Las columnas nuevas son opcionales.

## Herramientas
Las herramientas específicas están definidas en `__init__.py` y se auto-descubren vía `dexter.skills`.
