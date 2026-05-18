import pypandoc
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Pandoc Conversion Server")


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

    Parameters
    ----------
    source : str
        File path when source_is_file=True (e.g. "report.html"), or raw document
        text/markup when source_is_file=False.
    to : str
        Output format. Common values: gfm (GitHub-Flavored Markdown), commonmark,
        markdown, html, html5, docx, odt, pdf, rst, latex, mediawiki, epub, plain,
        asciidoc, textile, org, json. Use list_pandoc_formats() to see all options.
    source_format : str, optional
        Input format. Auto-detected from file extension when source_is_file=True.
        Required when source_is_file=False. Same value space as `to`.
    source_is_file : bool, default True
        True  → source is a file path; calls convert_file().
        False → source is raw content string; calls convert_text().
    output_file : str, optional
        If given, pandoc writes output to this path and this tool returns a
        confirmation message. If omitted, converted content is returned as a string.
    extra_args : list[str], optional
        Raw pandoc CLI flags passed through verbatim, e.g.:
          ["--wrap=none"]                   — disable line wrapping
          ["--atx-headers"]                 — use # headings in Markdown output
          ["--toc"]                         — insert a table of contents
          ["--columns=80"]                  — set line width
          ["--standalone"]                  — produce a complete document
          ["--reference-doc=template.docx"] — use a Word template
          ["--lua-filter=my.lua"]           — apply a Lua filter
          ["--strip-comments"]              — remove HTML comments
        Any pandoc flag accepted by the CLI can be passed here.

    Returns
    -------
    str
        Converted document content, or a confirmation string if output_file was given.

    Examples
    --------
    Convert an HTML file to GitHub-Flavored Markdown without line wrapping:
        source="report.html", to="gfm", extra_args=["--wrap=none"]

    Convert raw Markdown text to HTML5:
        source="# Hello\\n\\nWorld", to="html5", source_is_file=False, source_format="markdown"

    Convert a Markdown file to Word, writing to disk:
        source="draft.md", to="docx", output_file="draft.docx"

    Convert with a table of contents and standalone HTML:
        source="notes.md", to="html5", extra_args=["--toc", "--standalone"]
    """
    args = extra_args or []
    out = output_file or None
    try:
        if source_is_file:
            result = pypandoc.convert_file(
                source,
                to,
                format=source_format,
                outputfile=out,
                extra_args=args,
            )
        else:
            if not source_format:
                return "Error: source_format is required when source_is_file=False."
            result = pypandoc.convert_text(
                source,
                to,
                format=source_format,
                outputfile=out,
                extra_args=args,
            )
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
