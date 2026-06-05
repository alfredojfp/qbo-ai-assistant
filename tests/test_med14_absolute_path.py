"""Tests para MED-14: buscar_pdf_en_pending_bills debe aceptar absolute path.

Bug: main.py:4930-4937 — si user pasa nombre_archivo='/abs/path/x.pdf',
     la función solo busca por basename en la carpeta 'Pending bills'.
     Si el PDF está en otra ubicación (e.g., /tmp, /home/user/Downloads),
     no se encuentra aunque el path absoluto sea válido.

Fix: si nombre_archivo es absolute path y existe, retornarlo directo.
     Si no, fallback al comportamiento actual (search en Pending bills
     por basename parcial).
"""
import os
import tempfile
import unittest
from unittest.mock import patch


class TestBuscarPdfAbsolutePath(unittest.TestCase):
    """MED-14: buscar_pdf_en_pending_bills debe aceptar absolute path."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_absolute_path_existing_file_returned_directly(self):
        """RED: absolute path que existe debe retornarse directo sin buscar en Pending bills."""
        from main import buscar_pdf_en_pending_bills

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            tmp_path = f.name

        try:
            result = buscar_pdf_en_pending_bills(tmp_path)
            self.assertEqual(result, tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_absolute_path_nonexistent_raises(self):
        """RED: absolute path que NO existe debe raise FileNotFoundError."""
        from main import buscar_pdf_en_pending_bills

        fake_path = "/tmp/nonexistent_unique_xyz_12345.pdf"
        with self.assertRaises(FileNotFoundError):
            buscar_pdf_en_pending_bills(fake_path)

    def test_partial_name_searches_in_pending_bills(self):
        """GREEN: nombre parcial sigue buscando en Pending bills folder (backward compat)."""
        from main import buscar_pdf_en_pending_bills

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "factura_acme.pdf")
            with open(pdf_path, "wb") as f:
                f.write(b"%PDF-1.4\n")

            with patch("main.os.path.exists", return_value=True), \
                 patch("main.glob.glob", return_value=[pdf_path]):
                result = buscar_pdf_en_pending_bills("acme")
                self.assertEqual(result, pdf_path)


if __name__ == "__main__":
    unittest.main()
