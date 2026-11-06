---
gist: "Read when: an MCP client cannot connect to a FastMCP server in this repository family, or the server exits immediately with no error."
---

# FastMCP server exits silently without `mcp.run()`

- 2026-05-18 - A FastMCP server with tools registered but no `if __name__ == "__main__": mcp.run()` guard exits immediately with no error: the stdio listener never starts and the client only sees a failed/closed connection, with no exception pointing at the cause (commit 759163a). If a client cannot connect to a server in this family (see also the sibling `metadata_mcp` repository's `memory/fastmcp-registration-checks.md`), check for a missing `mcp.run()` call before debugging the transport or client config.
