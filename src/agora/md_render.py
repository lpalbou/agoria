"""Terminal markdown rendering for the HUMAN chat surface (mdpad-inspired).

Agents post markdown; `less`-style raw wrapping turns their tables into pipe
soup and drowns headings in `#`s (operator finding, 2026-07-14: a delegate's
status table arrived unreadable). This renders the common structures:

- pipe tables: columns aligned, widths adapted to the terminal (generous
  columns yield first, mdpad's idea simplified), numeric columns
  right-aligned, header bold;
- headings styled, list items wrapped with hanging indents, blockquotes and
  fenced code kept verbatim (code is never re-wrapped, only truncated);
- inline **bold** and `code` markers applied after width math, so styling
  can never overflow a line.

Deliberately CHAT-ONLY: the agent-facing read path (render.py) stays
verbatim inside nonce fences — models must see exactly what was written.
Pure stdlib; a Style of None (or disabled) degrades to clean plain text.
"""

from __future__ import annotations

import re
import textwrap
from typing import Any

_NUMERIC = re.compile(r"^[~≈<>+-]?[\d,.]+\s*(%|ms|s|m|h|d|kb|mb|gb|tb|k|x|×)?$", re.I)
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`]+)`")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_LIST = re.compile(r"^(\s*)([-*+]|\d{1,3}[.)])\s+(.*)$")
_TABLE_SEP = re.compile(r"^\s*\|?[\s:|-]+\|[\s:|-]*$")
_MIN_COL = 6          # a column never shrinks below this many visible chars


def _inline(text: str, s: Any) -> str:
    """Apply inline markers AFTER wrapping (removing markers only shortens)."""
    if s is None or not getattr(s, "enabled", False):
        return _CODE.sub(r"\1", _BOLD.sub(r"\1", text))
    text = _BOLD.sub(lambda m: s.bold(m.group(1)), text)
    return _CODE.sub(lambda m: s.cyan(m.group(1)), text)


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _fit_columns(natural: list[int], budget: int) -> list[int]:
    """mdpad's staged layout, simplified: columns that fit keep their natural
    width; the space-hungry ones share what remains proportionally."""
    if sum(natural) <= budget:
        return natural
    widths = list(natural)
    while sum(widths) > budget:
        over = [i for i, w in enumerate(widths) if w > _MIN_COL]
        if not over:
            break  # nothing left to shrink; the terminal is just too narrow
        excess = sum(widths) - budget
        hungry = sorted(over, key=lambda i: widths[i], reverse=True)
        took = False
        for i in hungry:
            cut = min(widths[i] - _MIN_COL, max(1, excess // len(hungry)))
            if cut > 0:
                widths[i] -= cut
                excess -= cut
                took = True
            if excess <= 0:
                break
        if not took:
            break
    return widths


def _render_table(block: list[str], width: int, s: Any) -> list[str]:
    header = _cells(block[0])
    ncols = len(header)
    rows = [(_cells(r) + [""] * ncols)[:ncols] for r in block[2:]]
    # Numeric columns read better right-aligned (mdpad behavior).
    right = [bool(rows) and all(_NUMERIC.match(r[i]) for r in rows if r[i])
             for i in range(ncols)]
    natural = [max(len(header[i]), *(len(r[i]) for r in rows)) if rows
               else len(header[i]) for i in range(ncols)]
    budget = width - (3 * ncols + 1)
    if budget < ncols * _MIN_COL:
        return [ln for ln in block]  # hopelessly narrow: raw beats wrong
    widths = _fit_columns(natural, budget)

    def emit(cells: list[str], *, bold: bool = False) -> list[str]:
        wrapped = [textwrap.wrap(c, widths[i], break_long_words=True) or [""]
                   for i, c in enumerate(cells)]
        height = max(len(w) for w in wrapped)
        out = []
        for line_i in range(height):
            parts = []
            for i in range(ncols):
                piece = wrapped[i][line_i] if line_i < len(wrapped[i]) else ""
                pad = widths[i] - len(piece)
                piece = (" " * pad + piece) if right[i] else (piece + " " * pad)
                piece = _inline(piece, s)
                if bold and s is not None and getattr(s, "enabled", False):
                    piece = s.bold(piece)
                parts.append(piece)
            out.append("| " + " | ".join(parts) + " |")
        return out

    rule = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    lines = emit(header, bold=True)
    lines.append(rule if s is None else s.dim(rule))
    for r in rows:
        lines.extend(emit(r))
    return lines


def render_markdown(text: str, width: int, s: Any = None) -> list[str]:
    """Render markdown to terminal lines of at most `width` visible chars.
    Structure-preserving and conservative: anything unrecognized wraps as a
    plain paragraph, so malformed input degrades to today's behavior."""
    lines: list[str] = []
    src = text.splitlines()
    i = 0
    in_code = False
    while i < len(src):
        line = src[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            lines.append((s.dim(stripped) if s else stripped))
            i += 1
            continue
        if in_code:
            # Verbatim: code is never re-wrapped, only truncated with a mark.
            shown = line if len(line) <= width else line[:width - 1] + "…"
            lines.append(s.dim(shown) if s else shown)
            i += 1
            continue
        # Pipe table: a |-row whose NEXT line is the separator row.
        if (stripped.startswith("|") and i + 1 < len(src)
                and _TABLE_SEP.match(src[i + 1].strip())
                and "|" in src[i + 1]):
            block = [stripped, src[i + 1].strip()]
            i += 2
            while i < len(src) and src[i].strip().startswith("|"):
                block.append(src[i].strip())
                i += 1
            lines.extend(_render_table(block, width, s))
            continue
        m = _HEADING.match(stripped)
        if m:
            head = _inline(m.group(2).strip(), s)
            lines.append(s.bold(head) if s else head)
            i += 1
            continue
        m = _LIST.match(line)
        if m:
            indent, marker, rest = m.groups()
            prefix = f"{indent}{marker} "
            cont = " " * len(prefix)
            wrapped = textwrap.wrap(rest, max(20, width - len(prefix)),
                                    break_long_words=False,
                                    break_on_hyphens=False) or [""]
            lines.append(prefix + _inline(wrapped[0], s))
            lines.extend(cont + _inline(w, s) for w in wrapped[1:])
            i += 1
            continue
        if stripped.startswith(">"):
            quoted = stripped.lstrip("> ").strip()
            for w in textwrap.wrap(quoted, max(20, width - 2),
                                   break_long_words=False) or [""]:
                lines.append(s.dim("▏ " + w) if s else "> " + w)
            i += 1
            continue
        # Plain paragraph line (blank lines preserved as separators).
        if not stripped:
            lines.append("")
        else:
            lines.extend(_inline(w, s) for w in
                         textwrap.wrap(line, max(20, width),
                                       break_long_words=False,
                                       break_on_hyphens=False))
        i += 1
    while lines and not lines[-1]:
        lines.pop()
    return lines
