# Amortización de Gastos
**Versión:** 1.0.0 | **Dominio:** Contabilidad Avanzada

Distribuye un gasto en el tiempo usando el método de prepaid expenses (cuenta puente). Crea journal entries automáticas para el traspaso inicial y la amortización mensual.

## Cuándo Usar
- Distribuir un gasto anual en 12 cuotas mensuales
- Prorratear una póliza de seguro
- Amortizar prepaid expenses
- Diferir cargos a lo largo de meses

## Flujo
1. El usuario indica: monto, cuenta origen, meses
2. Dexter pregunta: cuenta puente, tipo de distribución, día del mes, vendor
3. Dexter muestra el plan (SIN crear nada)
4. Usuario confirma → se crean journal entries

## Parámetros
| Parámetro | Tipo | Descripción |
|---|---|---|
| monto | number | Total a distribuir |
| cuenta_origen | string | Cuenta de gasto |
| meses | int | Plazo (default 12) |
| cuenta_puente | string | Prepaid Expenses, Deferred Charges |
| distribucion | string | "equitativa" o "personalizada" |
| vendor | string | Proveedor (opcional) |
| dia_mes | int | 1=principio, 15=mitad, 28=final |
