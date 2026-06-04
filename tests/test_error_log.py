"""Tests para dexter.error_log — sistema centralizado de logging de errores."""
import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


class TestErrorLogModule(unittest.TestCase):
    """Tests del módulo dexter.error_log."""

    def setUp(self):
        """Redirige LOG_DIR a un tmpdir antes de cada test."""
        self.tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmp.name)
        # Patch LOG_DIR antes de importar el módulo
        import importlib
        import dexter.error_log as el
        importlib.reload(el)
        el.LOG_DIR = self.tmpdir
        el.LOG_FILE = self.tmpdir / "dexter_errors.log"
        el._initialized = False  # reset handler
        el.setup_logging()

    def tearDown(self):
        import dexter.error_log as el
        el.clear_log()
        self.tmp.cleanup()

    def test_log_dir_exists_after_setup(self):
        import dexter.error_log as el
        self.assertTrue(el.LOG_DIR.exists())
        self.assertTrue(el.LOG_DIR.is_dir())

    def test_log_file_creates_on_first_error(self):
        import dexter.error_log as el
        el.clear_log()
        try:
            raise ValueError("test error")
        except ValueError as e:
            el.log_error(e, category="test")
        self.assertTrue(el.LOG_FILE.exists())

    def test_log_entry_is_json_line(self):
        import dexter.error_log as el
        el.clear_log()
        try:
            raise ValueError("primera falla")
        except ValueError as e:
            el.log_error(e, category="test", user_input="hola", tool_name="test_tool")
        content = el.LOG_FILE.read_text(encoding="utf-8")
        lines = [l for l in content.strip().split("\n") if l]
        self.assertEqual(len(lines), 1)
        entry = json.loads(lines[0])
        for required in ("timestamp", "level", "category", "error_type",
                         "message", "stack_trace"):
            self.assertIn(required, entry)
        self.assertEqual(entry["category"], "test")
        self.assertEqual(entry["user_input"], "hola")
        self.assertEqual(entry["tool_name"], "test_tool")
        self.assertEqual(entry["error_type"], "ValueError")
        self.assertEqual(entry["message"], "primera falla")
        self.assertIn("ValueError", entry["stack_trace"])

    def test_multiple_errors_append_not_overwrite(self):
        import dexter.error_log as el
        el.clear_log()
        for msg in ("primero", "segundo", "tercero"):
            try:
                raise RuntimeError(msg)
            except RuntimeError as e:
                el.log_error(e, category="test")
        content = el.LOG_FILE.read_text(encoding="utf-8")
        lines = [l for l in content.strip().split("\n") if l]
        self.assertEqual(len(lines), 3)
        msgs = [json.loads(l)["message"] for l in lines]
        self.assertEqual(msgs, ["primero", "segundo", "tercero"])

    def test_timestamp_is_iso8601(self):
        import dexter.error_log as el
        el.clear_log()
        try:
            raise ValueError("ts check")
        except ValueError as e:
            el.log_error(e, category="test")
        entry = json.loads(el.LOG_FILE.read_text().strip())
        # Verifica que es parseable como ISO 8601
        parsed = datetime.fromisoformat(entry["timestamp"])
        self.assertIsNotNone(parsed)

    def test_get_recent_errors_returns_list(self):
        import dexter.error_log as el
        el.clear_log()
        for i in range(5):
            try:
                raise ValueError(f"err {i}")
            except ValueError as e:
                el.log_error(e, category="test")
        recent = el.get_recent_errors(n=3)
        self.assertEqual(len(recent), 3)
        self.assertEqual([r["message"] for r in recent], ["err 2", "err 3", "err 4"])

    def test_get_recent_errors_default_n(self):
        import dexter.error_log as el
        el.clear_log()
        for i in range(25):
            try:
                raise ValueError(f"err {i}")
            except ValueError as e:
                el.log_error(e, category="test")
        recent = el.get_recent_errors()
        self.assertEqual(len(recent), 20)  # default

    def test_clear_log_empties_file(self):
        import dexter.error_log as el
        try:
            raise ValueError("a borrar")
        except ValueError as e:
            el.log_error(e, category="test")
        self.assertTrue(el.LOG_FILE.exists())
        el.clear_log()
        self.assertFalse(el.LOG_FILE.exists())

    def test_extra_field_is_preserved(self):
        import dexter.error_log as el
        el.clear_log()
        try:
            raise ValueError("con contexto")
        except ValueError as e:
            el.log_error(e, category="api_call",
                         extra={"status_code": 400, "endpoint": "/customer"})
        entry = json.loads(el.LOG_FILE.read_text().strip())
        self.assertIn("extra", entry)
        self.assertEqual(entry["extra"]["status_code"], 400)
        self.assertEqual(entry["extra"]["endpoint"], "/customer")

    def test_company_field_is_optional(self):
        import dexter.error_log as el
        el.clear_log()
        try:
            raise ValueError("sin empresa")
        except ValueError as e:
            el.log_error(e, category="test", company="Mi Empresa SA")
        entry = json.loads(el.LOG_FILE.read_text().strip())
        self.assertEqual(entry["company"], "Mi Empresa SA")

    def test_log_error_with_string_message(self):
        """Acepta tanto una excepción como un string de mensaje."""
        import dexter.error_log as el
        el.clear_log()
        el.log_error("algo salió mal", category="test", user_input="test")
        entry = json.loads(el.LOG_FILE.read_text().strip())
        self.assertEqual(entry["message"], "algo salió mal")
        self.assertEqual(entry["error_type"], "UnknownError")

    def test_tail_log_returns_human_readable(self):
        import dexter.error_log as el
        el.clear_log()
        try:
            raise ValueError("error legible")
        except ValueError as e:
            el.log_error(e, category="api_call", tool_name="buscar_cliente")
        output = el.tail_log(n=10)
        self.assertIn("ValueError", output)
        self.assertIn("error legible", output)
        self.assertIn("api_call", output)
        self.assertIn("buscar_cliente", output)

    def test_categories(self):
        """Las categorías esperadas son las definidas por el módulo."""
        import dexter.error_log as el
        self.assertIn("api_call", el.CATEGORIES)
        self.assertIn("tool_dispatch", el.CATEGORIES)
        self.assertIn("user_input", el.CATEGORIES)
        self.assertIn("auth", el.CATEGORIES)
        self.assertIn("unknown", el.CATEGORIES)


if __name__ == "__main__":
    unittest.main()
