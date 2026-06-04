"""Tests para dexter.tools — registry agregador y módulos individuales."""
import unittest


class TestBankFeedModule(unittest.TestCase):
    """Tests para dexter.tools.bank_feed (4 tools del bank feed intelligence)."""

    def test_module_imports(self):
        from dexter.tools import bank_feed
        self.assertTrue(hasattr(bank_feed, "SCHEMA"))
        self.assertTrue(hasattr(bank_feed, "FUNCTIONS"))

    def test_schema_count_matches_functions_count(self):
        from dexter.tools.bank_feed import SCHEMA, FUNCTIONS
        self.assertEqual(len(SCHEMA), 4)
        self.assertEqual(len(FUNCTIONS), 4)

    def test_schema_function_names_match(self):
        from dexter.tools.bank_feed import SCHEMA, FUNCTIONS
        schema_names = {s["name"] for s in SCHEMA}
        function_names = set(FUNCTIONS.keys())
        self.assertEqual(schema_names, function_names)

    def test_expected_tool_names(self):
        from dexter.tools.bank_feed import SCHEMA
        names = {s["name"] for s in SCHEMA}
        self.assertEqual(
            names,
            {
                "analizarbankfeed",
                "registrarclasificacion",
                "estadisticasclasificacion",
                "buscarpatron",
            },
        )

    def test_each_function_is_callable(self):
        from dexter.tools.bank_feed import FUNCTIONS
        for name, fn in FUNCTIONS.items():
            self.assertTrue(callable(fn), f"{name} is not callable")

    def test_each_schema_has_required_fields(self):
        from dexter.tools.bank_feed import SCHEMA
        for s in SCHEMA:
            self.assertIn("name", s)
            self.assertIn("description", s)
            self.assertIn("parameters", s)
            self.assertEqual(s["parameters"]["type"], "object")
            self.assertIn("properties", s["parameters"])

    def test_descriptions_are_substantive(self):
        """Una description <30 chars probablemente no explica qué retorna."""
        from dexter.tools.bank_feed import SCHEMA
        for s in SCHEMA:
            self.assertGreater(
                len(s["description"]),
                30,
                f"Tool '{s['name']}' description too short: {s['description']!r}",
            )


class TestToolsAggregator(unittest.TestCase):
    """Tests para dexter.tools.__init__ (registry agregador)."""

    def test_all_schemas_imports(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        self.assertIsInstance(ALL_SCHEMAS, list)
        self.assertIsInstance(ALL_FUNCTIONS, dict)

    def test_no_duplicate_names(self):
        from dexter.tools import ALL_SCHEMAS
        names = [s["name"] for s in ALL_SCHEMAS]
        self.assertEqual(len(names), len(set(names)), "Duplicate tool names")

    def test_every_schema_has_matching_function(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        for s in ALL_SCHEMAS:
            self.assertIn(
                s["name"],
                ALL_FUNCTIONS,
                f"Schema '{s['name']}' has no matching function",
            )
            self.assertTrue(callable(ALL_FUNCTIONS[s["name"]]))

    def test_every_function_has_matching_schema(self):
        from dexter.tools import ALL_SCHEMAS, ALL_FUNCTIONS
        schema_names = {s["name"] for s in ALL_SCHEMAS}
        for fn_name in ALL_FUNCTIONS:
            self.assertIn(
                fn_name,
                schema_names,
                f"Function '{fn_name}' has no matching schema",
            )


if __name__ == "__main__":
    unittest.main()
