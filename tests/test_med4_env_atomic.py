"""Tests para MED-4: update_env_file debe escribir atómicamente.

Bug: main.py:186-187 — update_env_file hace open(path, 'w') y
     f.writelines(lines) directamente. Si el proceso muere a mitad
     de write, .env queda truncado/corrupto.

Fix: escribir a .env.tmp primero, luego os.replace(tmp, real) que
     es atómico en POSIX. Garantiza que .env siempre queda en un
     estado consistente (viejo o nuevo, nunca parcial).
"""
import os
import unittest
from unittest.mock import patch, mock_open, MagicMock


class TestUpdateEnvFileAtomic(unittest.TestCase):
    """MED-4: update_env_file debe ser atómico via tmp+rename."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_uses_temp_file_then_replace(self):
        """RED: la implementación debe usar .env.tmp + os.replace (no open directo)."""
        from main import update_env_file

        with patch("os.path.exists", return_value=False), \
             patch("builtins.open", mock_open()) as mock_file, \
             patch("os.replace") as mock_replace, \
             patch("os.remove") as mock_remove:
            update_env_file("NEW_KEY", "new_value")

        mock_replace.assert_called_once()
        call_args = mock_replace.call_args
        self.assertIn(".tmp", call_args[0][0],
                      "Source debe ser .env.tmp; recibió: " + str(call_args[0][0]))

    def test_new_key_added(self):
        """GREEN: key nueva se agrega al .env."""
        from main import update_env_file

        with patch("os.path.exists", return_value=False), \
             patch("builtins.open", mock_open()) as mock_file, \
             patch("os.replace"), \
             patch("os.remove"):
            update_env_file("FOO", "bar")
            handle = mock_file()
            written = "".join(
                item
                for call in handle.writelines.call_args_list
                for item in (call.args[0] if call.args else [])
            )
            self.assertIn("FOO=bar", written)

    def test_existing_key_updated_preserves_others(self):
        """GREEN: key existente se actualiza, las demás se preservan."""
        from main import update_env_file

        existing_content = "FOO=old\nBAR=keep\n"

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=existing_content)) as mock_file, \
             patch("os.replace"), \
             patch("os.remove"):
            update_env_file("FOO", "new")

            handle = mock_file()
            written = "".join(
                item
                for call in handle.writelines.call_args_list
                for item in (call.args[0] if call.args else [])
            )
            self.assertIn("FOO=new", written)
            self.assertIn("BAR=keep", written)


if __name__ == "__main__":
    unittest.main()
