"""dexter.testing.llm_mock — DeepseekMock para tests de conversación.

R-10: mock realista del LLM deepseek (vía OpenRouter API) que simula
peculiaridades del modelo real:
  - JSON malformado en tool_call.arguments
  - Tool calls a funciones inexistentes (alucinaciones)
  - Rate limits (429) y timeouts (408)
  - Contenido vacío
  - Truncamiento
  - Respuestas scripted por call # (multi-turn)

Uso en tests:
    from dexter.testing.llm_mock import DeepseekMock

    def test_algo(self):
        mock = DeepseekMock()
        mock.set_text("Hola, ¿en qué te ayudo?")

        with patch("main.requests.post", side_effect=mock):
            result = main.call_llm("hola")
            self.assertIn("Hola", result)

    def test_tool_call_flow(self):
        mock = DeepseekMock()
        mock.set_responses([
            {"tool_call": ("tool_buscar_cliente", {"nombre": "Alfredo"})},
            {"text": "Encontré 1 cliente."},
        ])
        with patch("main.requests.post", side_effect=mock):
            main.call_llm("buscar cliente Alfredo")
            self.assertEqual(mock.call_count, 2)
"""
from __future__ import annotations

import json
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Union


def _make_response(status_code: int, body: Optional[Dict] = None,
                   text: str = "") -> Any:
    """Construye un objeto response-like (compatible con requests.Response)."""
    class _Resp:
        def __init__(self, status_code, body, text):
            self.status_code = status_code
            self._body = body or {}
            self.text = text

        def json(self):
            return self._body

    return _Resp(status_code, body, text)


def _default_text_response() -> Dict:
    """Respuesta default con text content."""
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "deepseek/deepseek-chat",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Entendido. ¿Qué necesitas?",
            },
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 8,
            "total_tokens": 18,
        },
    }


def _tool_call_response(name: str, arguments: Dict[str, Any],
                        malformed: bool = False) -> Dict:
    """Respuesta con un tool_call. Si malformed=True, arguments es JSON inválido."""
    if malformed:
        args_str = "{invalid json: missing quotes"
    else:
        args_str = json.dumps(arguments, ensure_ascii=False)

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "deepseek/deepseek-chat",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": args_str,
                    },
                }],
            },
            "finish_reason": "tool_calls",
        }],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70,
        },
    }


class DeepseekMock:
    """Mock callable del LLM deepseek para tests.

    Configurar respuestas via:
      - set_text(content)          # 1 respuesta con content
      - add_tool_call(name, args)  # 1 tool call (acumulable)
      - add_hallucinated_tool_call(name, args)  # tool call a fn inexistente
      - set_responses([...])       # script de respuestas por call #
      - enable_malformed_json()    # arguments inválido en próximo tool call
      - enable_rate_limit()        # 429 en próxima call
      - enable_timeout()           # 408 en próxima call

    Inspeccionar después:
      - mock.call_count            # número de calls
      - mock.captured_messages     # lista de messages[] enviados
    """

    def __init__(self):
        self.call_count = 0
        self.captured_messages: List[List[Dict]] = []

        self._text_response: Optional[str] = None
        self._tool_calls: List[Dict] = []
        self._scripted_responses: Optional[List[Dict]] = None
        self._malformed_next = False
        self._rate_limit_next = False
        self._timeout_next = False
        self._scripted_index = 0

    def set_text(self, content: str) -> None:
        """Configura la respuesta con text content."""
        self._text_response = content

    def add_tool_call(self, name: str, arguments: Dict[str, Any]) -> None:
        """Agrega un tool call a la respuesta (acumulable)."""
        self._tool_calls.append({"name": name, "args": arguments, "hallucinated": False})

    def add_hallucinated_tool_call(self, name: str, arguments: Dict[str, Any]) -> None:
        """Agrega un tool call a una función INEXISTENTE (simula alucinación)."""
        self._tool_calls.append({"name": name, "args": arguments, "hallucinated": True})

    def set_responses(self, responses: List[Dict]) -> None:
        """Configura script de respuestas. Cada item es un dict:
        {"text": "..."} o {"tool_call": (name, args)} o {"rate_limit": True}.
        """
        self._scripted_responses = responses
        self._scripted_index = 0

    def enable_malformed_json(self) -> None:
        """El próximo tool call tendrá arguments = JSON inválido."""
        self._malformed_next = True

    def enable_rate_limit(self) -> None:
        """La próxima call retorna 429."""
        self._rate_limit_next = True

    def enable_timeout(self) -> None:
        """La próxima call retorna 408 (timeout)."""
        self._timeout_next = True

    def __call__(self, *args, **kwargs) -> Any:
        """Callable interface (compatible con requests.post side_effect).

        Extrae messages de los kwargs o args. Retorna un response-like.
        """
        self.call_count += 1

        messages = kwargs.get("messages")
        if messages is None:
            messages = kwargs.get("json", {}).get("messages")
        if messages is None and args:
            for a in args:
                if isinstance(a, dict) and "messages" in a:
                    messages = a["messages"]
                    break
        if messages is None:
            messages = []
        self.captured_messages.append(messages)

        if self._rate_limit_next:
            self._rate_limit_next = False
            return _make_response(
                429,
                body={"error": {"message": "Rate limit exceeded", "type": "rate_limit"}},
                text="Rate limit exceeded. Please retry after 1s.",
            )

        if self._timeout_next:
            self._timeout_next = False
            return _make_response(
                408,
                body={"error": {"message": "Request timeout"}},
                text="Request timeout after 30s.",
            )

        if self._scripted_responses is not None:
            return self._next_scripted()

        if self._tool_calls:
            tcs = self._tool_calls
            self._tool_calls = []
            body = _tool_call_response(
                tcs[0]["name"], tcs[0]["args"], malformed=self._malformed_next,
            )
            if len(tcs) > 1:
                for tc in tcs[1:]:
                    body["choices"][0]["message"]["tool_calls"].append({
                        "id": f"call_{uuid.uuid4().hex[:8]}",
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["args"], ensure_ascii=False)
                                if not self._malformed_next
                                else "{invalid",
                        },
                    })
            self._malformed_next = False
            return _make_response(200, body=body)

        if self._text_response is not None:
            body = _default_text_response()
            body["choices"][0]["message"]["content"] = self._text_response
            return _make_response(200, body=body)

        return _make_response(200, body=_default_text_response())

    def _next_scripted(self) -> Any:
        """Sirve la próxima respuesta scripted."""
        if self._scripted_index >= len(self._scripted_responses):
            return _make_response(200, body=_default_text_response())
        item = self._scripted_responses[self._scripted_index]
        self._scripted_index += 1

        if "rate_limit" in item and item["rate_limit"]:
            return _make_response(
                429,
                body={"error": {"message": "Rate limit"}},
                text="Rate limit",
            )
        if "timeout" in item and item["timeout"]:
            return _make_response(408, text="Timeout")
        if "tool_call" in item:
            name, args = item["tool_call"]
            return _make_response(
                200, body=_tool_call_response(name, args, malformed=self._malformed_next),
            )
        if "text" in item:
            body = _default_text_response()
            body["choices"][0]["message"]["content"] = item["text"]
            return _make_response(200, body=body)
        return _make_response(200, body=_default_text_response())
