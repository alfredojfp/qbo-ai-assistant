# -*- coding: utf-8 -*-
import sys
import io
import traceback
from typing import Dict, Any
from contextlib import redirect_stdout, redirect_stderr

def execute_llm_code(code: str, context: Dict = None) -> Dict:
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            local_vars = {}
            exec(code, context or {}, local_vars)

        return {
            "success": True,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "variables": {k: str(v) for k, v in local_vars.items() if not k.startswith('_')},
            "return_value": local_vars.get('result', None)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue()
        }

def tool_execute_python(code: str) -> dict:
    return execute_llm_code(code)
