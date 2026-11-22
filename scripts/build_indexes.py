#!/usr/bin/env python3
"""Rebuild the generated AGENTS.md indexes and any marked README indexes.

Run me when: I added, renamed, deleted or changed the gist of a memory, a plan or a script, and before every pull request.

Rules:
- memory/*.md (not AGENTS.md): front matter key `gist: "Read me when: ..."`.
- plans/<plan>/plan.md: front matter key `gist: "Read me when: ..."`.
- scripts/*: a line `Run me when: ...` in the first 25 lines (any comment style).
- A README with legacy markers routes Markdown files beneath its folder.
- Only the text between the BEGIN and END markers changes. The text above is fixed.
- The old wording `Read when:` is accepted as a gist.

Usage: build_indexes.py [--check] [ROOT]   (--check changes nothing; exit 1 if stale)
"""
from __future__ import annotations

import re
import sys
from collections.abc import Iterator
from pathlib import Path

from ctx_common import BEGIN, END, SKIP_DIRS, repo_root, split_frontmatter

RUN_ME = re.compile(r"Run me when:\s*(.+?)\s*(?:\*/|#>|-->|\"\"\")?\s*$")
PLAN_SKIP = {"archive"}
README_BEGIN = "<!-- BEGIN GENERATED CONTEXT INDEX -->"
README_END = "<!-- END GENERATED CONTEXT INDEX -->"


def has_readme_index(path: Path) -> bool:
    return path.is_file() and README_BEGIN in path.read_text(encoding="utf-8")


def readme_files(folder: Path) -> Iterator[Path]:
    for child in folder.iterdir():
        if child.name in SKIP_DIRS:
            continue
        if child.is_dir():
            if has_readme_index(child / "README.md"):
                yield child / "README.md"
            else:
                yield from readme_files(child)
        elif child.suffix == ".md" and child.name != "README.md":
            yield child


def readme_entries(index: Path, errors: list[str]) -> str:
    text = index.read_text(encoding="utf-8")
    found = re.search(r"<!--\s*index-exclude:\s*(.*?)\s*-->", text)
    excluded = {name.strip() for name in found.group(1).split(",")} if found else set()
    items = []
    paths = {path.relative_to(index.parent).as_posix(): path for path in readme_files(index.parent)}
    for name, path in sorted(paths.items()):
        if name not in excluded and (gist := md_gist(path, errors)):
            items.append(f"* [{name}](./{name}).\n  {gist}")
    return "\n".join(items) if items else "<!-- No routed files yet. -->"


def md_gist(path: Path, errors: list[str]) -> str | None:
    meta, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    gist = meta.get("gist")
    if not isinstance(gist, str) or not gist.strip():
        errors.append(f"{path}: missing 'gist' front matter")
        return None
    return gist.strip()


def script_gist(path: Path, errors: list[str]) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").split("\n")[:25]
    except UnicodeDecodeError:
        errors.append(f"{path}: not a text file")
        return None
    for line in lines:
        found = RUN_ME.search(line)
        if found:
            return "Run me when: " + found.group(1)
    errors.append(f"{path}: missing 'Run me when:' line in the first 25 lines")
    return None


def entries(folder: Path, errors: list[str]) -> list[tuple[str, str]]:
    kind = folder.name
    out: list[tuple[str, str]] = []
    if kind == "memory":
        for p in sorted(folder.glob("*.md")):
            if p.name not in {"AGENTS.md", "README.md"} and (g := md_gist(p, errors)):
                out.append((p.name, g))
    elif kind == "plans":
        for d in sorted(x for x in folder.iterdir() if x.is_dir() and x.name not in PLAN_SKIP | SKIP_DIRS):
            if (d / "plan.md").is_file():
                if g := md_gist(d / "plan.md", errors):
                    out.append((f"{d.name}/plan.md", g))
            else:
                errors.append(f"{d}: plan folder has no plan.md")
    elif kind == "scripts":
        for p in sorted(folder.iterdir()):
            if p.is_file() and p.name not in {"AGENTS.md", "README.md"} and not p.name.startswith("."):
                if g := script_gist(p, errors):
                    out.append((p.name, g))
    return out


def render(items: list[tuple[str, str]]) -> str:
    if not items:
        return "<!-- Nothing to list yet. -->"
    return "\n".join(f"* [{name}](./{name})\n  {gist}" for name, gist in items)


def main(argv: list[str]) -> int:
    check = "--check" in argv
    args = [a for a in argv if not a.startswith("--")]
    root = repo_root(Path(args[0]) if args else None)
    errors: list[str] = []
    stale: list[str] = []

    def update(index: Path, begin: str, end: str, body: str) -> None:
        old = index.read_text(encoding="utf-8")
        head, marker, rest = old.partition(begin)
        _, closing, tail = rest.partition(end)
        if not marker or not closing:
            errors.append(f"{index}: missing or out-of-order BEGIN/END markers")
            return
        new = f"{head}{begin}\n\n{body}\n\n{end}{tail}"
        if new != old:
            stale.append(index.relative_to(root).as_posix())
            if not check:
                index.write_text(new, encoding="utf-8")

    for name in ("memory", "plans", "scripts"):
        folder = root / name
        index = folder / "AGENTS.md"
        if not index.is_file():
            errors.append(f"{index}: missing index")
            continue
        update(index, BEGIN, END, render(entries(folder, errors)))
    for index in sorted(root.rglob("README.md")):
        if not SKIP_DIRS.intersection(index.relative_to(root).parts) and has_readme_index(index):
            update(index, README_BEGIN, README_END, readme_entries(index, errors))
    for err in errors:
        print(f"ERROR {err}")
    if check and stale:
        print("STALE index (run: python3 scripts/build_indexes.py): " + ", ".join(stale))
    return 1 if errors or (check and stale) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
