"""Tests para LOW-4: load_chart_of_accounts cache con schema_version.

Bug: main.py:447 — load_chart_of_accounts cachea en chartofaccounts.json
     SIN schema_version. Si cambiamos la estructura interna
     (e.g., agregamos campo 'currency' o renombramos 'subtype' a
     'sub_type'), el cache viejo se carga y los tools fallan con
     KeyError. La única salida es `force_refresh=True`, pero los
     usuarios no siempre lo saben.

Fix: cache incluye 'schema_version' y 'company_realm_id'. Si el
     schema_version del cache no coincide con CHART_SCHEMA_VERSION
     (constante módulo), o si el realm_id difiere, IGNORAR el cache
     y re-descargar de QBO.
"""
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock, mock_open


class TestChartCacheSchemaVersion(unittest.TestCase):
    """LOW-4: load_chart_of_accounts respeta schema_version del cache."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_schema_version_constant_exists(self):
        """RED: main debe exportar CHART_SCHEMA_VERSION."""
        import main
        self.assertTrue(hasattr(main, "CHART_SCHEMA_VERSION"))
        self.assertIsInstance(main.CHART_SCHEMA_VERSION, int)

    def test_stale_cache_ignored(self):
        """GREEN: cache con schema_version viejo se ignora y re-descarga."""
        from main import load_chart_of_accounts
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump({
                "schema_version": 0,  # stale
                "company_realm_id": "9341455870833544",
                "last_updated": "2026-06-01T00:00:00",
                "accounts": {"fake": {"id": "fake", "name": "Old"}}
            }, f)
            tmp = f.name
        try:
            with patch("main.FILE_CHART_CACHE", tmp), \
                 patch("main.qbo_query", return_value={"QueryResponse": {"Account": []}}) as mock_q:
                result = load_chart_of_accounts(force_refresh=False)
                mock_q.assert_called_once()
        finally:
            os.unlink(tmp)

    def test_different_realm_ignored(self):
        """GREEN: cache de OTRA empresa se ignora (realm_id diferente)."""
        from main import load_chart_of_accounts
        import main
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump({
                "schema_version": main.CHART_SCHEMA_VERSION,
                "company_realm_id": "DIFFERENT_REALM",
                "last_updated": "2026-06-01T00:00:00",
                "accounts": {"fake": {"id": "fake", "name": "Other Company"}}
            }, f)
            tmp = f.name
        try:
            with patch("main.FILE_CHART_CACHE", tmp), \
                 patch("main.qbo_query", return_value={"QueryResponse": {"Account": []}}) as mock_q:
                load_chart_of_accounts(force_refresh=False)
                mock_q.assert_called_once()
        finally:
            os.unlink(tmp)

    def test_valid_cache_loaded(self):
        """GREEN: cache con schema_version correcto Y mismo realm Y < 24h se carga."""
        from main import load_chart_of_accounts
        import main
        from datetime import datetime
        accounts = {"1": {"id": "1", "name": "Bank"}}
        recent = datetime.now().isoformat()
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump({
                "schema_version": main.CHART_SCHEMA_VERSION,
                "company_realm_id": "9341455870833544",
                "last_updated": recent,
                "accounts": accounts
            }, f)
            tmp = f.name
        try:
            with patch("main.FILE_CHART_CACHE", tmp), \
                 patch("main.qbo_query") as mock_q:
                result = load_chart_of_accounts(force_refresh=False)
                mock_q.assert_not_called()
                self.assertEqual(result, accounts)
        finally:
            os.unlink(tmp)

    def test_cache_written_with_new_schema(self):
        """GREEN: al guardar, el cache incluye schema_version actual."""
        from main import load_chart_of_accounts
        import main
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            tmp = f.name
        try:
            with patch("main.FILE_CHART_CACHE", tmp), \
                 patch("main.qbo_query", return_value={"QueryResponse": {"Account": []}}):
                load_chart_of_accounts(force_refresh=True)
            with open(tmp) as f:
                data = json.load(f)
            self.assertEqual(data["schema_version"], main.CHART_SCHEMA_VERSION)
            self.assertEqual(data["company_realm_id"], "9341455870833544")
        finally:
            os.unlink(tmp)


if __name__ == "__main__":
    unittest.main()
