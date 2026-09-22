# DESIGN.md

# pandoc-mcp Design

## Boundary

pandoc-mcp provides an MCP-facing conversion boundary around Pandoc. README.md documents setup and calls; this document records why conversion stays in Pandoc rather than in an LLM or Python formatter.

## Core decisions

- Delegate mechanical document conversion to Pandoc through pypandoc. The agent retains responsibility for selecting formats, flags, and post-conversion review.
- Expose raw Pandoc arguments intentionally, preserving access to mature native features without reproducing them as many narrow MCP parameters.
- Support file and text sources, with an explicit source-format requirement for raw text.
- Expand file globs inside the server and derive output extensions from requested target formats so bulk conversion remains a single logical operation.

## Constraints

The server does not promise semantic equivalence across document formats. Conversion output must still be reviewed by the caller, especially when a format has capabilities that its target cannot represent.


