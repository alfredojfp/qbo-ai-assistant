"""Tests para dexter.tools — registry agregador y módulos individuales."""
import unittest


def _schema_name(s: dict) -> str:
    """Extrae name de un schema en formato OpenAI ({type, function:{name,...}}) o simple."""
    if "function" in s and isinstance(s["function"], dict):
        return s["function"]["name"]
    return s.get("name", "")


class TestBankFeedModule(unittest.TestCase):
    """Tests para dexter.tools.bank_feed (5 tools: 4 intelligence + 1 CSV)."""

    def test_module_imports(self):
        from dexter.tools import bank_feed
        self.assertTrue(hasattr(bank_feed, "SCHEMA"))
        self.assertTrue(hasattr(bank_feed, "FUNCTIONS"))

    def test_schema_count_matches_functions_count(self):
        from dexter.tools.bank_feed import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 5)
        self.assertEqual(len(FUNCTIONS), 5)

    def test_schema_function_names_match(self):
        from dexter.tools.bank_feed import SCHEMA, FUNCTIONS
        schema_names = {_schema_name(s) for s in SCHEMA}
        function_names = set(FUNCTIONS.keys())
        self.assertEqual(schema_names, function_names)

    def test_expected_tool_names(self):
        from dexter.tools.bank_feed import SCHEMA
        names = {_schema_name(s) for s in SCHEMA}
        self.assertEqual(
            names,
            {
                "analizarbankfeed",
                "registrarclasificacion",
                "estadisticasclasificacion",
                "buscarpatron",
                "procesar_bank_feed_csv",
            },
        )

    def test_each_function_is_callable(self):
        from dexter.tools.bank_feed import FUNCTIONS
        for name, fn in FUNCTIONS.items():
            self.assertTrue(callable(fn), f"{name} is not callable")

    def test_each_schema_has_required_fields(self):
        from dexter.tools.bank_feed import SCHEMA
        for s in SCHEMA:
            # Soporta ambos formatos: OpenAI ({type, function:{name,...}}) y simple ({name,...})
            if "function" in s:
                inner = s["function"]
            else:
                inner = s
            self.assertIn("name", inner)
            self.assertIn("description", inner)
            self.assertIn("parameters", inner)

    def test_descriptions_are_substantive(self):
        """Una description <30 chars probablemente no explica qué retorna."""
        from dexter.tools.bank_feed import SCHEMA
        for s in SCHEMA:
            inner = s["function"] if "function" in s else s
            self.assertGreater(
                len(inner["description"]),
                30,
                f"Tool '{inner['name']}' description too short: {inner['description']!r}",
            )


