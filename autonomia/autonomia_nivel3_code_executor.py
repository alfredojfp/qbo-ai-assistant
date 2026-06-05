# -*- coding: utf-8 -*-
"""LOW-8: Sandboxed Python code executor.

Executes LLM-generated Python code in a restricted environment that:
- Blocks dangerous builtins (exec, eval, __import__, open, input, etc.)
- Whitelists safe modules (math, json, datetime, statistics, etc.)
- Has a soft timeout (returns error, may leak thread on infinite loop)

Hardening rationale: code ejecutable por LLM es un riesgo de seguridad.
Un prompt injection podría hacer os.system('rm -rf /') o exfiltrate
data. El sandbox limita blast radius.
"""
import sys
import io
import time
import traceback
import builtins
import threading
from typing import Dict, Any
from contextlib import redirect_stdout, redirect_stderr


SAFE_MODULES = frozenset({
    "math",
    "cmath",
    "json",
    "datetime",
    "time",
    "calendar",
    "collections",
    "statistics",
    "decimal",
    "fractions",
    "re",
    "string",
    "itertools",
    "functools",
    "operator",
    "typing",
})


def _build_safe_globals() -> dict:
    """Construye globals con builtins restringidos + whitelist de módulos.

    Bloquea builtins peligrosos: __import__, exec, eval, compile, open,
    input, globals, locals, vars, breakpoint, help, exit, quit, copyright.
    Permite solo módulos en SAFE_MODULES (math, json, datetime, etc.).
    """
    safe_builtins = {
        k: getattr(builtins, k)
        for k in (
            "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes",
            "callable", "chr", "complex", "dict", "divmod", "enumerate",
            "filter", "float", "format", "frozenset", "hash", "hex", "id",
            "int", "isinstance", "issubclass", "iter", "len", "list", "map",
            "max", "min", "next", "object", "oct", "ord", "pow", "print",
            "range", "repr", "reversed", "round", "set", "slice", "sorted",
            "str", "sum", "tuple", "type", "zip", "True", "False", "None",
            "BaseException", "Exception", "ValueError", "TypeError",
            "ZeroDivisionError", "KeyError", "IndexError", "AttributeError",
            "RuntimeError", "StopIteration", "NotImplementedError",
            "ArithmeticError", "LookupError", "NameError", "OSError",
        )
        if hasattr(builtins, k)
    }

    def _safe_import(name, *args, **kwargs):
        if name in SAFE_MODULES:
            return __import__(name, *args, **kwargs)
        raise ImportError(
            f"Import of '{name}' is blocked by sandbox. "
            f"Allowed modules: {sorted(SAFE_MODULES)}"
        )

    safe_builtins["__import__"] = _safe_import

    safe_globals = {
        "__builtins__": safe_builtins,
        "__name__": "__dexter_sandbox__",
        "__doc__": None,
    }

    for mod_name in SAFE_MODULES:
        try:
            safe_globals[mod_name] = __import__(mod_name)
        except ImportError:
            pass

    return safe_globals


def _run_with_timeout(code: str, safe_globals: dict, local_vars: dict,
                     stdout_capture: io.StringIO,
                     stderr_capture: io.StringIO,
                     timeout: float) -> tuple:
    """Ejecuta code en thread. Retorna (success, error_msg, timed_out)."""
    result = {"success": False, "error": None, "timed_out": False}

    def target():
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, safe_globals, local_vars)
            result["success"] = True
        except Exception as e:
            result["error"] = (
                f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            )

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        result["timed_out"] = True
        result["error"] = f"Execution exceeded time limit of {timeout}s"
        return False, result["error"], True

    return result["success"], result["error"], False


def execute_llm_code(code: str, context: Dict = None,
                     timeout: float = 5.0) -> Dict:
    """Ejecuta código Python en sandbox.

    Args:
        code: código Python a ejecutar
        context: ignorado en sandboxed mode (compat hacia atrás)
        timeout: segundos máximos antes de abortar (default 5.0)

    Returns:
        dict con success, stdout, stderr, variables, return_value
        o success=False, error, traceback en caso de fallo.
    """
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    local_vars = {}

    safe_globals = _build_safe_globals()

    success, error, timed_out = _run_with_timeout(
        code, safe_globals, local_vars,
        stdout_capture, stderr_capture,
        timeout=timeout,
    )

    if success:
        return {
            "success": True,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "variables": {k: str(v) for k, v in local_vars.items() if not k.startswith('_')},
            "return_value": local_vars.get('result', None)
        }

    tb = "" if timed_out else traceback.format_exc()
    return {
        "success": False,
        "error": error or "Unknown error",
        "traceback": tb,
        "stdout": stdout_capture.getvalue(),
        "stderr": stderr_capture.getvalue(),
        "timed_out": timed_out,
    }


def tool_execute_python(code: str) -> dict:
    """Tool: ejecuta código Python del LLM en sandbox."""
    return execute_llm_code(code)
