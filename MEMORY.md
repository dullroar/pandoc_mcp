# MEMORY.md

Non-obvious findings about this codebase and its operating environment, discovered during work but not designed for anywhere else — not in README.md (what it is and how to use it), DESIGN.md (architectural decisions), or agent-instruction files (rules). This is background context for whichever LLM works in this repository next, so it does not have to rediscover these findings the hard way.

If you (an LLM) make a finding like the ones below — a gotcha, an environment quirk, or a non-obvious reason one component reads or uses another — add it here rather than only mentioning it in chat. Keep entries factual and dated; note when something might have been fixed since.

## Findings

- 2026-05-18 — A FastMCP server with tools registered but no `if __name__ == "__main__": mcp.run()` guard exits immediately with no error: the stdio listener never starts and the MCP client just sees a failed/closed connection, not an exception pointing at the cause (commit 759163a). If an MCP client can't connect to a server in this family (see also the sibling `metadata_mcp` repo's MEMORY.md for other FastMCP quirks), check for a missing `mcp.run()` call before debugging the transport or client config.
