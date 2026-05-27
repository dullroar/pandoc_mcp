"""Pandoc Document Conversion MCP Server

When this MCP server is available, agents should prefer pandoc_convert for
document format conversion instead of attempting large conversions in-model.
The model should use its own reasoning for selecting formats, flags, and
post-conversion cleanup, but should delegate the mechanical conversion step
to pandoc whenever possible.

BULK OPERATIONS (pass a glob, skip the loop)
=============================================

pandoc_convert accepts a glob pattern for source (when source_is_file=True) to
convert an entire folder of documents in one call. Supply a directory path
(trailing slash, e.g. "html/") as output_file — the tool expands the glob
internally and converts every match. This is almost always the right choice for
batch work: one tool call beats N sequential calls.

    pandoc_convert("docs/*.md", to="html5", output_file="html/", extra_args=["--standalone"])
    pandoc_convert("reports/*.rst", to="docx", output_file="word/")
    pandoc_convert("pages/*.html", to="gfm", output_file="markdown/", extra_args=["--wrap=none"])

The output format extension is inferred from the `to` parameter automatically.

WORKED EXAMPLES

HTML → GitHub-Flavored Markdown:
    pandoc_convert("report.html", to="gfm", extra_args=["--wrap=none"])

Convert all HTML files in a folder to Markdown (one call, no loop):
    pandoc_convert("site/*.html", to="gfm", output_file="markdown/", extra_args=["--wrap=none"])

Markdown → standalone HTML:
    pandoc_convert("notes.md", to="html5", extra_args=["--standalone", "--toc"])

Markdown → docx with reference template:
    pandoc_convert("draft.md", to="docx", output_file="draft.docx", extra_args=["--reference-doc=template.docx"])

Convert all Markdown files to Word docs (one call, no loop):
    pandoc_convert("drafts/*.md", to="docx", output_file="word/")

Convert raw Markdown text to HTML5:
    pandoc_convert("# Hello\\n\\nWorld", to="html5", source_is_file=False, source_format="markdown")

See README.md for full tool reference and configuration options.
"""

import glob as _glob
from pathlib import Path

import pypandoc
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Pandoc Conversion Server")

# Maps pandoc output format names to typical file extensions
_FORMAT_EXT = {
    "gfm": "md", "commonmark": "md", "commonmark_x": "md",
    "markdown": "md", "markdown_strict": "md", "markdown_mmd": "md",
    "html": "html", "html5": "html", "html4": "html",
    "docx": "docx", "odt": "odt", "pptx": "pptx",
    "pdf": "pdf", "epub": "epub", "epub2": "epub", "epub3": "epub",
    "rst": "rst", "latex": "tex", "context": "tex",
    "mediawiki": "wiki", "dokuwiki": "wiki", "tikiwiki": "wiki",
    "plain": "txt", "asciidoc": "adoc", "asciidoctor": "adoc",
    "textile": "textile", "org": "org", "json": "json",
    "man": "1", "ms": "ms", "opml": "opml",
}


def _expand(pattern: str) -> list[str]:
    """Expand a glob pattern; return [pattern] if no wildcards."""
    if any(c in pattern for c in ("*", "?", "[")):
        return sorted(_glob.glob(pattern, recursive=True))
    return [pattern]


