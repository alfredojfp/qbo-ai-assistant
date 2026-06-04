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

    def test_count_is_43(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        self.assertEqual(len(ALL_SCHEMAS), 43)
        self.assertEqual(len(ALL_FUNCTIONS), 43)

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
        ("transactions", 4),
        ("reports", 5),
        ("tokens", 2),
        ("admin", 2),
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


if __name__ == "__main__":
    unittest.main()
