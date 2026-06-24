"""Deterministic, fail-open, meaning-preserving text compression.

Stdlib only (re, json). Each algorithm shrinks text only when it is safe to do
so — it must NEVER corrupt the meaning of code or prose. Algorithms operate at
the whitespace / blank-line / dedup / JSON-minify level only; intra-line spacing
inside lines is never touched (it can be load-bearing in code).

Public API:
    compress(text) -> str
    compress_report(text) -> dict
    ALGOS -> list[(name, fn)]

Invariants:
    - compress(text) returns `text` unchanged when nothing shrinks.
    - compress is idempotent: compress(compress(x)) == compress(x).
    - each algo is applied only if it strictly shrinks the text.
"""

from __future__ import annotations

import json
import re

__all__ = ["compress", "compress_report", "ALGOS"]


# 1. strip_ansi — remove ANSI terminal escape sequences (CSI/SGR, OSC, etc.).
_ANSI_RE = re.compile(
    r"""
    \x1b
    (?:
        \[[0-?]*[ -/]*[@-~]      # CSI ... final byte
      | \][^\x07\x1b]*(?:\x07|\x1b\\)  # OSC ... BEL or ST
      | [@-Z\\-_]               # 2-char escapes
    )
    """,
    re.VERBOSE,
)


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


# 2. trailing_ws — strip trailing whitespace per line (preserve EOL style).
_TRAILING_RE = re.compile(r"[ \t]+(?=\r?\n)|[ \t]+\Z")


def trailing_ws(text: str) -> str:
    return _TRAILING_RE.sub("", text)


# 3. collapse_blanks — 3+ consecutive blank lines -> 2.
# A "blank" line is empty or whitespace-only. Works for \n and \r\n.
# A run of N newlines spans N-1 blank lines between two content lines; mapping
# runs of 4+ newlines down to 3 yields "3+ blank lines -> 2 blank lines".
_BLANKS_RE = re.compile(r"(?:[ \t]*\r?\n){4,}")


def collapse_blanks(text: str) -> str:
    def _repl(m: "re.Match[str]") -> str:
        eol = "\r\n" if "\r\n" in m.group(0) else "\n"
        return eol * 3
    return _BLANKS_RE.sub(_repl, text)


# 4. dedup_lines — collapse runs of identical consecutive non-empty lines to one
#    + a "… (N repeated lines collapsed)" marker.
_MARKER_RE = re.compile(r"… \(\d+ repeated lines collapsed\)\Z")


def dedup_lines(text: str) -> str:
    # Preserve EOL of each line by splitting with keepends.
    lines = text.splitlines(keepends=True)
    if not lines:
        return text
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        cur = lines[i]
        content = cur.rstrip("\r\n")
        if content == "" or _MARKER_RE.search(content):
            out.append(cur)
            i += 1
            continue
        # count run of identical lines (compare full incl. EOL so we don't merge
        # a final no-EOL line with an EOL line).
        j = i + 1
        while j < n and lines[j] == cur:
            j += 1
        run = j - i
        out.append(cur)
        if run > 1:
            eol = cur[len(content):] or "\n"
            collapsed = run - 1
            marker = "… (%d repeated lines collapsed)%s" % (collapsed, eol)
            out.append(marker)
        i = j
    return "".join(out)


# 5. minify_json — if the WHOLE text is a standalone JSON object/array, minify.
def minify_json(text: str) -> str:
    stripped = text.strip()
    if not stripped or stripped[0] not in "{[":
        return text
    try:
        obj = json.loads(stripped)
    except (ValueError, TypeError):
        return text
    if not isinstance(obj, (dict, list)):
        return text
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


# 6. rule_runs — collapse runs of 10+ identical rule chars to 8.
_RULE_CHARS = "=-_*#.~"
_RULE_RE = re.compile(
    r"(?P<c>[" + re.escape(_RULE_CHARS) + r"])(?P=c){9,}"
)


def rule_runs(text: str) -> str:
    def _repl(m: "re.Match[str]") -> str:
        return m.group("c") * 8
    return _RULE_RE.sub(_repl, text)