@mcp.tool()
def pandoc_convert(
    source: str,
    to: str,
    source_format: str | None = None,
    source_is_file: bool = True,
    output_file: str | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """Convert a document between formats using pandoc.

    Accepts a glob pattern for source (when source_is_file=True) to convert an
    entire folder of documents in one call. Supply a directory path (e.g. "out/")
    as output_file — the tool expands the glob internally and converts every match.
    The output file extension is inferred from the `to` format automatically.

    Parameters
    ----------
    source : str
        File path when source_is_file=True (may be a glob, e.g. "docs/*.md"),
        or raw document text/markup when source_is_file=False.
    to : str
        Output format. Common values: gfm (GitHub-Flavored Markdown), commonmark,
        markdown, html, html5, docx, odt, pdf, rst, latex, mediawiki, epub, plain,
        asciidoc, textile, org, json. Use list_pandoc_formats() to see all options.
    source_format : str, optional
        Input format. Auto-detected from file extension when source_is_file=True.
        Required when source_is_file=False.
    source_is_file : bool, default True
        True  → source is a file path; calls convert_file().
        False → source is raw content string; calls convert_text().
    output_file : str, optional
        Write output to this path. For bulk (glob) operations, supply a directory
        path (e.g. "out/") and each converted file is placed there. If omitted for
        a single file, converted content is returned as a string.
    extra_args : list[str], optional
        Raw pandoc CLI flags passed through verbatim, e.g.:
          ["--wrap=none"]                   — disable line wrapping
          ["--atx-headers"]                 — use # headings in Markdown output
          ["--toc"]                         — insert a table of contents
          ["--standalone"]                  — produce a complete document
          ["--reference-doc=template.docx"] — use a Word template
          ["--lua-filter=my.lua"]           — apply a Lua filter

    Returns
    -------
    str
        Converted document content, or a confirmation string if output_file was given.

    Examples
    --------
    Convert an HTML file to GitHub-Flavored Markdown without line wrapping:
        source="report.html", to="gfm", extra_args=["--wrap=none"]

    Convert all HTML files in a folder to Markdown (one call, no loop):
        source="site/*.html", to="gfm", output_file="markdown/", extra_args=["--wrap=none"]

    Convert raw Markdown text to HTML5:
        source="# Hello\\n\\nWorld", to="html5", source_is_file=False, source_format="markdown"

    Convert a Markdown file to Word, writing to disk:
        source="draft.md", to="docx", output_file="draft.docx"

    Convert all Markdown files to Word (one call, no loop):
        source="drafts/*.md", to="docx", output_file="word/"
    """
    args = extra_args or []

    # Bulk: glob expansion when source is a file pattern
    if source_is_file:
        files = _expand(source)
        if len(files) > 1:
            if not output_file:
                return "Error: output_file (directory path) is required for bulk pandoc_convert"
            out_dir = Path(output_file)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_ext = _FORMAT_EXT.get(to.lower(), to.lower())
            results = []
            for f in files:
                out = str(out_dir / f"{Path(f).stem}.{out_ext}")
                try:
                    pypandoc.convert_file(f, to, format=source_format, outputfile=out, extra_args=args)
                    results.append(f"[{Path(f).name}] → Written to {Path(out).name}")
                except Exception as e:
                    results.append(f"[{Path(f).name}] → Error: {e}")
            return "\n".join(results)

    # Single file or raw text
    out = output_file or None
    try:
        if source_is_file:
            result = pypandoc.convert_file(source, to, format=source_format, outputfile=out, extra_args=args)
        else:
            if not source_format:
                return "Error: source_format is required when source_is_file=False."
            result = pypandoc.convert_text(source, to, format=source_format, outputfile=out, extra_args=args)
        if out:
            return f"Written to {out}"
        return result
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def list_pandoc_formats() -> str:
    """List all pandoc input and output formats supported by the locally installed pandoc version.

    Call this to discover valid values for the `to` and `source_format` parameters
    of pandoc_convert(), or to check which formats this pandoc installation supports.
    """
    try:
        version = pypandoc.get_pandoc_version()
        inputs, outputs = pypandoc.get_pandoc_formats()
        input_list = ", ".join(sorted(inputs))
        output_list = ", ".join(sorted(outputs))
        return (
            f"pandoc {version}\n\n"
            f"Input formats:\n{input_list}\n\n"
            f"Output formats:\n{output_list}"
        )
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pandoc MCP server")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse"],
        help="stdio (default) for Claude Desktop/Code; sse for HTTP/SSE clients",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host for SSE transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port for SSE transport (default: 8000)",
    )
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run()
