# Ejemplos de CSV

Este directorio contiene archivos CSV de ejemplo con **datos ficticios** para demostrar el uso de Dexter.

## ⚠️ Importante

Estos archivos contienen **nombres y montos de ejemplo**. No son datos reales de clientes.

## Archivos Disponibles

### deposits_example.csv
- **Propósito:** Demostrar el formato de CSV para depósitos multi-cliente
- **Columnas:** date, client_name, amount, bank_account, line_account, memo
- **Uso:** `procesar_csv_customer_deposits examples/deposits_example.csv`

### customer_deposits_example.csv
- **Propósito:** Demostrar el formato de CSV para depósitos individuales
- **Columnas:** client_name, amount
- **Uso:** `aplicar_customer_deposit examples/customer_deposits_example.csv`

## Formato Esperado

### Para Depósitos Multi-línea (deposits_example.csv)
```csv
date,client_name,amount,bank_account,line_account,memo
2026-01-15,John Smith,$1500.00,Checking - Main Bank,Customer Deposits,Invoice #1001
```

### Para Depósitos Individuales (customer_deposits_example.csv)
```csv
client_name,amount
John Smith,1500.00
```

## Notas

- Los montos pueden incluir o no el símbolo `$`
- Las comas en los montos son opcionales (ej: `$1,500.00` o `1500.00`)
- El campo `memo` es opcional
- Los nombres de cuentas deben coincidir con tu Chart of Accounts en QBO
