"""Tests para LOW-8: tool_execute_python debe sandboxar exec().

Bug: autonomia/autonomia_nivel3_code_executor.py:15 — execute_llm_code
     hace exec(code, context or {}, local_vars) sin sandbox. Con
     context={} (default) el LLM puede:
       - import os / subprocess / shutil
       - os.system("rm -rf /")
       - __import__('subprocess').run(['rm','-rf','/'])
       - open('/etc/passwd').read()
       - socket.socket() → exfiltrate data
       - while True: pass (sin timeout)
     Es un riesgo de seguridad: código generado por LLM (o prompt
     injection) puede ejecutar comandos arbitrarios con los permisos
     del usuario que corre dexter.

Fix: sandbox via restricted __builtins__ + whitelist de módulos seguros
     (math, json, datetime, statistics, collections, decimal, re).
     Bloquear builtins peligrosos: __import__, exec, eval, compile,
     open, input, globals, locals, vars. Timeout via threading.Timer
     que mata el thread o via signal.alarm (solo main thread Unix).
     Para tests, usar threading.Thread con join(timeout).
"""
import unittest
import os
import time


class TestExecutePythonSandbox(unittest.TestCase):
    """LOW-8: tool_execute_python está sandboxed."""

    def setUp(self):
        from autonomia.autonomia_nivel3_code_executor import execute_llm_code
        self.execute_llm_code = execute_llm_code

    def test_simple_arithmetic_still_works(self):
        """GREEN backward compat: 2+2 sigue retornando result=4."""
        r = self.execute_llm_code("result = 2 + 2")
        self.assertTrue(r["success"])
        self.assertEqual(r["return_value"], 4)

    def test_blocks_dangerous_imports(self):
        """RED: import os debe fallar dentro del sandbox."""
        r = self.execute_llm_code("import os; result = os.listdir('/')")
        self.assertFalse(r["success"])
        self.assertIn("error", r)

    def test_blocks_subprocess(self):
        """GREEN: __import__('subprocess') debe fallar."""
        r = self.execute_llm_code(
            "__import__('subprocess').run(['echo', 'pwned'])"
        )
        self.assertFalse(r["success"])

    def test_blocks_eval(self):
        """GREEN: eval() debe estar bloqueado."""
        r = self.execute_llm_code("result = eval('1+1')")
        self.assertFalse(r["success"])

    def test_blocks_exec(self):
        """GREEN: exec() anidado debe estar bloqueado."""
        r = self.execute_llm_code("exec('result = 1+1')")
        self.assertFalse(r["success"])

    def test_allows_safe_module_math(self):
        """GREEN backward compat: import math funciona."""
        r = self.execute_llm_code("import math; result = math.sqrt(16)")
        self.assertTrue(r["success"])
        self.assertEqual(r["return_value"], 4.0)

    def test_allows_safe_module_json(self):
        """GREEN: import json funciona."""
        r = self.execute_llm_code(
            "import json; result = json.dumps({'a': 1})"
        )
        self.assertTrue(r["success"])
        self.assertEqual(r["return_value"], '{"a": 1}')

    def test_allows_safe_module_datetime(self):
        """GREEN: import datetime funciona."""
        r = self.execute_llm_code(
            "import datetime; result = datetime.date(2026,1,1).isoformat()"
        )
        self.assertTrue(r["success"])
        self.assertEqual(r["return_value"], "2026-01-01")

    def test_captures_stdout(self):
        """GREEN backward compat: print() se captura."""
        r = self.execute_llm_code("print('hello'); result = 42")
        self.assertTrue(r["success"])
        self.assertIn("hello", r["stdout"])
        self.assertEqual(r["return_value"], 42)

    def test_captures_syntax_error(self):
        """GREEN backward compat: SyntaxError se captura."""
        r = self.execute_llm_code("this is not python")
        self.assertFalse(r["success"])
        self.assertIn("error", r)

    def test_captures_runtime_error(self):
        """GREEN backward compat: 1/0 → ZeroDivisionError."""
        r = self.execute_llm_code("result = 1/0")
        self.assertFalse(r["success"])
        self.assertIn("division by zero", r["error"].lower())


class TestExecutePythonTimeout(unittest.TestCase):
    """LOW-8: tool_execute_python tiene timeout."""

    def test_infinite_loop_times_out(self):
        """RED: while True debe ser interrumpido por timeout."""
        from autonomia.autonomia_nivel3_code_executor import execute_llm_code
        t0 = time.time()
        r = execute_llm_code("while True: pass")
        elapsed = time.time() - t0
        self.assertFalse(r["success"])
        self.assertLess(elapsed, 10.0)
        self.assertTrue(
            any(k in str(r.get("error", "")).lower() for k in ["timeout", "time limit", "interrupted"]),
            f"Expected timeout error, got: {r}"
        )


if __name__ == "__main__":
    unittest.main()
