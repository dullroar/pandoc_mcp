---
gist: "Read when: changing conversion arguments, source handling, glob/bulk behavior, or tempted to convert with an LLM or Python formatter."
---

# Delegate conversion to Pandoc

**Decision.** Mechanical document conversion goes to Pandoc through pypandoc, not to an LLM or a Python formatter. The agent keeps responsibility for selecting formats, flags, and post-conversion review. Raw Pandoc arguments are exposed intentionally rather than as many narrow MCP parameters. File and text sources are supported, with an explicit source format required for raw text. File globs expand inside the server and output extensions derive from the target format, so bulk conversion is one logical operation.

**Boundary.** No promise of semantic equivalence across formats; callers must review output, especially where the target cannot represent source features.
