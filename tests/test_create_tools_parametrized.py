"""Tests parametrizados para R-9: 18 create_* tools.

Cada create_X de main.py tiene un tool_crear_X correspondiente. Esta
suite verifica:
  1. La función create_X existe en main.
  2. tool_crear_X existe y es callable.
  3. Con qbo_request mockeado a 200 + Id válida, retorna success.
  4. Con qbo_request mockeado a 4xx, retorna error graceful (no raise).

Usa subTest para parametrizar sobre 18 entidades. Verifica backward
compat: cada create_X es testeable con mocks sin red.

NOTA: create_X tienen APIs heterogéneas (algunos requieren line_items,
otros solo IDs/nombres). Esta suite pasa args mínimos que cada create
puede aceptar — no se intenta cubrir TODO el flow, solo el happy path
y el error path.
"""
import unittest
from unittest.mock import MagicMock, patch


# 18 create_* tools core (excluye helpers internos como create_deposits_template)
CREATE_TOOLS = [
    ("create_invoice", "tool_crear_invoice", {"customer_id": "1", "lineas": [{"item_id": "1", "amount": 10}]}),
    ("create_bill", "tool_crear_bill", {"vendor_id": "1", "lineas": [{"account_id": "1", "amount": 10}]}),
    ("create_deposit", "tool_crear_deposito", {"cuenta_destino_id": "1", "lineas": [{"from_account_id": "2", "amount": 100}]}),
    ("create_payment", "tool_crear_pago", {"customer_id": "1", "amount": 100, "cuenta_id": "1"}),
    ("create_customer", "tool_crear_cliente", {"nombre": "Test Customer"}),
    ("create_vendor", "tool_crear_vendor", {"nombre": "Test Vendor"}),
    ("create_account", "tool_crear_cuenta", {"nombre": "Test Account", "tipo_cuenta": "Bank"}),
    ("create_item", "tool_crear_item", {"nombre": "Test Item"}),
    ("create_employee", "tool_crear_empleado", {"nombre": "Test"}),
    ("create_class", "tool_crear_clase", {"nombre": "Test Class"}),
    ("create_department", "tool_crear_departamento", {"nombre": "Test Dept"}),
    ("create_term", "tool_crear_termino", {"nombre": "Net 30"}),
    ("create_payment_method", "tool_crear_paymentmethod", {"nombre": "Cash"}),
    ("create_billpayment", "tool_crear_billpayment", {"vendor_id": "1", "monto_total": 100}),
    ("create_estimate", "tool_crear_estimate", {"cliente_id": "1", "lineas": [{"item_id": "1", "amount": 10}]}),
    ("create_salesreceipt", "tool_crear_salesreceipt", {"cliente_id": "1", "lineas": [{"item_id": "1", "amount": 10}]}),
    ("create_creditmemo", "tool_crear_creditmemo", {"cliente_id": "1", "lineas": [{"item_id": "1", "amount": 10}]}),
    ("create_purchase", "tool_crear_purchase", {"vendor_id": "1", "cuenta_gasto_id": "1", "monto": 100}),
]


def _ok_response(entity_name: str, entity_id: str = "9999"):
    """Mock de QBO POST 200 OK con {Entity: {Id: '9999'}}."""
    r = MagicMock()
    r.status_code = 200
    r.text = ""
    r.json.return_value = {entity_name: {"Id": entity_id, "SyncToken": "0"}}
    return r


def _err_response(status: int = 400, text: str = "bad request"):
    """Mock de QBO POST error."""
    r = MagicMock()
    r.status_code = status
    r.text = text
    r.json.return_value = {"Fault": {"Error": [{"Message": text}]}}
    return r


# Mapeo create_X function name → entity name en respuesta QBO
ENTITY_NAME_MAP = {
    "create_invoice": "Invoice",
    "create_bill": "Bill",
    "create_deposit": "Deposit",
    "create_payment": "Payment",
    "create_customer": "Customer",
    "create_vendor": "Vendor",
    "create_account": "Account",
    "create_item": "Item",
    "create_employee": "Employee",
    "create_class": "Class",
    "create_department": "Department",
    "create_term": "Term",
    "create_payment_method": "PaymentMethod",
    "create_billpayment": "BillPayment",
    "create_estimate": "Estimate",
    "create_salesreceipt": "SalesReceipt",
    "create_creditmemo": "CreditMemo",
    "create_purchase": "Purchase",
}


class TestCreateToolsExist(unittest.TestCase):
    """R-9.1: las 18 funciones create_X y tool_crear_X existen."""

    def test_all_create_functions_exist(self):
        import main
        for create_name, tool_name, _ in CREATE_TOOLS:
            with self.subTest(create=create_name):
                self.assertTrue(
                    hasattr(main, create_name),
                    f"main.{create_name} no existe",
                )
                self.assertTrue(
                    hasattr(main, tool_name),
                    f"main.{tool_name} no existe",
                )
                self.assertTrue(callable(getattr(main, create_name)))
                self.assertTrue(callable(getattr(main, tool_name)))


class TestCreateToolsHappyPath(unittest.TestCase):
    """R-9.2: con QBO 200 OK, cada tool retorna success."""

    def test_each_create_tool_returns_success(self):
        """Mock qbo_request → 200 OK con Id. tool_crear_X retorna success."""
        import main

        for create_name, tool_name, kwargs in CREATE_TOOLS:
            entity_name = ENTITY_NAME_MAP[create_name]
            with self.subTest(tool=tool_name):
                with patch.object(main, "qbo_request",
                                  return_value=_ok_response(entity_name, "9999")):
                    tool_fn = getattr(main, tool_name)
                    try:
                        result = tool_fn(**kwargs)
                    except Exception as e:
                        self.fail(f"{tool_name} raised {type(e).__name__}: {e}")

                    self.assertIsInstance(result, dict, f"{tool_name} no retornó dict")
                    self.assertTrue(
                        result.get("success", False) or "Id" in str(result) or "invoice_id" in result or "bill_id" in result,
                        f"{tool_name} no retornó success: {result}",
                    )


class TestCreateToolsErrorPath(unittest.TestCase):
    """R-9.3: con QBO 4xx, cada tool retorna error graceful (no raise)."""

    def test_each_create_tool_handles_4xx(self):
        import main

        for create_name, tool_name, kwargs in CREATE_TOOLS:
            with self.subTest(tool=tool_name):
                with patch.object(main, "qbo_request",
                                  return_value=_err_response(400, "validation error")):
                    tool_fn = getattr(main, tool_name)
                    try:
                        result = tool_fn(**kwargs)
                    except Exception as e:
                        self.fail(f"{tool_name} raised {type(e).__name__}: {e}")

                    self.assertIsInstance(result, dict, f"{tool_name} no retornó dict en error")
                    self.assertFalse(
                        result.get("success", True),
                        f"{tool_name} retornó success=True en error: {result}",
                    )


if __name__ == "__main__":
    unittest.main()
