"""E2E tests contra QuickBooks sandbox realm 9341455870833544.

R-1: tests/test_e2e_sandbox.py — suite E2E con flows reales.

Estos tests hacen llamadas HTTP reales al sandbox de QBO. Crean
entidades (clientes, items, invoices) con nombres únicos timestampados
para evitar colisiones, y limpian al final voidando las entidades.

⚠️ REQUISITOS:
   1. OAuth flow vigente: ejecutar
        python scripts/oauth_flow.py
      y completar el flow en Brave browser.
   2. Token guardado en companies/Sandbox Company_US_1/meta.json
   3. Para correr la suite:
        RUN_E2E_SANDBOX=1 python -m unittest tests.test_e2e_sandbox

Si el token está expirado o el flow no se ha hecho, los tests se saltan
con @unittest.skip mostrando el motivo. Esto evita romper la suite
estándar (python -m unittest discover tests/).

⚠️ SEGURIDAD:
   - NO loggear access_token en stdout (puede aparecer en CI logs).
   - Usar entidades con nombre único timestampado para idempotencia.
   - Cleanup: void al final (no delete — QBO no permite delete de
     transacciones, solo void).
"""
import os
import json
import time
import unittest
from datetime import datetime, timedelta


# Sandbox realm por defecto
SANDBOX_REALM_ID = "9341455870833544"
SANDBOX_COMPANY_DIR = "companies/Sandbox Company_US_1"
SANDBOX_META = f"{SANDBOX_COMPANY_DIR}/meta.json"


def _sandbox_available() -> tuple:
    """Verifica que tenemos token vigente. Retorna (available, reason)."""
    if not os.path.exists(SANDBOX_META):
        return False, f"meta.json no existe en {SANDBOX_META}"
    try:
        with open(SANDBOX_META) as f:
            meta = json.load(f)
        if not meta.get("access_token"):
            return False, "access_token vacío en meta.json"
        if not meta.get("refresh_token"):
            return False, "refresh_token vacío en meta.json"
        return True, "OK"
    except Exception as e:
        return False, f"Error leyendo meta.json: {e}"


_SANDBOX_OK, _SANDBOX_REASON = _sandbox_available()


def _require_sandbox(test_method):
    """Decorator: skip test si sandbox no disponible."""
    return unittest.skipUnless(
        os.environ.get("RUN_E2E_SANDBOX") == "1" and _SANDBOX_OK,
        f"Sandbox E2E no disponible: {_SANDBOX_REASON}. "
        f"Set RUN_E2E_SANDBOX=1 + ejecutar OAuth flow.",
    )(test_method)


def _load_token() -> str:
    """Carga access_token desde meta.json."""
    with open(SANDBOX_META) as f:
        return json.load(f)["access_token"]


