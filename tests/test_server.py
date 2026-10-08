"""Test MCP server setup."""

import pytest

from mcp_rag.server import create_server, create_tools


class TestServerSetup:
    def test_create_tools(self) -> None:
        tools = create_tools()
        assert len(tools) == 4
        names = {t.name for t in tools}
        assert names == {
            "search_documents",
            "retrieve_chunk",
            "generate_answer",
            "cite_sources",
        }

    def test_create_server(self) -> None:
        server = create_server()
        assert server.name == "mcp-server-rag"

    def test_tools_have_unique_names(self) -> None:
        tools = create_tools()
        names = [t.name for t in tools]
        assert len(names) == len(set(names)), "Tool names must be unique"

    def test_tools_to_mcp_format(self) -> None:
        tools = create_tools()
        for tool in tools:
            mcp_tool = tool.to_mcp_tool()
            assert mcp_tool.name == tool.name
            assert mcp_tool.description == tool.description
            assert mcp_tool.inputSchema is not None
