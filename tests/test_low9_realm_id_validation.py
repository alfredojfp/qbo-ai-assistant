"""Tests para LOW-9: extract_realm_id debe validar input estrictamente.

Bug: company_manager.py:26 — extract_realm_id usa regex r'(\d{10,})'
     que captura CUALQUIER secuencia de 10+ dígitos en el string.
     Esto es demasiado permisivo:
       - 'Transaction ID 1234567890123456' → matchea el txn ID
       - 'phone 15551234567' → matchea el teléfono
       - 'timestamp 1640995200' → matchea el timestamp Unix
       - '1234567890123456ABCDEF' → matchea el número dentro
     QBO realm IDs son típicamente 16 dígitos y vienen solos o en
     URLs companyId=. Cualquier otra cosa es input malformado.

Fix: helper _is_valid_realm_id(s) que valida:
     - 10-20 dígitos (rango razonable que cubre 10, 12, 16)
     - String completo es solo dígitos (después de strip)
     - URL pattern: companyId=<digits>
     Rechaza: teléfono, timestamp, transaction ID, mixed alphanumeric.
"""
import unittest


class TestExtractRealmIdValid(unittest.TestCase):
    """LOW-9: extract_realm_id acepta inputs válidos."""

    def test_pure_realm_id_16_digits(self):
        """GREEN: 16 dígitos puros (típico QBO)."""
        from company_manager import extract_realm_id
        self.assertEqual(
            extract_realm_id("9341455870833544"),
            "9341455870833544",
        )

    def test_pure_realm_id_12_digits(self):
        """GREEN: 12 dígitos también válido."""
        from company_manager import extract_realm_id
        self.assertEqual(extract_realm_id("462081636528"), "462081636528")

    def test_pure_realm_id_10_digits(self):
        """GREEN: 10 dígitos es el mínimo aceptable."""
        from company_manager import extract_realm_id
        self.assertEqual(extract_realm_id("4620816365"), "4620816365")

    def test_pure_realm_id_20_digits(self):
        """GREEN: hasta 20 dígitos aceptable."""
        from company_manager import extract_realm_id
        self.assertEqual(
            extract_realm_id("12345678901234567890"),
            "12345678901234567890",
        )

    def test_url_with_company_id(self):
        """GREEN: URL con companyId=... se extrae."""
        from company_manager import extract_realm_id
        self.assertEqual(
            extract_realm_id("https://app.qbo.intuit.com/app/homepage?companyId=9341455870833544"),
            "9341455870833544",
        )

    def test_url_short_company_id(self):
        """GREEN: URL con companyId corto (10 dígitos)."""
        from company_manager import extract_realm_id
        self.assertEqual(
            extract_realm_id("https://qbo.example.com?companyId=4620816365"),
            "4620816365",
        )

    def test_whitespace_around_pure_id(self):
        """GREEN: espacios alrededor se ignoran."""
        from company_manager import extract_realm_id
        self.assertEqual(
            extract_realm_id("  9341455870833544  "),
            "9341455870833544",
        )

    def test_empty_returns_none(self):
        """GREEN backward compat: empty → None."""
        from company_manager import extract_realm_id
        self.assertIsNone(extract_realm_id(""))

    def test_none_returns_none(self):
        """GREEN backward compat: None → None."""
        from company_manager import extract_realm_id
        self.assertIsNone(extract_realm_id(None))


class TestExtractRealmIdRejects(unittest.TestCase):
    """LOW-9: extract_realm_id rechaza inputs malformados."""

    def test_rejects_phone_number(self):
        """RED: número de teléfono (10-11 dígitos con espacios) NO matchea."""
        from company_manager import extract_realm_id
        self.assertIsNone(extract_realm_id("+1 555 123 4567"))

    def test_rejects_unix_timestamp(self):
        """RED: timestamp Unix 1640995200 (10 dígitos) NO debe matchear
        cuando hay texto alrededor sugiriendo contexto no-QBO."""
        from company_manager import extract_realm_id
        self.assertIsNone(extract_realm_id("timestamp: 1640995200"))

    def test_rejects_transaction_id_with_label(self):
        """RED: 'Transaction ID 1234567890123456' NO matchea."""
        from company_manager import extract_realm_id
        self.assertIsNone(extract_realm_id("Transaction ID 1234567890123456"))

    def test_rejects_too_short(self):
        """RED: 9 dígitos es muy corto."""
        from company_manager import extract_realm_id
        self.assertIsNone(extract_realm_id("123456789"))

    def test_rejects_too_long(self):
        """RED: 21+ dígitos es muy largo (no es QBO válido)."""
        from company_manager import extract_realm_id
        self.assertIsNone(extract_realm_id("123456789012345678901"))

    def test_rejects_alphanumeric_mix(self):
        """RED: '1234567890ABCDEF' NO matchea (alfanumérico)."""
        from company_manager import extract_realm_id
        self.assertIsNone(extract_realm_id("1234567890ABCDEF"))

    def test_rejects_letters_only(self):
        """RED: solo letras → None."""
        from company_manager import extract_realm_id
        self.assertIsNone(extract_realm_id("notarealmid"))

    def test_rejects_natural_language_with_embedded_number(self):
        """RED: 'I have 16 customers who paid me 1234567890123456' NO matchea."""
        from company_manager import extract_realm_id
        self.assertIsNone(
            extract_realm_id("I have 16 customers who paid me 1234567890123456")
        )

    def test_rejects_credit_card_number_with_label(self):
        """RED: 'card 1234567890123456' NO matchea."""
        from company_manager import extract_realm_id
        self.assertIsNone(extract_realm_id("card 1234567890123456"))


if __name__ == "__main__":
    unittest.main()