class TestToolsAggregator(unittest.TestCase):
    """Tests para dexter.tools.__init__ (registry agregador)."""

    def test_all_schemas_imports(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        self.assertIsInstance(ALL_SCHEMAS, list)
        self.assertIsInstance(ALL_FUNCTIONS, dict)

    def test_count_is_100(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        self.assertEqual(len(ALL_SCHEMAS), 100)
        self.assertEqual(len(ALL_FUNCTIONS), 100)

    def test_no_duplicate_names(self):
        from dexter.tools import ALL_SCHEMAS
        names = [_schema_name(s) for s in ALL_SCHEMAS]
        self.assertEqual(len(names), len(set(names)), "Duplicate tool names")

    def test_every_schema_has_matching_function(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        for s in ALL_SCHEMAS:
            name = _schema_name(s)
            self.assertIn(name, ALL_FUNCTIONS, f"Schema '{name}' has no matching function")
            self.assertTrue(callable(ALL_FUNCTIONS[name]))

    def test_every_function_has_matching_schema(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        schema_names = {_schema_name(s) for s in ALL_SCHEMAS}
        for fn_name in ALL_FUNCTIONS:
            self.assertIn(
                fn_name,
                schema_names,
                f"Function '{fn_name}' has no matching schema",
            )


class TestAllDomainModules(unittest.TestCase):
    """Verifica que los 14 módulos de dominio importan sin error y tienen
    schema/func counts consistentes."""

    EXPECTED_DOMAINS = [
        ("search", 4),
        ("transactions", 5),
        ("reports", 5),
        ("tokens", 2),
        ("admin", 4),
        ("batch", 3),
        ("reconciliation", 3),
        ("ocr", 1),
        ("behavior", 4),
        ("report_custom", 2),
        ("api_explorer", 5),
        ("journal", 2),
        ("web_code", 1),
        ("bank_feed", 5),
    ]

    def test_each_domain_module_loads(self):
        import importlib
        for domain, _ in self.EXPECTED_DOMAINS:
            with self.subTest(domain=domain):
                m = importlib.import_module(f"dexter.tools.{domain}")
                self.assertTrue(hasattr(m, "SCHEMA"))
                self.assertTrue(hasattr(m, "FUNCTIONS"))

    def test_each_domain_has_expected_count(self):
        import importlib
        for domain, expected in self.EXPECTED_DOMAINS:
            with self.subTest(domain=domain, expected=expected):
                m = importlib.import_module(f"dexter.tools.{domain}")
                self.assertEqual(len(m.SCHEMA), expected, f"{domain}.SCHEMA")
                self.assertEqual(len(m.FUNCTIONS), expected, f"{domain}.FUNCTIONS")


class TestCreateCustomerTool(unittest.TestCase):
    """Tests para crear_cliente (agregado en transactions module)."""

    def test_crear_cliente_in_transactions_module(self):
        from dexter.tools.transactions import SCHEMA, FUNCTIONS
        names = {_schema_name(s) for s in SCHEMA}
        self.assertIn("crear_cliente", names)
        self.assertIn("crear_cliente", FUNCTIONS)

    def test_crear_cliente_in_global_registry(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        names = {_schema_name(s) for s in ALL_SCHEMAS}
        self.assertIn("crear_cliente", names)
        self.assertIn("crear_cliente", ALL_FUNCTIONS)

    def test_crear_cliente_has_required_nombre_param(self):
        from dexter.tools.transactions import SCHEMA
        target = next(
            s for s in SCHEMA
            if _schema_name(s) == "crear_cliente"
        )
        inner = target["function"]
        params = inner["parameters"]
        self.assertIn("nombre", params["properties"])
        self.assertIn("nombre", params["required"])

    def test_crear_cliente_function_callable(self):
        from dexter.tools import ALL_FUNCTIONS
        from main import tool_crear_cliente
        self.assertIs(ALL_FUNCTIONS["crear_cliente"], tool_crear_cliente)
        self.assertTrue(callable(tool_crear_cliente))

    def test_keywords_include_cliente(self):
        """El routing debe activarse cuando el usuario menciona cliente/customer."""
        from dexter.tools import KEYWORDS_BY_MODULE
        from dexter.tools import transactions
        kw = KEYWORDS_BY_MODULE["dexter.tools.transactions"]
        joined = " ".join(kw).lower()
        self.assertIn("cliente", joined)


class TestErrorLogTools(unittest.TestCase):
    """Tests para ver_log_errores y limpiar_log_errores (admin module)."""

    def test_ver_log_errores_in_admin_module(self):
        from dexter.tools.admin import SCHEMA, FUNCTIONS
        names = {_schema_name(s) for s in SCHEMA}
        self.assertIn("ver_log_errores", names)
        self.assertIn("ver_log_errores", FUNCTIONS)

    def test_limpiar_log_errores_in_admin_module(self):
        from dexter.tools.admin import SCHEMA, FUNCTIONS
        names = {_schema_name(s) for s in SCHEMA}
        self.assertIn("limpiar_log_errores", names)
        self.assertIn("limpiar_log_errores", FUNCTIONS)

    def test_ver_log_errores_in_global_registry(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        names = {_schema_name(s) for s in ALL_SCHEMAS}
        self.assertIn("ver_log_errores", names)
        self.assertIn("ver_log_errores", ALL_FUNCTIONS)
        self.assertIn("limpiar_log_errores", names)
        self.assertIn("limpiar_log_errores", ALL_FUNCTIONS)

    def test_admin_module_has_4_tools(self):
        from dexter.tools.admin import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 4)
        self.assertEqual(len(FUNCTIONS), 4)

    def test_ver_log_errores_callable(self):
        from dexter.tools import ALL_FUNCTIONS
        from main import tool_ver_log_errores
        self.assertIs(ALL_FUNCTIONS["ver_log_errores"], tool_ver_log_errores)
        self.assertTrue(callable(tool_ver_log_errores))

    def test_admin_keywords_include_log(self):
        from dexter.tools import KEYWORDS_BY_MODULE
        kw = KEYWORDS_BY_MODULE["dexter.tools.admin"]
        joined = " ".join(kw).lower()
        self.assertIn("log", joined)
        self.assertIn("error", joined)


# ============================================================================
# Tests para los 48 tools nuevos de Sprints 1+2+3 (gap analysis)
# ============================================================================

class TestSprint1AMasterData(unittest.TestCase):
    """Sprint 1A: 8 tools de master data (vendor, account, item, employee, etc.)."""

    def test_master_data_module_has_8_tools(self):
        from dexter.tools.master_data import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 8)
        self.assertEqual(len(FUNCTIONS), 8)

    def test_master_data_all_registered(self):
        expected = [
            "crear_vendor", "crear_cuenta", "crear_item", "crear_empleado",
            "crear_clase", "crear_departamento", "crear_termino", "crear_paymentmethod",
        ]
        from dexter.tools.master_data import SCHEMA, FUNCTIONS
        names = {_schema_name(s) for s in SCHEMA}
        for name in expected:
            self.assertIn(name, names, f"master_data missing {name}")
            self.assertIn(name, FUNCTIONS)

    def test_master_data_in_global_registry(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        names = {_schema_name(s) for s in ALL_SCHEMAS}
        for name in ["crear_vendor", "crear_cuenta", "crear_item", "crear_empleado"]:
            self.assertIn(name, names)
            self.assertIn(name, ALL_FUNCTIONS)


class TestSprint1BTransactionExtra(unittest.TestCase):
    """Sprint 1B: 9 tools de transacciones faltantes."""

    def test_transaction_extra_module_has_9_tools(self):
        from dexter.tools.transaction_extra import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 9)
        self.assertEqual(len(FUNCTIONS), 9)

    def test_transaction_extra_all_registered(self):
        expected = [
            "crear_billpayment", "crear_estimate", "crear_salesreceipt",
            "crear_creditmemo", "crear_purchase", "crear_purchaseorder",
            "crear_refundreceipt", "crear_vendorcredit", "crear_timeactivity",
        ]
        from dexter.tools.transaction_extra import SCHEMA, FUNCTIONS
        names = {_schema_name(s) for s in SCHEMA}
        for name in expected:
            self.assertIn(name, names, f"transaction_extra missing {name}")
            self.assertIn(name, FUNCTIONS)

    def test_transaction_extra_in_global_registry(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        names = {_schema_name(s) for s in ALL_SCHEMAS}
        for name in ["crear_billpayment", "crear_estimate", "crear_purchaseorder"]:
            self.assertIn(name, names)
            self.assertIn(name, ALL_FUNCTIONS)


class TestSprint1COperations(unittest.TestCase):
    """Sprint 1C: 10 tools de update/void/delete/deactivate/send."""

    def test_operations_module_has_10_tools(self):
        from dexter.tools.operations import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 10)
        self.assertEqual(len(FUNCTIONS), 10)

    def test_operations_all_registered(self):
        expected = [
            "actualizar_cliente", "actualizar_vendor", "actualizar_factura", "actualizar_bill",
            "eliminar_transaccion", "void_transaccion",
            "desactivar_cliente", "desactivar_vendor",
            "enviar_factura", "enviar_orden_compra",
        ]
        from dexter.tools.operations import SCHEMA, FUNCTIONS
        names = {_schema_name(s) for s in SCHEMA}
        for name in expected:
            self.assertIn(name, names, f"operations missing {name}")
            self.assertIn(name, FUNCTIONS)

    def test_operations_in_global_registry(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        names = {_schema_name(s) for s in ALL_SCHEMAS}
        for name in ["actualizar_cliente", "eliminar_transaccion", "enviar_factura"]:
            self.assertIn(name, names)
            self.assertIn(name, ALL_FUNCTIONS)

    def test_operations_callable(self):
        from dexter.tools import ALL_FUNCTIONS
        from main import tool_actualizar_cliente, tool_eliminar_transaccion
        self.assertIs(ALL_FUNCTIONS["actualizar_cliente"], tool_actualizar_cliente)
        self.assertIs(ALL_FUNCTIONS["eliminar_transaccion"], tool_eliminar_transaccion)


class TestSprint1EReportsExtra(unittest.TestCase):
    """Sprint 1E + P2 opcionales: 16 tools de reportes nativos QBO."""

    def test_reports_extra_module_has_16_tools(self):
        from dexter.tools.reports_extra import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 16)
        self.assertEqual(len(FUNCTIONS), 16)

    def test_reports_extra_all_registered(self):
        expected = [
            "reporte_trial_balance", "reporte_general_ledger", "reporte_cash_flow",
            "reporte_ar_aging", "reporte_ap_aging",
            "reporte_customer_balance", "reporte_vendor_balance",
            "reporte_pl_detail", "reporte_journal", "reporte_account_list",
        ]
        from dexter.tools.reports_extra import SCHEMA, FUNCTIONS
        names = {_schema_name(s) for s in SCHEMA}
        for name in expected:
            self.assertIn(name, names, f"reports_extra missing {name}")
            self.assertIn(name, FUNCTIONS)

    def test_reports_extra_in_global_registry(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        names = {_schema_name(s) for s in ALL_SCHEMAS}
        for name in ["reporte_trial_balance", "reporte_ar_aging", "reporte_cash_flow"]:
            self.assertIn(name, names)
            self.assertIn(name, ALL_FUNCTIONS)


class TestSprint1FRead(unittest.TestCase):
    """Sprint 1F: 3 tools de lectura directa (CompanyInfo, Preferences, Query)."""

    def test_read_module_has_3_tools(self):
        from dexter.tools.read import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 3)
        self.assertEqual(len(FUNCTIONS), 3)

    def test_read_all_registered(self):
        expected = ["leer_companyinfo", "leer_preferencias", "consulta_avanzada"]
        from dexter.tools.read import SCHEMA, FUNCTIONS
        names = {_schema_name(s) for s in SCHEMA}
        for name in expected:
            self.assertIn(name, names, f"read missing {name}")
            self.assertIn(name, FUNCTIONS)

    def test_consulta_avanzada_has_security_constraints(self):
        from dexter.tools.read import SCHEMA
        schema_names = {_schema_name(s) for s in SCHEMA}
        self.assertIn("consulta_avanzada", schema_names)
        for s in SCHEMA:
            if _schema_name(s) == "consulta_avanzada":
                props = s["function"]["parameters"]["properties"]
                self.assertIn("max_results", props)
                self.assertLessEqual(props["max_results"].get("maximum", 1000), 1000)

    def test_read_in_global_registry(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        names = {_schema_name(s) for s in ALL_SCHEMAS}
        for name in ["leer_companyinfo", "leer_preferencias", "consulta_avanzada"]:
            self.assertIn(name, names)
            self.assertIn(name, ALL_FUNCTIONS)


class TestSprint2Recurring(unittest.TestCase):
    """Sprint 2: 2 tools (recurring + attachments)."""

    def test_recurring_module_has_2_tools(self):
        from dexter.tools.recurring import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 2)
        self.assertEqual(len(FUNCTIONS), 2)

    def test_recurring_all_registered(self):
        expected = ["crear_recurringtransaction", "adjuntar_archivo"]
        from dexter.tools.recurring import SCHEMA, FUNCTIONS
        names = {_schema_name(s) for s in SCHEMA}
        for name in expected:
            self.assertIn(name, names, f"recurring missing {name}")
            self.assertIn(name, FUNCTIONS)

    def test_recurring_in_global_registry(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        names = {_schema_name(s) for s in ALL_SCHEMAS}
        for name in ["crear_recurringtransaction", "adjuntar_archivo"]:
            self.assertIn(name, names)
            self.assertIn(name, ALL_FUNCTIONS)

    def test_crear_recurringtransaction_has_intervalo(self):
        from dexter.tools.recurring import SCHEMA
        for s in SCHEMA:
            if _schema_name(s) == "crear_recurringtransaction":
                props = s["function"]["parameters"]["properties"]
                self.assertIn("intervalo", props)
                self.assertIn("enum", props["intervalo"])

    def test_adjuntar_archivo_required_params(self):
        from dexter.tools.recurring import SCHEMA
        for s in SCHEMA:
            if _schema_name(s) == "adjuntar_archivo":
                params = s["function"]["parameters"]
                required = params.get("required", [])
                self.assertIn("ruta_archivo", required)
                self.assertIn("tipo_entidad", required)
                self.assertIn("id_entidad", required)


class TestSprint3Advanced(unittest.TestCase):
    """Sprint 3: 6 tools P2 (TaxCode, TaxRate, ExchangeRate, Batch, CDC, Budget)."""

    def test_advanced_module_has_6_tools(self):
        from dexter.tools.advanced import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 6)
        self.assertEqual(len(FUNCTIONS), 6)

    def test_advanced_all_registered(self):
        expected = [
            "crear_taxcode", "crear_taxrate", "leer_exchange_rate",
            "ejecutar_batch", "cdc_query", "crear_budget",
        ]
        from dexter.tools.advanced import SCHEMA, FUNCTIONS
        names = {_schema_name(s) for s in SCHEMA}
        for name in expected:
            self.assertIn(name, names, f"advanced missing {name}")
            self.assertIn(name, FUNCTIONS)

    def test_advanced_in_global_registry(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        names = {_schema_name(s) for s in ALL_SCHEMAS}
        for name in ["crear_taxcode", "ejecutar_batch", "cdc_query", "crear_budget"]:
            self.assertIn(name, names)
            self.assertIn(name, ALL_FUNCTIONS)

    def test_ejecutar_batch_max_30_items(self):
        from dexter.tools.advanced import SCHEMA
        for s in SCHEMA:
            if _schema_name(s) == "ejecutar_batch":
                ops = s["function"]["parameters"]["properties"]["operaciones"]
                self.assertEqual(ops.get("maxItems"), 30)

    def test_crear_taxrate_required_tasa(self):
        from dexter.tools.advanced import SCHEMA
        for s in SCHEMA:
            if _schema_name(s) == "crear_taxrate":
                required = s["function"]["parameters"]["required"]
                self.assertIn("nombre", required)
                self.assertIn("tasa", required)


class TestSprintTotalCoverage(unittest.TestCase):
    """Tests de cobertura global: 100 tools, 21 módulos."""

    def test_total_100_tools(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        self.assertEqual(len(ALL_SCHEMAS), 100)
        self.assertEqual(len(ALL_FUNCTIONS), 100)

    def test_total_21_modules(self):
        from dexter.tools import KEYWORDS_BY_MODULE
        self.assertEqual(len(KEYWORDS_BY_MODULE), 21)

    def test_all_new_tools_have_descriptions(self):
        from dexter.tools import ALL_SCHEMAS
        new_tools = [
            "crear_vendor", "crear_billpayment", "actualizar_cliente",
            "eliminar_transaccion", "reporte_trial_balance", "leer_companyinfo",
            "crear_recurringtransaction", "crear_taxcode", "ejecutar_batch",
        ]
        names = {_schema_name(s): s for s in ALL_SCHEMAS}
        for name in new_tools:
            self.assertIn(name, names, f"{name} missing from registry")
            desc = names[name]["function"].get("description", "")
            self.assertGreater(len(desc), 30, f"{name} has too-short description")

    def test_all_new_tools_have_well_formed_params(self):
        from dexter.tools import ALL_SCHEMAS
        for s in ALL_SCHEMAS:
            name = _schema_name(s)
            if name.startswith("crear_") or name.startswith("actualizar_") or name.startswith("reporte_") or name.startswith("leer_") or name.startswith("eliminar_") or name.startswith("void_") or name.startswith("desactivar_") or name.startswith("enviar_") or name.startswith("consulta_") or name.startswith("adjuntar_") or name.startswith("cdc_") or name.startswith("ejecutar_"):
                params = s["function"].get("parameters", {})
                self.assertEqual(params.get("type"), "object", f"{name} parameters.type must be 'object'")
                self.assertIsInstance(params.get("properties"), dict, f"{name} missing 'properties' dict")


class TestP2OptionalReports(unittest.TestCase):
    """P2 opcionales: 6 reportes faltantes (gaps 49-53 + reabastecimiento)."""

    def test_p2_reports_in_reports_extra(self):
        from dexter.tools.reports_extra import SCHEMA, FUNCTIONS
        expected = [
            "reporte_inventory_valuation",
            "reporte_sales_by_customer",
            "reporte_expenses_by_vendor",
            "reporte_transaction_list",
            "reporte_class_sales",
            "reporte_department_sales",
        ]
        names = {_schema_name(s) for s in SCHEMA}
        for name in expected:
            self.assertIn(name, names, f"reports_extra missing {name}")
            self.assertIn(name, FUNCTIONS, f"reports_extra FUNCTIONS missing {name}")

    def test_reports_extra_module_has_16_tools(self):
        from dexter.tools.reports_extra import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 16)
        self.assertEqual(len(FUNCTIONS), 16)

    def test_p2_reports_in_global_registry(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        names = {_schema_name(s) for s in ALL_SCHEMAS}
        for name in [
            "reporte_inventory_valuation",
            "reporte_sales_by_customer",
            "reporte_expenses_by_vendor",
            "reporte_transaction_list",
            "reporte_class_sales",
            "reporte_department_sales",
        ]:
            self.assertIn(name, names, f"{name} missing from global registry")
            self.assertIn(name, ALL_FUNCTIONS)

    def test_p2_reports_callable(self):
        from dexter.tools import ALL_FUNCTIONS
        from main import (
            tool_reporte_inventory_valuation,
            tool_reporte_sales_by_customer,
            tool_reporte_expenses_by_vendor,
            tool_reporte_transaction_list,
            tool_reporte_class_sales,
            tool_reporte_department_sales,
        )
        self.assertIs(ALL_FUNCTIONS["reporte_inventory_valuation"], tool_reporte_inventory_valuation)
        self.assertIs(ALL_FUNCTIONS["reporte_sales_by_customer"], tool_reporte_sales_by_customer)
        self.assertIs(ALL_FUNCTIONS["reporte_expenses_by_vendor"], tool_reporte_expenses_by_vendor)
        self.assertIs(ALL_FUNCTIONS["reporte_transaction_list"], tool_reporte_transaction_list)
        self.assertIs(ALL_FUNCTIONS["reporte_class_sales"], tool_reporte_class_sales)
        self.assertIs(ALL_FUNCTIONS["reporte_department_sales"], tool_reporte_department_sales)

    def test_total_100_tools(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        self.assertEqual(len(ALL_SCHEMAS), 100)
        self.assertEqual(len(ALL_FUNCTIONS), 100)

    def test_p2_reports_have_descriptions(self):
        from dexter.tools import ALL_SCHEMAS
        new_tools = [
            "reporte_inventory_valuation",
            "reporte_sales_by_customer",
            "reporte_expenses_by_vendor",
            "reporte_transaction_list",
            "reporte_class_sales",
            "reporte_department_sales",
        ]
        names = {_schema_name(s): s for s in ALL_SCHEMAS}
        for name in new_tools:
            self.assertIn(name, names)
            desc = names[name]["function"].get("description", "")
            self.assertGreater(len(desc), 30, f"{name} has too-short description")


class TestVerifyToolIntegrity(unittest.TestCase):
    """Tests para la safeguard verify_tool_integrity (Layer 1)."""

    def setUp(self):
        import main
        self._main = main
        self._injected_names = []

    def tearDown(self):
        for name in self._injected_names:
            if hasattr(self._main, name):
                delattr(self._main, name)

    def _inject(self, name: str, fn):
        setattr(self._main, name, fn)
        self._injected_names.append(name)

    def test_result_keys_present(self):
        from dexter.tools import verify_tool_integrity
        result = verify_tool_integrity(verbose=False)
        for key in ("ok", "total_wrappers", "total_registered", "orphans", "registered_unwired"):
            self.assertIn(key, result)

    def test_baseline_no_orphans(self):
        from dexter.tools import verify_tool_integrity
        result = verify_tool_integrity(verbose=False)
        self.assertTrue(result["ok"], f"Baseline should be clean. Got: {result}")
        self.assertEqual(result["orphans"], [])
        self.assertEqual(result["registered_unwired"], [])

    def test_detects_injected_orphan(self):
        from dexter.tools import verify_tool_integrity
        self._inject("tool_test_orphan_injected", lambda: None)
        result = verify_tool_integrity(verbose=False)
        self.assertFalse(result["ok"])
        self.assertIn("tool_test_orphan_injected", result["orphans"])

    def test_verbose_writes_to_stderr_on_failure(self):
        import io
        from dexter.tools import verify_tool_integrity
        self._inject("tool_test_verbose_orphan", lambda: None)
        captured = io.StringIO()
        import sys
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            verify_tool_integrity(verbose=True)
        finally:
            sys.stderr = old_stderr
        output = captured.getvalue()
        self.assertIn("DEXTER TOOLS INTEGRITY CHECK FAILED", output)
        self.assertIn("tool_test_verbose_orphan", output)
        self.assertIn("Acción", output)

    def test_verbose_silent_when_ok(self):
        import io
        import sys
        from dexter.tools import verify_tool_integrity
        captured = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = captured
        try:
            verify_tool_integrity(verbose=True)
        finally:
            sys.stderr = old_stderr
        self.assertEqual(captured.getvalue(), "")

    def test_total_wrappers_count(self):
        from dexter.tools import verify_tool_integrity
        result = verify_tool_integrity(verbose=False)
        self.assertEqual(result["total_wrappers"], result["total_registered"])

    def test_result_keys_include_dispatch_check(self):
        from dexter.tools import verify_tool_integrity
        result = verify_tool_integrity(verbose=False)
        for key in ("not_dispatched", "total_dispatched"):
            self.assertIn(key, result)

    def test_all_schemas_are_dispatched(self):
        """Cada schema expuesto al LLM debe tener un entry en TOOL_FUNCTIONS.
        Si no, el LLM llama el tool y main.py responde 'Tool no encontrado'
        → 'límite de iteraciones' → usuario frustrado.
        Bug que motivó esta verificación: 'crear_cliente' faltaba en TOOL_FUNCTIONS
        (definido en main.py + schema en dexter/tools/transactions.py, pero no
        registrado en el dispatch table)."""
        from dexter.tools import verify_tool_integrity
        result = verify_tool_integrity(verbose=False)
        self.assertEqual(
            result["not_dispatched"], [],
            f"Hay {len(result['not_dispatched'])} schemas sin dispatch: "
            f"{result['not_dispatched']}"
        )

    def test_verbose_dispatch_failure_mentions_dispatch(self):
        import io
        import sys
        from dexter.tools import verify_tool_integrity
        # Forzar un gap: registrar un tool pero NO agregarlo a TOOL_FUNCTIONS
        from dexter.tools import ALL_SCHEMAS
        from dexter.tools import _extract_name
        # Tomar un nombre de schema que SÍ esté dispatched y simular que no
        # (monkey-patching en main.TOOL_FUNCTIONS)
        import main
        if main.TOOL_FUNCTIONS:
            sample_key = next(iter(main.TOOL_FUNCTIONS))
            if sample_key in main.TOOL_FUNCTIONS:
                saved = main.TOOL_FUNCTIONS.pop(sample_key)
                try:
                    captured = io.StringIO()
                    old = sys.stderr
                    sys.stderr = captured
                    try:
                        verify_tool_integrity(verbose=True)
                    finally:
                        sys.stderr = old
                    self.assertIn("dispatch", captured.getvalue().lower())
                finally:
                    main.TOOL_FUNCTIONS[sample_key] = saved


if __name__ == "__main__":
    unittest.main()