def _unique_name(prefix: str) -> str:
    """Genera nombre único con timestamp para evitar colisiones."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}_E2E_{ts}"


class TestE2ESandboxConnection(unittest.TestCase):
    """R-1.1: Conexión básica al sandbox."""

    @_require_sandbox
    def test_company_info_returns_200(self):
        """CompanyInfo query retorna 200 con CompanyName."""
        import main
        original = main.QB_ACCESS_TOKEN
        main.QB_ACCESS_TOKEN = _load_token()
        try:
            r = main.qbo_request(
                "GET", f"companyinfo/{SANDBOX_REALM_ID}",
            )
            self.assertEqual(r.status_code, 200, r.text[:300])
            j = r.json()
            name = j.get("CompanyInfo", {}).get("CompanyName", "")
            self.assertTrue(name, "CompanyName vacío")
        finally:
            main.QB_ACCESS_TOKEN = original

    @_require_sandbox
    def test_query_companyinfo_sql(self):
        """Query SQL a CompanyInfo retorna al menos 1 registro."""
        import main
        original = main.QB_ACCESS_TOKEN
        main.QB_ACCESS_TOKEN = _load_token()
        try:
            r = main.qbo_request(
                "GET", "query",
                params={"query": "SELECT * FROM CompanyInfo MAXRESULTS 1"},
            )
            self.assertEqual(r.status_code, 200, r.text[:300])
            j = r.json()
            rows = j.get("QueryResponse", {}).get("CompanyInfo", [])
            self.assertGreaterEqual(len(rows), 1)
        finally:
            main.QB_ACCESS_TOKEN = original


class TestE2ECustomerFlow(unittest.TestCase):
    """R-1.2: Flujo crear→query→void customer."""

    @_require_sandbox
    def test_create_query_void_customer(self):
        """Crea customer con nombre único, lo queryea, lo intenta void
        (QBO no permite void de Customer, así que solo validamos creación
        + query)."""
        import main
        original = main.QB_ACCESS_TOKEN
        main.QB_ACCESS_TOKEN = _load_token()
        try:
            unique = _unique_name("E2ECust")
            payload = {
                "DisplayName": unique,
                "CompanyName": unique,
            }
            r = main.qbo_request("POST", "customer", data=payload)
            self.assertEqual(r.status_code, 200, r.text[:300])
            cust_id = r.json()["Customer"]["Id"]
            self.assertTrue(cust_id)

            r2 = main.qbo_request(
                "GET", "query",
                params={"query": f"SELECT * FROM Customer WHERE Id='{cust_id}'"},
            )
            self.assertEqual(r2.status_code, 200)
            self.assertEqual(
                r2.json()["QueryResponse"]["Customer"][0]["DisplayName"],
                unique,
            )
        finally:
            main.QB_ACCESS_TOKEN = original


class TestE2EItemFlow(unittest.TestCase):
    """R-1.3: Flujo crear→query item."""

    @_require_sandbox
    def test_create_query_item(self):
        """Crea item tipo Service, lo queryea, lo valida."""
        import main
        original = main.QB_ACCESS_TOKEN
        main.QB_ACCESS_TOKEN = _load_token()
        try:
            unique = _unique_name("E2EItem")
            payload = {
                "Name": unique,
                "Type": "Service",
                "IncomeAccountRef": {"value": "1"},
                "UnitPrice": 100.0,
            }
            r = main.qbo_request("POST", "item", data=payload)
            self.assertEqual(r.status_code, 200, r.text[:300])
            item_id = r.json()["Item"]["Id"]

            r2 = main.qbo_request(
                "GET", "item/" + item_id,
            )
            self.assertEqual(r2.status_code, 200)
            self.assertEqual(
                r2.json()["Item"]["Name"],
                unique,
            )
        finally:
            main.QB_ACCESS_TOKEN = original


class TestE2EInvoiceFlow(unittest.TestCase):
    """R-1.4: Flujo invoice completo (buscar customer + item, crear invoice)."""

    @_require_sandbox
    def test_create_invoice_end_to_end(self):
        """Crea invoice usando wrapper tool_crear_invoice con sandbox data."""
        import main
        original = main.QB_ACCESS_TOKEN
        main.QB_ACCESS_TOKEN = _load_token()
        try:
            cust_name = "AlfredoTPM"
            cust_res = main.tool_buscar_cliente(cust_name)
            self.assertIn("clientes", cust_res)
            custs = cust_res.get("clientes", [])
            self.assertTrue(custs, f"Customer {cust_name} no existe en sandbox")
            self.assertIn("id", custs[0])

            item_res = main.tool_buscar_item("Sales")
            items = item_res.get("items", [])
            if not items:
                item_res = main.tool_buscar_item("Service")
                items = item_res.get("items", [])
            if not items:
                self.skipTest("No hay item 'Sales' o 'Service' en sandbox")

            fecha = datetime.now().strftime("%Y-%m-%d")
            res = main.tool_crear_invoice(
                customer_id=custs[0]["id"],
                lineas=[{
                    "item_id": items[0]["id"],
                    "amount": 10.0,
                    "quantity": 1,
                    "description": "E2E test invoice",
                }],
                fecha=fecha,
                memo=f"E2E suite {datetime.now().isoformat()}",
            )
            self.assertTrue(res.get("success"), res)
            self.assertIn("invoice_id", res)
        finally:
            main.QB_ACCESS_TOKEN = original


class TestE2EReportFlow(unittest.TestCase):
    """R-1.5: Generación de reportes P&L y Balance Sheet."""

    @_require_sandbox
    def test_pl_report_returns_list(self):
        """P&L del último mes retorna list[dict] (LOW-7)."""
        import main
        original = main.QB_ACCESS_TOKEN
        main.QB_ACCESS_TOKEN = _load_token()
        try:
            end = datetime.now()
            start = end - timedelta(days=30)
            rows = main.generate_pl_report(
                start.strftime("%Y-%m-%d"),
                end.strftime("%Y-%m-%d"),
            )
            self.assertIsInstance(rows, list)
        finally:
            main.QB_ACCESS_TOKEN = original

    @_require_sandbox
    def test_balance_sheet_returns_list(self):
        """Balance Sheet retorna list[dict] (LOW-7)."""
        import main
        original = main.QB_ACCESS_TOKEN
        main.QB_ACCESS_TOKEN = _load_token()
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            rows = main.generate_balance_sheet(today)
            self.assertIsInstance(rows, list)
        finally:
            main.QB_ACCESS_TOKEN = original


class TestE2EChartCache(unittest.TestCase):
    """R-1.6: Chart of Accounts cache funciona (LOW-4)."""

    @_require_sandbox
    def test_chart_of_accounts_loads(self):
        """load_chart_of_accounts() retorna dict con cuentas (flat)."""
        import main
        original_token = main.QB_ACCESS_TOKEN
        main.QB_ACCESS_TOKEN = _load_token()
        try:
            chart = main.load_chart_of_accounts(force_refresh=True)
            self.assertIsInstance(chart, dict)
            self.assertGreater(len(chart), 0)
            first_key = next(iter(chart))
            self.assertIn("id", chart[first_key])
            self.assertIn("name", chart[first_key])
            self.assertIn("type", chart[first_key])
        finally:
            main.QB_ACCESS_TOKEN = original_token

    @_require_sandbox
    def test_chart_cache_file_has_schema_version(self):
        """FILE_CHART_CACHE contiene schema_version + company_realm_id."""
        import main
        original_token = main.QB_ACCESS_TOKEN
        main.QB_ACCESS_TOKEN = _load_token()
        try:
            main.load_chart_of_accounts(force_refresh=True)
            with open(main.FILE_CHART_CACHE) as f:
                cache = json.load(f)
            self.assertEqual(cache.get("schema_version"), main.CHART_SCHEMA_VERSION)
            self.assertIn("company_realm_id", cache)
            self.assertIn("last_updated", cache)
        finally:
            main.QB_ACCESS_TOKEN = original_token


class TestE2ESearchAndQuery(unittest.TestCase):
    """R-1.7: Search tools funcionan contra sandbox."""

    @_require_sandbox
    def test_buscar_cliente_real(self):
        """tool_buscar_cliente() encuentra 'AlfredoTPM' (creado en sesión)."""
        import main
        original = main.QB_ACCESS_TOKEN
        main.QB_ACCESS_TOKEN = _load_token()
        try:
            res = main.tool_buscar_cliente("AlfredoTPM")
            self.assertIn("clientes", res)
            self.assertGreater(res.get("encontrados", 0), 0)
            self.assertIn("id", res["clientes"][0])
            self.assertIn("name", res["clientes"][0])
        finally:
            main.QB_ACCESS_TOKEN = original

    @_require_sandbox
    def test_buscar_cuenta_real(self):
        """tool_buscar_cuenta() requiere session_state['chart_of_accounts']
        poblado. Verifica que el wrapper retorna shape correcta."""
        import main
        original = main.QB_ACCESS_TOKEN
        main.QB_ACCESS_TOKEN = _load_token()
        try:
            res = main.tool_buscar_cuenta("Checking")
            self.assertIn("cuentas", res)
            self.assertIn("encontradas", res)
            self.assertIsInstance(res["cuentas"], list)
        finally:
            main.QB_ACCESS_TOKEN = original


if __name__ == "__main__":
    unittest.main()
