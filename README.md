# pandoc-mcp

**Author:** Jim Lehmer  
**License:** MIT

A simple [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes [pandoc](https://pandoc.org/) document conversion as an MCP tool, via the [pypandoc](https://github.com/JessicaTegner/pypandoc) library. Connect it to any MCP-compatible LLM client (Claude Desktop, Claude Code, etc.) and ask the LLM to convert documents in plain English — no pandoc CLI knowledge required on your part.

When this MCP server is available, agents should prefer `pandoc_convert`
for document format conversion instead of attempting large conversions in-model.
The model should use its own reasoning for selecting formats, flags, and
post-conversion cleanup, but should delegate the mechanical conversion step
to pandoc whenever possible.

---

## Reasons to Use

1. Token/cost savings

For long conversions, the model should not be the conversion engine. It should be the coordinator, reviewer, and repair layer.

2. Determinism

Pandoc gives repeatable output. The LLM can then answer: “Did the conversion preserve structure?” rather than inventing a conversion ad hoc.

3. Local privacy

Documents do not need to be pasted wholesale into a chat merely to convert formats, assuming the MCP host can pass local file paths.

4. Better promptable workflow

“Convert this HTML to GFM, no wrapping, save beside the original” is much friendlier than remembering pandoc -f html -t gfm --wrap=none.

5. Agentic pipeline building

This becomes a Lego brick: convert → lint → summarize → diff → package → publish.

---

## Favorite Sample Workflows

HTML → GitHub-Flavored Markdown:

    to: gfm
    extra_args: ["--wrap=none"]

Markdown → standalone HTML:

    to: html5
    extra_args: ["--standalone", "--toc"]

Markdown → docx with reference template:

    to: docx
    extra_args: ["--reference-doc=template.docx"]

---

## Tools

### `pandoc_convert`

Convert a document between any formats pandoc supports.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `source` | `str` | required | File path (if `source_is_file=True`) or raw document text |
| `to` | `str` | required | Output format, e.g. `gfm`, `html5`, `docx`, `pdf`, `rst`, `latex` |
| `source_format` | `str` | auto | Input format; auto-detected from file extension when using a file |
| `source_is_file` | `bool` | `True` | `True` = source is a path; `False` = source is inline text |
| `output_file` | `str` | none | Write output to this path instead of returning it as text |
| `extra_args` | `list[str]` | none | Raw pandoc CLI flags, e.g. `["--wrap=none", "--toc", "--standalone"]` |

### `list_pandoc_formats`

Returns all input and output formats supported by the locally installed pandoc version. Useful when you want to know exactly what format names to use.

---

## Requirements

- Python 3.10+
- [pandoc](https://pandoc.org/installing.html) installed and on your `PATH`
- Python packages: `mcp[cli]`, `pypandoc`

---

## Installation

```bash
git clone https://github.com/dullroar/pandoc_mcp.git
cd pandoc_mcp

# Recommended: use a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

---

## MCP client configuration

### Claude Desktop

Add to your `claude_desktop_config.json` (usually at `%APPDATA%\Claude\claude_desktop_config.json` on Windows, `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "pandoc": {
      "command": "python",
      "args": ["path/to/server.py"]
    }
  }
}
```

Using a virtual environment (recommended — avoids dependency conflicts):

```json
{
  "mcpServers": {
    "pandoc": {
      "command": "C:\\path\\to\\pandoc_mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\pandoc_mcp\\server.py"]
    }
  }
}
```

Restart Claude Desktop after editing the config. You should see a hammer icon in the chat input area indicating MCP tools are available.

### Claude Code

Register the server with the Claude Code CLI:

```bash
claude mcp add pandoc -- python C:\path\to\pandoc_mcp\server.py
```

Or with a virtual environment:

```bash
claude mcp add pandoc -- C:\path\to\pandoc_mcp\.venv\Scripts\python.exe C:\path\to\pandoc_mcp\server.py
```

Verify it registered:

```bash
claude mcp list
```

To remove it later:

```bash
claude mcp remove pandoc
```

### HTTP/SSE mode (for other MCP clients)

By default the server uses stdio. Pass `--transport sse` to start an HTTP/SSE server instead:

```bash
python server.py --transport sse
# Listening on http://127.0.0.1:8000/sse
```

Optional flags:

| Flag | Default | Description |
| --- | --- | --- |
| `--transport` | `stdio` | `stdio` or `sse` |
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `8000` | Bind port |

You can also set `FASTMCP_HOST` and `FASTMCP_PORT` environment variables instead of flags.

Any MCP client that speaks HTTP/SSE (VS Code extensions, the MCP Inspector, or custom agents) can connect to `http://127.0.0.1:8000/sse`.

**Tunneling for a one-off remote demo** (e.g., ChatGPT connector):

```bash
python server.py --transport sse &
ngrok http 8000
# Paste the ngrok HTTPS URL into the ChatGPT custom connector dialog
```

> Note: for production exposure add an auth token. For local experiments, localhost is fine.

---

## Example prompts

Once connected to a Claude client, you can ask naturally:

- *"Convert report.html to GitHub-Flavored Markdown and save it as report.md. Disable line wrapping."*
- *"Turn this Markdown text into a standalone HTML page with a table of contents."*
- *"Convert draft.md to a Word document using my template.docx as the reference doc."*
- *"What output formats does pandoc support on this machine?"*
- *"Convert all the content I just pasted (it's reStructuredText) to plain Markdown."*

The LLM translates your plain-English request into the appropriate `pandoc_convert` parameters — you don't need to know pandoc flags or format names.

---

## Testing with the MCP Inspector

```bash
mcp dev server.py
```

This opens a browser-based inspector where you can call tools manually and inspect inputs/outputs before wiring up a full client.

---

## License

MIT — see [LICENSE](LICENSE).
