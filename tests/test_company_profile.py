"""Tests para company profile automático (UX-3).

Al cargar una empresa por primera vez, Dexter estudia QBO y genera
un PROFILE.md con: chart of accounts, P&L, clientes, vendors,
invoices recientes, y cuentas bancarias.

Este perfil se inyecta en el system prompt para que Dexter conozca
la empresa desde el minuto 0.
"""
import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestCompanyProfile(unittest.TestCase):
    """UX-3: generación automática de perfil de empresa."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_profile_generated_when_not_exists(self):
        """RED: si no existe PROFILE.md, se genera automáticamente."""
        import main
        profile_path = Path(self.tmp) / "PROFILE.md"

        # Mock qbo_query para devolver datos simulados
        def fake_qbo(query):
            q = query.upper()
            if "COUNT(*) FROM ACCOUNT" in q:
                return {"QueryResponse": {"totalCount": 91}}
            if "ACCOUNTTYPE" in q:
                return {"QueryResponse": {
                    "Account": [
                        {"AccountType": "Bank", "Name": "Checking"},
                        {"AccountType": "Income", "Name": "Sales"},
                    ],
                    "totalCount": 2,
                }}
            if "COUNT(*) FROM CUSTOMER" in q:
                return {"QueryResponse": {"totalCount": 12}}
            if "COUNT(*) FROM VENDOR" in q:
                return {"QueryResponse": {"totalCount": 8}}
            if "INVOICE" in q:
                return {"QueryResponse": {"Invoice": [], "totalCount": 5}}
            if "ESTIMATE" in q:
                return {"QueryResponse": {"Estimate": [], "totalCount": 0}}
            return {"QueryResponse": {"totalCount": 0}}

        def fake_report(name, start, end, **kw):
            return {
                "Header": {"ReportName": name},
                "Rows": {"Row": []},
            }

        with patch("main.qbo_query", side_effect=fake_qbo), \
             patch("main._fetch_report", side_effect=fake_report), \
             patch("main.CURRENT_COMPANY", {"name": "TestCo", "realm_id": "123"}):
            main._generate_company_profile(profile_dir=str(self.tmp))

        self.assertTrue(profile_path.exists(), "PROFILE.md debe generarse")
        content = profile_path.read_text()
        self.assertIn("TestCo", content)
        self.assertIn("91", content)  # cuentas
        self.assertIn("12", content)  # clientes

    def test_profile_not_regenerated_if_exists(self):
        """Si PROFILE.md ya existe, no se regenera automáticamente."""
        import main
        profile_path = Path(self.tmp) / "PROFILE.md"
        profile_path.write_text("Perfil existente")
        mtime_before = profile_path.stat().st_mtime

        with patch("main.qbo_query") as mock_qbo, \
             patch("main._fetch_report") as mock_report, \
             patch("main.CURRENT_COMPANY", {"name": "TestCo", "realm_id": "123"}):
            main._generate_company_profile(profile_dir=str(self.tmp))

        self.assertEqual(profile_path.read_text(), "Perfil existente")
        self.assertEqual(profile_path.stat().st_mtime, mtime_before)
        mock_qbo.assert_not_called()

    def test_profile_force_refresh(self):
        """Con force=True, se regenera aunque exista."""
        import main
        profile_path = Path(self.tmp) / "PROFILE.md"
        profile_path.write_text("Viejo")

        with patch("main.qbo_query", return_value={"QueryResponse": {"totalCount": 50}}), \
             patch("main._fetch_report", return_value={"Header": {}, "Rows": {"Row": []}}), \
             patch("main.CURRENT_COMPANY", {"name": "TestCo", "realm_id": "123"}):
            main._generate_company_profile(profile_dir=str(self.tmp), force=True)

        self.assertIn("50", profile_path.read_text())

    def test_profile_loaded_into_memory(self):
        """El perfil se carga en memoria al iniciar la empresa."""
        import main
        profile_path = Path(self.tmp) / "PROFILE.md"
        profile_path.write_text("Perfil de TestCo: 50 cuentas, 10 clientes")

        result = main._load_company_profile(profile_dir=str(self.tmp))
        self.assertIn("TestCo", result)
        self.assertIn("50", result)

    def test_profile_empty_when_no_file(self):
        """Sin PROFILE.md, retorna string vacío."""
        import main
        result = main._load_company_profile(profile_dir=self.tmp)
        self.assertEqual(result, "")

    def test_full_profile_content_structure(self):
        """El perfil generado tiene secciones claras."""
        import main
        profile_path = Path(self.tmp) / "PROFILE.md"

        def fake_qbo(query):
            return {"QueryResponse": {"totalCount": 99}}

        def fake_report(name, start, end, **kw):
            return {"Header": {"ReportName": name}, "Rows": {"Row": []}}

        with patch("main.qbo_query", side_effect=fake_qbo), \
             patch("main._fetch_report", side_effect=fake_report), \
             patch("main.CURRENT_COMPANY", {"name": "Empresa", "realm_id": "456"}):
            main._generate_company_profile(profile_dir=str(self.tmp))

        content = profile_path.read_text()
        self.assertIn("Perfil de Empresa", content)
        self.assertIn("Chart of Accounts", content)
        self.assertIn("99", content)
