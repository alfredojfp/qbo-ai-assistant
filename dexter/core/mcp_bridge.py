"""MCPBridge: Python ↔ Node.js JSON-RPC over stdio.

HIGH-3: bridges Dexter (Python) to Intuit's official quickbooks-online-mcp-server
        (Node.js) via the Model Context Protocol (JSON-RPC 2.0 over stdio).
"""
import json
import os
import subprocess
import threading
from typing import Any, Dict, List, Optional


class MCPBridgeError(Exception):
    """Error from the MCP bridge or the underlying MCP server."""
    pass


class MCPBridge:
    """Manages a Node.js MCP server subprocess with JSON-RPC communication."""

    def __init__(self, mcp_dir: str, env: Dict[str, str] = None):
        self._mcp_dir = mcp_dir
        self._env = env or {}
        self._proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._id_counter = 0
        self._initialized = False

    def start(self):
        if self._proc is not None:
            return
        node_cmd = self._env.get("NODE_PATH", "node")
        server_path = os.path.join(self._mcp_dir, "dist", "index.js")
        if not os.path.exists(server_path):
            raise MCPBridgeError(
                f"MCP server not found at {server_path}. Run install.sh first."
            )
        proc_env = {**os.environ, **self._env}
        try:
            self._proc = subprocess.Popen(
                [node_cmd, server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=proc_env,
            )
        except FileNotFoundError:
            raise MCPBridgeError("Node.js not found. Install Node.js >= 20.")
        self._initialize()

    def stop(self):
        if self._proc is None:
            return
        try:
            self._proc.stdin.close()
            self._proc.stdout.close()
            if self._proc.stderr:
                self._proc.stderr.close()
        except Exception:
            pass
        try:
            self._proc.terminate()
            self._proc.wait(timeout=5)
        except Exception:
            self._proc.kill()
        finally:
            self._proc = None
        self._initialized = False

    def call_tool(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self._initialized:
            raise MCPBridgeError("MCP bridge not initialized. Call start() first.")
        args = {"params": arguments or {}}
        response = self._send("tools/call", {"name": name, "arguments": args})
        content = response.get("content", [])
        if not content:
            return {}
        text = content[0].get("text", "{}")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}

    def list_tools(self) -> List[Dict[str, Any]]:
        if not self._initialized:
            raise MCPBridgeError("MCP bridge not initialized. Call start() first.")
        response = self._send("tools/list", {})
        return response.get("tools", [])

    def _next_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    def _initialize(self):
        self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "dexter", "version": "5.0.0"},
        })
        self._notify("notifications/initialized", {})
        self._initialized = True

    def _notify(self, method: str, params: Dict[str, Any]):
        """Send a JSON-RPC notification (no id, no response expected)."""
        msg = json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        })
        with self._lock:
            self._proc.stdin.write(msg + "\n")
            self._proc.stdin.flush()

    def _send(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        request_id = self._next_id()
        msg = self._format_request(request_id, method, params)
        with self._lock:
            self._proc.stdin.write(msg + "\n")
            self._proc.stdin.flush()
            line = self._proc.stdout.readline()
            if not line:
                stderr_data = ""
                if self._proc.stderr:
                    stderr_data = self._proc.stderr.read()
                raise MCPBridgeError(
                    f"MCP server closed connection. stderr: {stderr_data[:500]}"
                )
        return self._parse_response(line)

    @staticmethod
    def _format_request(request_id: int, method: str, params: Dict[str, Any]) -> str:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        })

    @staticmethod
    def _parse_response(line: str) -> Dict[str, Any]:
        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            raise MCPBridgeError(
                f"Invalid JSON response: {e}. Raw: {line[:200]}"
            )
        if "error" in data:
            err = data["error"]
            raise MCPBridgeError(
                f"MCP error {err.get('code')}: {err.get('message')}"
            )
        if "result" not in data:
            raise MCPBridgeError(f"No result in response: {data}")
        return data["result"]
