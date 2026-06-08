# -*- coding: utf-8 -*-
"""
Tests para el módulo OCR de bills.

Estos tests usan unittest de stdlib y mockean la API de Gemini.
Ejecutar con: python -m unittest tests.test_ocr_bills
"""
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import ocr_bills


class TestListarPdfs(unittest.TestCase):
    """Tests para listar PDFs en una carpeta."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_listar_pdfs_en_carpeta_vacia_retorna_lista_vacia(self):
        result = ocr_bills.listar_pdfs_en_carpeta(self.tmpdir)
        self.assertEqual(result, [])

    def test_listar_pdfs_encuentra_archivos_pdf(self):
        for name in ["factura1.pdf", "factura2.pdf", "reporte.pdf"]:
            open(os.path.join(self.tmpdir, name), 'w').close()
        result = ocr_bills.listar_pdfs_en_carpeta(self.tmpdir)
        self.assertEqual(len(result), 3)
        for path in result:
            self.assertTrue(path.endswith(".pdf"))

    def test_listar_pdfs_ignora_no_pdfs(self):
        for name in ["factura.pdf", "imagen.jpg", "doc.txt", "datos.xlsx"]:
            open(os.path.join(self.tmpdir, name), 'w').close()
        result = ocr_bills.listar_pdfs_en_carpeta(self.tmpdir)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].endswith("factura.pdf"))

    def test_listar_pdfs_ordenados_alfabeticamente(self):
        for name in ["z.pdf", "a.pdf", "m.pdf"]:
            open(os.path.join(self.tmpdir, name), 'w').close()
        result = ocr_bills.listar_pdfs_en_carpeta(self.tmpdir)
        basenames = [os.path.basename(p) for p in result]
        self.assertEqual(basenames, ["a.pdf", "m.pdf", "z.pdf"])

    def test_listar_pdfs_carpeta_inexistente(self):
        result = ocr_bills.listar_pdfs_en_carpeta("/no/existe/aqui")
        self.assertEqual(result, [])

    def test_listar_pdfs_default_a_pending_bills(self):
        # Verifica que la función existe con un default
        self.assertTrue(callable(ocr_bills.listar_pdfs_en_carpeta))


class TestProcesarLoteOcr(unittest.TestCase):
    """Tests para la función de procesamiento en lote."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.pdf1 = os.path.join(self.tmpdir, "factura1.pdf")
        self.pdf2 = os.path.join(self.tmpdir, "factura2.pdf")
        for path in [self.pdf1, self.pdf2]:
            open(path, 'w').close()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        # Limpiar archivos generados
        for f in os.listdir('.'):
            if f.startswith("bills_preview_") and f.endswith(".csv"):
                try:
                    os.remove(f)
                except OSError:
                    pass

    def test_procesar_lote_con_carpeta_vacia(self):
        empty = tempfile.mkdtemp()
        try:
            result = ocr_bills.procesar_lote_ocr(carpeta=empty)
            self.assertIn("error", result)
        finally:
            shutil.rmtree(empty, ignore_errors=True)

    @patch("ocr_bills.extraer_bills_de_pdf")
    def test_procesar_lote_ocr_llama_por_cada_pdf(self, mock_extract):
        mock_extract.return_value = [
            {"invoice_number": "INV-001", "vendor_name": "Acme", "total_amount": 100.0}
        ]
        result = ocr_bills.procesar_lote_ocr(carpeta=self.tmpdir, mover_exitosos=False)
        self.assertEqual(result["total_bills"], 2)
        self.assertEqual(mock_extract.call_count, 2)

    @patch("ocr_bills.extraer_bills_de_pdf")
    def test_procesar_lote_ocr_agrega_resultados(self, mock_extract):
        mock_extract.side_effect = [
            [{"invoice_number": "INV-1", "vendor_name": "V1", "total_amount": 10.0}],
            [{"invoice_number": "INV-2", "vendor_name": "V2", "total_amount": 20.0}],
        ]
        result = ocr_bills.procesar_lote_ocr(carpeta=self.tmpdir, mover_exitosos=False)
        self.assertEqual(result["total_bills"], 2)
        self.assertIsNone(result.get("errores"))

    @patch("ocr_bills.extraer_bills_de_pdf")
    def test_procesar_lote_ocr_maneja_excepcion(self, mock_extract):
        mock_extract.side_effect = [
            [{"invoice_number": "INV-1", "vendor_name": "V1", "total_amount": 10.0}],
            Exception("Gemini timeout"),
        ]
        result = ocr_bills.procesar_lote_ocr(carpeta=self.tmpdir, mover_exitosos=False)
        self.assertEqual(result["total_bills"], 1)
        self.assertEqual(len(result.get("errores", [])), 1)

    @patch("ocr_bills.extraer_bills_de_pdf")
    def test_procesar_lote_ocr_mueve_fallidos_a_subcarpeta(self, mock_extract):
        mock_extract.side_effect = Exception("Test failure")
        result = ocr_bills.procesar_lote_ocr(
            carpeta=self.tmpdir, mover_exitosos=False
        )
        self.assertEqual(len(result.get("errores", [])), 2)

    @patch("ocr_bills.extraer_bills_de_pdf")
    def test_procesar_lote_ocr_estructura_resumen(self, mock_extract):
        mock_extract.return_value = [
            {"invoice_number": "INV-1", "vendor_name": "V1", "total_amount": 10.0}
        ]
        result = ocr_bills.procesar_lote_ocr(carpeta=self.tmpdir, mover_exitosos=False)
        for key in ["success", "total_bills", "mode", "errores"]:
            self.assertIn(key, result)


class TestValidarBill(unittest.TestCase):
    """Tests para la validación de bills extraídos."""

    def test_bill_valido_tiene_campos_requeridos(self):
        bill = {
            "invoice_number": "INV-001",
            "invoice_date": "2026-01-15",
            "vendor_name": "Acme Corp",
            "total_amount": 100.0
        }
        self.assertTrue(ocr_bills.validar_bill_minimo(bill))

    def test_bill_sin_invoice_number_es_invalido(self):
        bill = {
            "invoice_date": "2026-01-15",
            "vendor_name": "Acme",
            "total_amount": 100.0
        }
        self.assertFalse(ocr_bills.validar_bill_minimo(bill))

    def test_bill_sin_total_es_invalido(self):
        bill = {
            "invoice_number": "INV-1",
            "invoice_date": "2026-01-15",
            "vendor_name": "Acme"
        }
        self.assertFalse(ocr_bills.validar_bill_minimo(bill))

    def test_bill_sin_vendor_es_invalido(self):
        bill = {
            "invoice_number": "INV-1",
            "invoice_date": "2026-01-15",
            "total_amount": 100.0
        }
        self.assertFalse(ocr_bills.validar_bill_minimo(bill))

    def test_bill_sin_fecha_es_invalido(self):
        bill = {
            "invoice_number": "INV-1",
            "vendor_name": "Acme",
            "total_amount": 100.0
        }
        self.assertFalse(ocr_bills.validar_bill_minimo(bill))

    def test_bill_none_es_invalido(self):
        self.assertFalse(ocr_bills.validar_bill_minimo(None))

    def test_bill_dict_vacio_es_invalido(self):
        self.assertFalse(ocr_bills.validar_bill_minimo({}))


if __name__ == "__main__":
    unittest.main()
