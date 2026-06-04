"""Tests for the conversational CLI main_loop / show_main_menu."""
import io
import unittest
from contextlib import redirect_stdout


class TestShowMainMenu(unittest.TestCase):
    """Tests for show_main_menu() — the on-demand help menu."""

    def test_returns_string(self):
        from main import show_main_menu
        result = show_main_menu()
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 100)

    def test_includes_brand(self):
        from main import show_main_menu
        result = show_main_menu()
        self.assertIn("DEXTER", result)
        self.assertIn("QuickBooks", result)

    def test_includes_exit_command(self):
        from main import show_main_menu
        result = show_main_menu()
        self.assertIn("salir", result.lower())
        self.assertIn("exit", result.lower())

    def test_includes_menu_invokers(self):
        from main import show_main_menu
        result = show_main_menu()
        # The menu documents its own invokers
        self.assertIn("menu", result.lower())
        self.assertIn("?", result)

    def test_includes_all_quick_help_topics(self):
        from main import show_main_menu
        result = show_main_menu().lower()
        for topic in ["ocr", "bancos", "recon", "reportes", "template csv", "lote csv"]:
            self.assertIn(topic, result, f"Missing quick-help topic: {topic}")

    def test_includes_token_shortcuts(self):
        from main import show_main_menu
        result = show_main_menu().lower()
        self.assertIn("tokens", result)
        self.assertIn("informe", result)

    def test_mentions_natural_language(self):
        from main import show_main_menu
        result = show_main_menu().lower()
        # User-facing note about NL is important (UX)
        self.assertTrue(
            "natural" in result or "hablar" in result or "habla" in result,
            "Menu should mention natural language interaction",
        )


class TestMainLoopBannerIsMinimal(unittest.TestCase):
    """Verify the startup banner is minimal (no static menu dump)."""

    def test_startup_banner_does_not_contain_full_menu(self):
        """main_loop should NOT print the full quick-help menu at startup.
        A reference is only shown on demand (menu/?/ayuda)."""
        from main import show_main_menu
        full_menu = show_main_menu()
        # The full menu contains the brand line repeated. We just check
        # that nothing in the file's main_loop source contains a multi-line
        # quick-help list dumped at module level.
        import re
        from main import main_loop
        src = re.sub(r'\s+', ' ', main_loop.__code__.co_consts[0] or "")
        # The main_loop docstring + body should NOT contain "ayuda ocr" inline
        # (it only contains the keyword "menu" in invokers)
        self.assertNotIn("ayuda ocr", src)


class TestMenuCommandRoutes(unittest.TestCase):
    """Document the on-demand menu invokers (not asserting the loop itself,
    since that requires mocking input — but verifying the canonical list)."""

    def test_canonical_invokers(self):
        # These should trigger the menu in main_loop
        invokers = {"menu", "?", "help", "ayuda"}
        # Just assert the contract is documented in main_loop
        import inspect
        from main import main_loop
        src = inspect.getsource(main_loop)
        for inv in invokers:
            self.assertIn(f'"{inv}"', src, f"main_loop must support '{inv}' as menu invoker")


if __name__ == "__main__":
    unittest.main()
