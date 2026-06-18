"""Tests for MCPBridge — Python JSON-RPC client for Intuit MCP Server."""
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dexter.core.mcp_bridge import MCPBridge, MCPBridgeError


class TestMCPBridgeProtocol(unittest.TestCase):
    """Test JSON-RPC message parsing and formatting (no subprocess)."""

    def test_tools_list_response_parsed(self):
        raw = (
            '{"jsonrpc":"2.0","id":1,"result":{"tools":['
            '{"name":"search_customers","description":"Search customers",'
            '"inputSchema":{"type":"object","properties":{"searchTerm":{"type":"string"}},'
            '"required":["searchTerm"]}}]}}\n'
        )
        result = MCPBridge._parse_response(raw)
        self.assertEqual(len(result["tools"]), 1)
        self.assertEqual(result["tools"][0]["name"], "search_customers")

    def test_tools_call_response_parsed(self):
        raw = (
            '{"jsonrpc":"2.0","id":2,"result":{"content":['
            '{"type":"text","text":"{\\"Customer\\":{\\"Id\\":\\"42\\",'
            '\\"DisplayName\\":\\"ACME\\"}}"}]}}\n'
        )
        result = MCPBridge._parse_response(raw)
        self.assertIn("content", result)
        self.assertEqual(result["content"][0]["type"], "text")

    def test_error_response_raises_mcp_error(self):
        raw = (
            '{"jsonrpc":"2.0","id":3,"error":'
            '{"code":-32601,"message":"Method not found"}}\n'
        )
        with self.assertRaises(MCPBridgeError) as ctx:
            MCPBridge._parse_response(raw)
        self.assertIn("Method not found", str(ctx.exception))

    def test_parse_invalid_json_raises(self):
        with self.assertRaises(MCPBridgeError):
            MCPBridge._parse_response("not json\n")

    def test_request_format_is_valid_jsonrpc(self):
        msg = MCPBridge._format_request(
            1, "tools/call",
            {"name": "get_deposit", "arguments": {"id": "123"}},
        )
        parsed = json.loads(msg)
        self.assertEqual(parsed["jsonrpc"], "2.0")
        self.assertEqual(parsed["method"], "tools/call")
        self.assertEqual(parsed["id"], 1)
        self.assertEqual(parsed["params"]["name"], "get_deposit")

    def test_format_request_no_params(self):
        msg = MCPBridge._format_request(5, "tools/list", {})
        parsed = json.loads(msg)
        self.assertEqual(parsed["id"], 5)
        self.assertEqual(parsed["params"], {})

    def test_call_tool_without_start_raises(self):
        bridge = MCPBridge("/nonexistent")
        with self.assertRaises(MCPBridgeError):
            bridge.call_tool("test", {})

    def test_list_tools_without_start_raises(self):
        bridge = MCPBridge("/nonexistent")
        with self.assertRaises(MCPBridgeError):
            bridge.list_tools()

    def test_start_server_not_found_raises(self):
        bridge = MCPBridge("/nonexistent/path")
        with self.assertRaises(MCPBridgeError) as ctx:
            bridge.start()
        self.assertIn("not found", str(ctx.exception))


class TestMCPBridgeIntegration(unittest.TestCase):
    """Integration: spawns real Intuit MCP subprocess (no QBO network required)."""

    def test_start_and_list_tools_in_sandbox_mode(self):
        mcp_dir = os.path.join(
            os.path.dirname(__file__), "..", "vendor", "quickbooks-online-mcp-server"
        )
        if not os.path.exists(mcp_dir):
            self.skipTest("Intuit MCP not installed. Run install.sh first.")
        bridge = MCPBridge(mcp_dir, env={
            "QUICKBOOKS_CLIENT_ID": "test",
            "QUICKBOOKS_CLIENT_SECRET": "test",
            "QUICKBOOKS_REFRESH_TOKEN": "test",
            "QUICKBOOKS_REALM_ID": "test",
            "QUICKBOOKS_ENVIRONMENT": "sandbox",
        })
        try:
            bridge.start()
            tools = bridge.list_tools()
            self.assertGreaterEqual(len(tools), 100)
            self.assertTrue(any(t["name"] == "search_customers" for t in tools))
            self.assertTrue(any(t["name"] == "create_deposit" for t in tools))
            self.assertTrue(any(t["name"] == "create_customer" for t in tools))
        finally:
            bridge.stop()
