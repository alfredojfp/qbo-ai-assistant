"""dexter.skills.advanced.tools — 8 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

from datetime import datetime
from main import buscar_cliente, buscar_vendor, buscar_cuenta, buscar_item

def tool_calcular_distribucion(monto: float, cuenta_origen: str,
                               meses: int = 12, cuenta_puente: str = None,
                               fecha_inicio: str = None,
                               distribucion: str = "equitativa",
                               montos_personalizados: list = None,
                               dia_mes: int = 1,
                               vendor: str = None) -> dict:
    """Tool: Calcula la distribución de un gasto en N meses.

    Paso 1 de 2. Muestra el plan de amortización ANTES de crear nada en QBO.

    SIEMPRE preguntá al usuario antes de llamar este tool:
      1. ¿Cuenta puente? (Prepaid Expenses, Deferred Charges, etc.)
      2. ¿Distribución? 'equitativa' (montos iguales) o 'personalizada'
      3. ¿Día del mes? 1=principio, 15=mitad, 28=final
      4. ¿Fecha de inicio? (YYYY-MM-DD, default: 1er día del mes actual)

    Args:
        monto: Monto total a distribuir
        cuenta_origen: Nombre de la cuenta de gasto
        meses: Número de meses
        cuenta_puente: Nombre de la cuenta puente
        fecha_inicio: Fecha YYYY-MM-DD
        distribucion: 'equitativa' o 'personalizada'
        montos_personalizados: Lista de montos por mes (si personalizada)
        dia_mes: Día del mes para cada JE (1-28)
    """
    if cuenta_puente is None:
        return {
            "success": False,
            "necesita_cuenta_puente": True,
            "mensaje": "Necesito saber la cuenta puente. Ej: 'Prepaid Expenses', 'Deferred Charges'. "
                       "El gasto se mueve de la cuenta origen a esta cuenta puente, "
                       "y luego se distribuye mes a mes."
        }

    from datetime import datetime, timedelta
    if fecha_inicio is None:
        fecha_inicio = datetime.now().strftime("%Y-%m-01")

    # Validar dia_mes (1-28 para evitar problemas con febrero)
    dia_mes = max(1, min(dia_mes or 1, 28))

    # Buscar cuentas
    origen = buscar_cuenta(cuenta_origen)
    puente = buscar_cuenta(cuenta_puente)

    if origen.get("encontrados", 0) == 0:
        return {"success": False, "error": f"Cuenta origen '{cuenta_origen}' no encontrada"}
    if puente.get("encontrados", 0) == 0:
        return {"success": False, "error": f"Cuenta puente '{cuenta_puente}' no encontrada"}

    origen_id = origen["cuentas"][0]["id"]
    origen_name = origen["cuentas"][0]["name"]
    puente_id = puente["cuentas"][0]["id"]
    puente_name = puente["cuentas"][0]["name"]

    # Vendor opcional
    vendor_id = None
    vendor_name = None
    if vendor:
        v = buscar_vendor(vendor)
        if v and isinstance(v, list) and len(v) > 0:
            vendor_id = v[0].get("id")
            vendor_name = v[0].get("name", vendor)

    # Calcular montos mensuales
    if distribucion == "personalizada" and montos_personalizados:
        montos = montos_personalizados[:meses]
    else:
        monto_mensual = round(monto / meses, 2)
        montos = [monto_mensual] * meses
        montos[-1] = round(monto - monto_mensual * (meses - 1), 2)

    # Plan de journal entries
    plan = {
        "paso_1": {
            "descripcion": f"Mover ${monto:,.2f} de {origen_name} → {puente_name}",
            "debito": {"cuenta": puente_name, "cuenta_id": puente_id, "monto": monto},
            "credito": {"cuenta": origen_name, "cuenta_id": origen_id, "monto": monto},
        },
        "paso_2_amortizacion": [],
    }

    start_date = datetime.strptime(fecha_inicio[:7] + "-01", "%Y-%m-%d")
    for i in range(meses):
        mes_fecha = start_date + timedelta(days=32 * i)
        try:
            mes_fecha = mes_fecha.replace(day=min(dia_mes, 28))
        except ValueError:
            mes_fecha = mes_fecha.replace(day=28)
        monto_este_mes = montos[i]
        plan["paso_2_amortizacion"].append({
            "mes": i + 1,
            "fecha": mes_fecha.strftime("%Y-%m-%d"),
            "debito": {"cuenta": origen_name, "cuenta_id": origen_id, "monto": monto_este_mes},
            "credito": {"cuenta": puente_name, "cuenta_id": puente_id, "monto": monto_este_mes},
        })

    return {
        "success": True,
        "plan": plan,
        "resumen": {
            "monto_total": monto,
            "meses": meses,
            "monto_mensual": monto_mensual,
            "ajuste_ultimo_mes": ajuste_ultimo,
            "cuenta_origen": origen_name,
            "cuenta_puente": puente_name,
            "vendor": vendor_name,
            "vendor_id": vendor_id,
            "fecha_inicio": fecha_inicio,
            "dia_mes": dia_mes,
        },
        "siguiente_paso": "Para ejecutar, usá tool_ejecutar_distribucion con este plan."
    }



def tool_cdc_query(entidades: List[str], desde: str) -> dict:
    """Tool: Change Data Capture — retorna entidades modificadas desde un timestamp."""
    return cdc_query(entidades, desde)



def tool_crear_budget(nombre: str, fecha_inicio: str, fecha_fin: str,
                      lineas_presupuesto: List[dict]) -> dict:
    """Tool: Crea un presupuesto (Budget) en QuickBooks."""
    return create_budget(nombre, fecha_inicio, fecha_fin, lineas_presupuesto)



def tool_crear_taxcode(nombre: str, tax_rate_id: str = None, descripcion: str = None,
                        activo: bool = True) -> dict:
    """Tool: Crea un código de impuesto (TaxCode: NON o TAX)."""
    return create_taxcode(nombre, tax_rate_id, descripcion, activo)



def tool_crear_taxrate(nombre: str, tasa: float, agencia_id: str = None,
                       descripcion: str = None, activo: bool = True) -> dict:
    """Tool: Crea una tasa de impuesto (TaxRate) en QuickBooks."""
    return create_taxrate(nombre, tasa, agencia_id, descripcion, activo)



def tool_ejecutar_batch(operaciones: List[dict]) -> dict:
    """Tool: Ejecuta hasta 30 operaciones en una sola llamada (batch API)."""
    return execute_batch(operaciones)



def tool_ejecutar_distribucion(plan: dict) -> dict:
    """Tool: Ejecuta el plan de distribución de gasto (crea journal entries).

    Paso 2 de 2. Recibe el plan generado por tool_calcular_distribucion
    y crea las journal entries en QBO. Requiere confirmación previa del usuario.
    """
    if not plan.get("success"):
        return {"success": False, "error": "Plan inválido"}

    resumen = plan.get("resumen", {})
    detalles = plan.get("plan", {})

    entries_creadas = []

    # Paso 1: Mover monto total a cuenta puente
    paso1 = detalles.get("paso_1", {})
    vendor_ref = f" [{resumen.get('vendor', '')}]" if resumen.get("vendor") else ""
    if paso1:
        try:
            result = create_journal_entry(
                txn_date=resumen.get("fecha_inicio"),
                lines=[
                    {"account_id": paso1["debito"]["cuenta_id"],
                     "amount": paso1["debito"]["monto"],
                     "posting_type": "Debit",
                     "description": paso1["descripcion"] + vendor_ref},
                    {"account_id": paso1["credito"]["cuenta_id"],
                     "amount": paso1["credito"]["monto"],
                     "posting_type": "Credit",
                     "description": paso1["descripcion"] + vendor_ref},
                ],
                memo=f"Distribución: ${resumen.get('monto_total',0):,.2f} en {resumen.get('meses',12)} meses{vendor_ref}"
            )
            entries_creadas.append({"paso": 1, "result": result})
        except Exception as e:
            return {"success": False, "error": f"Error en paso 1: {e}"}

    # Paso 2: Amortización mensual
    for amort in detalles.get("paso_2_amortizacion", []):
        try:
            desc = f"Amortización mes {amort['mes']}/{resumen.get('meses',12)}"
            result = create_journal_entry(
                txn_date=amort["fecha"],
                lines=[
                    {"account_id": amort["debito"]["cuenta_id"],
                     "amount": amort["debito"]["monto"],
                     "posting_type": "Debit",
                     "description": desc},
                    {"account_id": amort["credito"]["cuenta_id"],
                     "amount": amort["credito"]["monto"],
                     "posting_type": "Credit",
                     "description": desc},
                ],
                memo=f"Amortización {amort['mes']}/{resumen.get('meses',12)}: "
                     f"${resumen.get('monto_total',0):,.2f} de {resumen.get('cuenta_origen','?')}"
            )
            entries_creadas.append({"paso": f"2.{amort['mes']}", "result": result})
        except Exception as e:
            return {"success": False, "error": f"Error en mes {amort['mes']}: {e}"}

    return {
        "success": True,
        "journal_entries_creadas": len(entries_creadas),
        "detalle": entries_creadas[:3],  # primeros 3 como preview
        "resumen": resumen,
    }



def tool_leer_exchange_rate(moneda_origen: str, moneda_destino: str = "USD",
                            fecha: str = None) -> dict:
    """Tool: Lee la tasa de cambio entre dos monedas en una fecha."""
    return get_exchange_rate(moneda_origen, moneda_destino, fecha)



