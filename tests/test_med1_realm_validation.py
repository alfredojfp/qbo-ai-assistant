"""Tests para MED-1: QB_BASE_URL debe construirse con realm_id validado.

Bug: main.py:99 — `QB_BASE_URL = f".../{QB_REALM_ID}"` con QB_REALM_ID
     de os.getenv(). Si env var missing, QB_REALM_ID=None, la URL
     queda ".../company/None" → falla con error confuso en runtime.

Fix: helper `_build_qb_base_url(realm_id)` valida y construye. La
     asignación module-level usa el helper con mensaje claro si missing.
     Función pura testeable sin reload de módulo.
"""
import os
import unittest


class TestBuildQbBaseUrl(unittest.TestCase):
    """MED-1: _build_qb_base_url debe validar realm_id."""

    def test_valid_realm_id_constructs_url(self):
        """GREEN: con realm_id válido, la URL lo incluye."""
        from main import _build_qb_base_url
        url = _build_qb_base_url("9341455870833544")
        self.assertIn("9341455870833544", url)
        self.assertNotIn("None", url)

    def test_missing_realm_id_returns_placeholder(self):
        """Sin realm_id, retorna URL placeholder (no crashea al importar)."""
        from main import _build_qb_base_url
        result = _build_qb_base_url(None)
        self.assertIn("REALM_ID_PENDING", result)
        self.assertIn("sandbox-quickbooks", result)

    def test_empty_realm_id_returns_placeholder(self):
        """Realm_id vacío, retorna URL placeholder."""
        from main import _build_qb_base_url
        result = _build_qb_base_url("")
        self.assertIn("REALM_ID_PENDING", result)

    def test_sandbox_url_pattern(self):
        """GREEN: el patrón URL es intuitivamente correcto."""
        from main import _build_qb_base_url
        url = _build_qb_base_url("12345")
        self.assertTrue(url.startswith("https://"))
        self.assertIn("/v3/company/12345", url)


if __name__ == "__main__":
    unittest.main()
