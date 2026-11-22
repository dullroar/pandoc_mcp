"""Exercise Pandoc through the MCP stdio entry point."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult, TextContent


SERVER = Path(__file__).resolve().parents[1] / "server.py"


class StdioTest(unittest.TestCase):
    def tool_text(self, result: CallToolResult) -> str:
        self.assertFalse(result.isError, result.content)
        self.assertEqual(len(result.content), 1)
        content = result.content[0]
        self.assertIsInstance(content, TextContent)
        return content.text

    def test_list_tools_and_convert(self):
        anyio.run(self.check_stdio)

    async def check_stdio(self):
        with TemporaryDirectory(prefix="pandoc-mcp-stdio-") as directory:
            server = StdioServerParameters(
                command=sys.executable, args=[str(SERVER)], cwd=directory
            )
            with anyio.fail_after(30):
                async with stdio_client(server) as (reader, writer):
                    async with ClientSession(reader, writer) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        self.assertEqual(
                            {tool.name for tool in tools.tools},
                            {"list_pandoc_formats", "pandoc_convert"},
                        )

                        formats = self.tool_text(await session.call_tool("list_pandoc_formats"))
                        version, inputs, outputs = formats.split("\n\n")
                        self.assertRegex(version, r"^pandoc \d+")
                        self.assertTrue(inputs.startswith("Input formats:\n"), inputs)
                        self.assertTrue(outputs.startswith("Output formats:\n"), outputs)
                        self.assertIn("markdown", inputs.split("\n", 1)[1].split(", "))
                        self.assertIn("html5", outputs.split("\n", 1)[1].split(", "))

                        inline = await session.call_tool("pandoc_convert", {
                            "source": "# Example\n\n**Synthetic fixture**\n",
                            "source_format": "markdown",
                            "source_is_file": False,
                            "to": "html5",
                        })
                        self.assertEqual(
                            self.tool_text(inline).strip(),
                            '<h1 id="example">Example</h1>\n<p><strong>Synthetic fixture</strong></p>',
                        )

                        fixture = Path(directory) / "example.md"
                        fixture.write_text("A *local* fixture.\n", encoding="utf-8")
                        output = fixture.with_suffix(".html")
                        written = await session.call_tool("pandoc_convert", {
                            "source": str(fixture),
                            "to": "html5",
                            "output_file": str(output),
                        })
                        self.assertEqual(self.tool_text(written), f"Written to {output}")
                        self.assertEqual(
                            output.read_text(encoding="utf-8").strip(),
                            "<p>A <em>local</em> fixture.</p>",
                        )