# 7. hex_dump_fold — collapse 32+ consecutive hex pairs to a marker.
#    A "hex dump" = >=32 groups of two hex digits, separated by single spaces,
#    e.g. "de ad be ef ...". Folded to "[N bytes hex elided]".
_HEX_RE = re.compile(r"(?:[0-9A-Fa-f]{2})(?: [0-9A-Fa-f]{2}){31,}")


def hex_dump_fold(text: str) -> str:
    def _repl(m: "re.Match[str]") -> str:
        run = m.group(0)
        nbytes = (len(run) + 1) // 3  # "XX " repeated
        return "[%d bytes hex elided]" % nbytes
    return _HEX_RE.sub(_repl, text)


# 8. fenced_log_fold — within ``` fences or indented blocks, collapse 5+ lines
#    sharing an identical leading timestamp/prefix into one + a marker.
#    A "prefix" here = a leading run matching a timestamp-ish or bracketed tag.
_PREFIX_RE = re.compile(
    r"^(?P<p>"
    r"(?:\[[^\]]+\]\s*)"                        # [tag] / [2024-...]
    r"|(?:\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}\S*\s*)"  # ISO ts
    r"|(?:\d{2}:\d{2}:\d{2}(?:[.,]\d+)?\s*)"    # HH:MM:SS
    r")"
)


def _line_prefix(line: str) -> str | None:
    body = line
    # respect indentation: a leading-indent log block keeps its indent.
    m = _PREFIX_RE.match(body.lstrip(" \t"))
    if not m:
        return None
    indent = body[: len(body) - len(body.lstrip(" \t"))]
    return indent + m.group("p")


def fenced_log_fold(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines:
        return text
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        content = line.rstrip("\r\n")
        prefix = _line_prefix(content)
        if prefix is None:
            out.append(line)
            i += 1
            continue
        j = i + 1
        while j < n:
            nxt = lines[j].rstrip("\r\n")
            if _line_prefix(nxt) == prefix:
                j += 1
            else:
                break
        run = j - i
        if run >= 5:
            out.append(lines[i])  # keep first line verbatim
            eol = line[len(content):] or "\n"
            hidden = run - 1
            out.append(
                "%s… (%d more lines with prefix %r)%s"
                % (prefix, hidden, prefix.strip(), eol)
            )
            i = j
        else:
            out.append(line)
            i += 1
    return "".join(out)


ALGOS = [
    ("strip_ansi", strip_ansi),
    ("trailing_ws", trailing_ws),
    ("rule_runs", rule_runs),
    ("hex_dump_fold", hex_dump_fold),
    ("fenced_log_fold", fenced_log_fold),
    ("dedup_lines", dedup_lines),
    ("collapse_blanks", collapse_blanks),
    ("minify_json", minify_json),
]


def _run_pipeline(text: str) -> "tuple[str, list[str]]":
    applied: list[str] = []
    cur = text
    for name, fn in ALGOS:
        try:
            out = fn(cur)
        except Exception:
            # fail-open: a misbehaving algo never breaks the pipeline.
            continue
        if isinstance(out, str) and len(out) < len(cur):
            cur = out
            applied.append(name)
    return cur, applied


def compress(text: str) -> str:
    """Compress `text`, returning it unchanged if nothing shrinks.

    Idempotent: re-running over the output yields the same output, because each
    pass only re-applies algos that still strictly shrink the (already shrunk)
    text — and the algos are fixpoints on their own output.
    """
    if not isinstance(text, str) or not text:
        return text
    out, _ = _run_pipeline(text)
    return out if len(out) < len(text) else text


def compress_report(text: str) -> dict:
    """Return {before, after, saved, pct, applied:[names]}."""
    if not isinstance(text, str):
        text = str(text)
    before = len(text)
    out, applied = _run_pipeline(text)
    if len(out) >= before:
        out, applied = text, []
    after = len(out)
    saved = before - after
    pct = round((saved / before) * 100, 2) if before else 0.0
    return {
        "before": before,
        "after": after,
        "saved": saved,
        "pct": pct,
        "applied": applied,
    }
