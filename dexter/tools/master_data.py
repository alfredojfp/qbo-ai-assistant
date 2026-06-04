"""dexter.tools.master_data — 8 tools para crear master data."""
from typing import Any, Dict, List

from main import (
    tool_crear_vendor,
    tool_crear_cuenta,
    tool_crear_item,
    tool_crear_empleado,
    tool_crear_clase,
    tool_crear_departamento,
    tool_crear_termino,
    tool_crear_paymentmethod,
)

SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "crear_vendor",
            "description": "Crea un proveedor (Vendor) en QuickBooks. Solo requiere el nombre (DisplayName). Opcionales: empresa, email, teléfono, dirección, si es 1099, tarifa por hora, plazo de pago.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre del proveedor (DisplayName)"},
                    "empresa": {"type": "string", "description": "Razón social (CompanyName)"},
                    "email": {"type": "string", "description": "Email principal"},
                    "telefono": {"type": "string", "description": "Teléfono principal"},
                    "direccion": {"type": "string", "description": "Dirección de facturación"},
                    "es_1099": {"type": "boolean", "description": "True si es contractor 1099-MISC", "default": False},
                    "tarifa_hora": {"type": "number", "description": "Tarifa por hora para facturación"},
                    "term_id": {"type": "string", "description": "ID del plazo de pago (Term)"},
                },
                "required": ["nombre"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_cuenta",
            "description": "Crea una cuenta (Account) en el Chart of Accounts. Tipos: Bank, AccountsReceivable, OtherCurrentAsset, FixedAsset, OtherAsset, AccountsPayable, CreditCard, OtherCurrentLiability, LongTermLiability, Equity, Income, CostOfGoodsSold, Expense, OtherIncome, OtherExpense.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre de la cuenta"},
                    "tipo_cuenta": {"type": "string", "description": "Tipo de cuenta (AccountType)"},
                    "subtipo": {"type": "string", "description": "Subtipo específico (AccountSubType)"},
                    "descripcion": {"type": "string", "description": "Descripción de la cuenta"},
                    "saldo_apertura": {"type": "number", "description": "Saldo inicial (opening balance)"},
                    "fecha_saldo_apertura": {"type": "string", "description": "Fecha del saldo inicial (YYYY-MM-DD)"},
                },
                "required": ["nombre", "tipo_cuenta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_item",
            "description": "Crea un item (producto o servicio) en QuickBooks. Tipos: Service (servicio), Inventory (inventario con qty), NonInventory (producto sin inventario).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre del item"},
                    "tipo": {"type": "string", "enum": ["Service", "Inventory", "NonInventory"], "default": "Service"},
                    "precio_unitario": {"type": "number", "description": "Precio unitario de venta"},
                    "cuenta_ingreso_id": {"type": "string", "description": "ID de cuenta de ingreso"},
                    "cuenta_gasto_id": {"type": "string", "description": "ID de cuenta de gasto (COGS)"},
                    "cuenta_activo_id": {"type": "string", "description": "ID de cuenta de activo (inventory)"},
                    "sku": {"type": "string", "description": "SKU del producto"},
                    "rastrear_inventario": {"type": "boolean", "description": "True si rastrea cantidad en mano", "default": False},
                    "cantidad_inicial": {"type": "number", "description": "Cantidad inicial en inventario"},
                    "fecha_inicio_inv": {"type": "string", "description": "Fecha de inicio del inventario"},
                    "descripcion": {"type": "string", "description": "Descripción del item"},
                },
                "required": ["nombre"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_empleado",
            "description": "Crea un empleado (Employee) en QuickBooks para nóminas o time tracking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre (DisplayName)"},
                    "apellido": {"type": "string", "description": "Apellido principal (GivenName)"},
                    "segundo_apellido": {"type": "string", "description": "Segundo apellido (FamilyName)"},
                    "email": {"type": "string", "description": "Email principal"},
                    "telefono": {"type": "string", "description": "Teléfono principal"},
                    "direccion": {"type": "string", "description": "Dirección del empleado"},
                    "fecha_contratacion": {"type": "string", "description": "Fecha de contratación (YYYY-MM-DD)"},
                    "tarifa_hora": {"type": "number", "description": "Tarifa por hora facturable"},
                },
                "required": ["nombre"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_clase",
            "description": "Crea una clase (Class) en QuickBooks para segmentación de P&L (ej: proyectos, líneas de negocio).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre de la clase"},
                    "clase_padre_id": {"type": "string", "description": "ID de la clase padre (para sub-clases)"},
                    "activa": {"type": "boolean", "default": True},
                },
                "required": ["nombre"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_departamento",
            "description": "Crea un departamento (Department) en QuickBooks para segmentación de P&L.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre del departamento"},
                    "depto_padre_id": {"type": "string", "description": "ID del departamento padre (para sub-departamentos)"},
                    "activo": {"type": "boolean", "default": True},
                },
                "required": ["nombre"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_termino",
            "description": "Crea un plazo de pago (Term) en QuickBooks. Ejemplos: Net 30, 2/10 Net 30 (2% descuento si paga en 10 días, total en 30).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre del plazo (ej: Net 30)"},
                    "dias_vencimiento": {"type": "integer", "description": "Días hasta el vencimiento", "default": 30},
                    "dias_descuento": {"type": "integer", "description": "Días para descuento pronto pago", "default": 0},
                    "pct_descuento": {"type": "number", "description": "Porcentaje de descuento pronto pago", "default": 0.0},
                    "activo": {"type": "boolean", "default": True},
                },
                "required": ["nombre"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_paymentmethod",
            "description": "Crea un método de pago (PaymentMethod) en QuickBooks. Tipos: Cash, Check, CreditCard, BankTransfer, Other.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre del método de pago"},
                    "tipo": {"type": "string", "enum": ["Cash", "Check", "CreditCard", "BankTransfer", "Other"], "default": "Other"},
                    "activo": {"type": "boolean", "default": True},
                },
                "required": ["nombre"],
            },
        },
    },
]

KEYWORDS: List[str] = [
    "vendor", "proveedor", "crear proveedor", "nuevo proveedor",
    "cuenta", "account", "chart of accounts", "nueva cuenta",
    "item", "producto", "servicio", "inventario", "nuevo item",
    "empleado", "employee", "nómina", "nuevo empleado",
    "clase", "class", "segmentación", "nueva clase",
    "departamento", "department", "nuevo departamento",
    "termino", "term", "plazo", "net 30", "vencimiento",
    "payment method", "metodo pago", "forma pago",
    "master data", "configuración inicial", "setup",
]

FUNCTIONS: Dict[str, Any] = {
    "crear_vendor": tool_crear_vendor,
    "crear_cuenta": tool_crear_cuenta,
    "crear_item": tool_crear_item,
    "crear_empleado": tool_crear_empleado,
    "crear_clase": tool_crear_clase,
    "crear_departamento": tool_crear_departamento,
    "crear_termino": tool_crear_termino,
    "crear_paymentmethod": tool_crear_paymentmethod,
}
