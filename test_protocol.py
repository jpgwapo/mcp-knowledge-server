"""Exercise the real stdio transport and registered tools with public fixtures."""

import asyncio
from pathlib import Path
import sys
import tempfile
import unittest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class StdioIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_registered_tools_work_through_stdio(self):
        async def exercise():
            # Launch from a different directory to check path independence.
            with tempfile.TemporaryDirectory() as cwd:
                parameters = StdioServerParameters(
                    command=sys.executable,
                    args=[str(Path(__file__).with_name("server.py").resolve())],
                    cwd=cwd,
                )
                async with stdio_client(parameters) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        self.assertEqual(
                            {tool.name for tool in tools.tools},
                            {"list_documents", "search_knowledge", "get_document"},
                        )
                        listed = await session.call_tool("list_documents", {})
                        self.assertFalse(listed.isError)
                        self.assertEqual(listed.content[0].text, "equipment.md\nirrigation.md")
                        read_result = await session.call_tool("get_document", {"filename": "equipment.md"})
                        self.assertFalse(read_result.isError)
                        expected = Path(__file__).with_name("knowledge").joinpath("equipment.md").read_text(encoding="utf-8")
                        self.assertEqual(read_result.content[0].text, expected)
                        searched = await session.call_tool("search_knowledge", {"query": "irrigation"})
                        self.assertFalse(searched.isError)
                        self.assertIn("--- irrigation.md ---", searched.content[0].text)
                        rejected = await session.call_tool("get_document", {"filename": "../README.md"})
                        self.assertEqual(rejected.content[0].text, "Document not found or filename not allowed.")

        await asyncio.wait_for(exercise(), timeout=30)


if __name__ == "__main__":
    unittest.main()
