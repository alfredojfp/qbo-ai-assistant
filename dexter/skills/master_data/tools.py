"""dexter.skills.master_data.tools — 8 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).


def tool_crear_clase(nombre: str, clase_padre_id: str = None, activa: bool = True) -> dict:
    """Tool: Crea una clase para segmentación P&L."""
    return create_class(nombre, clase_padre_id, activa)



def tool_crear_cuenta(nombre: str, tipo_cuenta: str, subtipo: str = None,
                      descripcion: str = None, saldo_apertura: float = None,
                      fecha_saldo_apertura: str = None) -> dict:
    """Tool: Crea una cuenta contable (Account) en QuickBooks."""
    return create_account(nombre, tipo_cuenta, subtipo, descripcion,
                          saldo_apertura, fecha_saldo_apertura)



def tool_crear_departamento(nombre: str, depto_padre_id: str = None, activo: bool = True) -> dict:
    """Tool: Crea un departamento para segmentación P&L."""
    return create_department(nombre, depto_padre_id, activo)



def tool_crear_empleado(nombre: str, apellido: str = None, segundo_apellido: str = None,
                        email: str = None, telefono: str = None, direccion: str = None,
                        fecha_contratacion: str = None, tarifa_hora: float = None) -> dict:
    """Tool: Crea un empleado (Employee) en QuickBooks."""
    return create_employee(nombre, apellido, segundo_apellido, email, telefono,
                          direccion, fecha_contratacion, tarifa_hora)



def tool_crear_item(nombre: str, tipo: str = "Service", precio_unitario: float = 0.0,
                    cuenta_ingreso_id: str = None, cuenta_gasto_id: str = None,
                    cuenta_activo_id: str = None, sku: str = None,
                    rastrear_inventario: bool = False, cantidad_inicial: float = 0.0,
                    fecha_inicio_inv: str = None, descripcion: str = None) -> dict:
    """Tool: Crea un item (producto o servicio) en QuickBooks."""
    return create_item(nombre, tipo, precio_unitario, cuenta_ingreso_id,
                       cuenta_gasto_id, cuenta_activo_id, sku,
                       rastrear_inventario, cantidad_inicial, fecha_inicio_inv,
                       descripcion)



def tool_crear_paymentmethod(nombre: str, tipo: str = "Other", activo: bool = True) -> dict:
    """Tool: Crea un método de pago en QuickBooks."""
    return create_payment_method(nombre, tipo, activo)



def tool_crear_termino(nombre: str, dias_vencimiento: int = 30,
                       dias_descuento: int = 0, pct_descuento: float = 0.0,
                       activo: bool = True) -> dict:
    """Tool: Crea un plazo de pago (ej: Net 30, 2/10 Net 30)."""
    return create_term(nombre, dias_vencimiento, dias_descuento, pct_descuento, activo)



def tool_crear_vendor(nombre: str, empresa: str = None, email: str = None,
                      telefono: str = None, direccion: str = None,
                      es_1099: bool = False, tarifa_hora: float = None,
                      term_id: str = None) -> dict:
    """Tool: Crea un proveedor (Vendor) en QuickBooks."""
    return create_vendor(nombre, empresa, email, telefono, direccion, es_1099, tarifa_hora, term_id)



