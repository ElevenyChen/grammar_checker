"""Markdown / plain text -> Document (second reader, scope 1.0).

- `#` lines are headings (level = number of #). If the first heading is the only level-1
  heading and level-2 headings follow, it is the document title.
- Blank-line separated blocks are paragraphs; lines inside a block are joined with a space.
- Fenced code blocks -> "code"; runs of lines starting with | -> "table"; lines starting with
  ![ -> "image". All skipped and recorded by ingest.blocks.
- Inline markup is stripped to plain text: **bold**, *italic*, _italic_, `code`, [text](url).
"""
from __future__ import annotations

import re
from pathlib import Path

from checker.ingest.blocks import RawBlock, build
from checker.model import Document

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
EMPH_RE = re.compile(r"(\*\*|__)(.+?)\1|(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)|(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?!\w)")
CODE_RE = re.compile(r"`([^`]*)`")


def read(path: Path) -> Document:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    blocks = _blocks(lines)
    _mark_title(blocks)
    doc = build(str(path), blocks)
    doc.meta["reader"] = "markdown"
    return doc


def strip_inline(text: str) -> str:
    text = LINK_RE.sub(r"\1", text)
    text = CODE_RE.sub(r"\1", text)
    prev = None
    while prev != text:
        prev = text
        text = EMPH_RE.sub(lambda m: next(g for g in m.groups()[1:] if g is not None), text)
    return text


def _blocks(lines: list[str]) -> list[RawBlock]:
    out: list[RawBlock] = []
    para: list[str] = []
    in_code = False
    in_table = False

    def flush() -> None:
        if para:
            out.append(RawBlock(kind="para", text=strip_inline(" ".join(s.strip() for s in para))))
            para.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            flush()
            if not in_code:
                out.append(RawBlock(kind="code"))
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("|"):
            flush()
            if not in_table:
                out.append(RawBlock(kind="table"))
                in_table = True
            continue
        in_table = False
        if not stripped:
            flush()
            continue
        m = HEADING_RE.match(stripped)
        if m:
            flush()
            out.append(RawBlock(kind="para", text=strip_inline(m.group(2)),
                                style=f"Heading {len(m.group(1))}", heading_level=len(m.group(1))))
            continue
        if stripped.startswith("!["):
            flush()
            out.append(RawBlock(kind="image"))
            continue
        para.append(line)
    flush()
    return out


def _mark_title(blocks: list[RawBlock]) -> None:
    headings = [b for b in blocks if b.heading_level is not None]
    if not headings or headings[0].heading_level != 1:
        return
    level1 = [b for b in headings if b.heading_level == 1]
    if len(level1) == 1 and any(b.heading_level == 2 for b in headings[1:]):
        first = headings[0]
        first.is_title = True
        first.heading_level = None
        first.style = "Title"
