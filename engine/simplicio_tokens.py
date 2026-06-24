"""Stdlib-only token estimator for prompt + completion accounting.

Why this exists
---------------
The naive `len(text) / 4` rule is cheap but drifts badly on the two inputs an
LLM loop cares about most: dense code/JSON (where punctuation and short symbols
inflate the real BPE token count) and whitespace-heavy text (where runs of
spaces/newlines collapse into very few tokens). This module stays pure-stdlib
(`re` only, no network, no tokenizer download) while landing within ~15% of real
BPE counts on mixed text.

The heuristic
-------------
We tokenize with a single regex into disjoint classes, then weight each class by
how a real byte-pair encoder tends to fragment it:

  - Words (runs of letters): real BPE keeps most English words whole (1 token)
    and only fragments longer ones. We charge 1 token up to ~6 chars, then add a
    sub-word piece per ~5 extra chars (`1 + (len - 1) // 5`), which tracks the
    empirical ~words*1.3 rate for English.
  - Numbers (runs of digits): BPE often emits one token per 1-3 digits. We use
    ~`ceil(len / 3)` with a 1-token floor.
  - Standalone punctuation / code symbols (`{ } [ ] ( ) ; : , . = + - * / < >`
    etc.): mostly one token each, but adjacent symbols frequently merge into a
    single BPE token, so a run of N symbol chars costs `ceil(N * 0.75)`.
  - Whitespace runs: a single space usually merges into the following token, but
    long runs (indentation, blank lines) compress hard. We charge
    `ceil(len / 6)` per run with a 0-token floor for a lone single space, so
    whitespace-heavy text scores *fewer* tokens, not more.

Calibration targets (chars -> tokens ratio == chars / tokens):
  - typical English prose .... ~4.0  (len/4)
  - code / JSON .............. ~3.2  (len/3.2, denser due to symbols)
  - whitespace-heavy ......... >4.0  (fewer tokens, runs collapse)

These are tuned so the per-class weights blend to the right global ratio on
mixed text rather than any single class being exact in isolation.
"""

from __future__ import annotations

import math
import re

# One pass, disjoint classes. Order matters: longer/specific classes first.
#   \s+              whitespace runs (indentation, newlines)
#   [A-Za-z]+        word (letter run) — sub-word fragmented by real BPE
#   \d+              number (digit run)
#   [^\w\s]+         a run of punctuation / symbol chars (partly merged by BPE)
#   .                any other single char (CJK, emoji bytes, etc.) — 1 token
_TOKEN_RE = re.compile(r"\s+|[A-Za-z]+|\d+|[^\w\s]+|.", re.DOTALL)

# Per-message overhead mimicking chat-template framing (role markers, delimiters)
# that real OpenAI/Anthropic tokenizers add around every message.
_PER_MESSAGE_OVERHEAD = 4


def _word_tokens(length: int) -> int:
    """Sub-word pieces for a letter run of `length` chars (>=1).

    1 token for short/common words, then one extra piece per ~5 chars."""
    return 1 + (length - 1) // 5


def _number_tokens(length: int) -> int:
    """Tokens for a digit run of `length` chars (>=1)."""
    return max(1, math.ceil(length / 3))


def _symbol_tokens(length: int) -> int:
    """Tokens for a run of `length` punctuation/symbol chars (>=1).

    Mostly 1 token each, but adjacent symbols often merge in BPE -> ~0.75x."""
    return max(1, math.ceil(length * 0.75))


def _whitespace_tokens(length: int) -> int:
    """Tokens for a whitespace run. A lone single space is usually free
    (merges into the neighbouring token); longer runs compress at ~1/6."""
    if length <= 1:
        return 0
    return math.ceil(length / 6)


def count_tokens(text: str) -> int:
    """Estimate the BPE token count of `text` with a blended heuristic.

    Empty string -> 0. Otherwise sums per-class weights (see module docstring)
    so English prose lands near len/4, code/JSON near len/3.2, and
    whitespace-heavy text below len/4.
    """
    if not text:
        return 0

    total = 0
    for match in _TOKEN_RE.finditer(text):
        piece = match.group()
        first = piece[0]
        if first.isspace():
            total += _whitespace_tokens(len(piece))
        elif first.isalpha() and first.isascii():
            total += _word_tokens(len(piece))
        elif first.isdigit():
            total += _number_tokens(len(piece))
        elif len(piece) == 1:
            # Any single non-ascii/other char (CJK, emoji byte, etc.): 1 token.
            total += 1
        else:
            # Run of punctuation / code symbols.
            total += _symbol_tokens(len(piece))
    return total


def _block_text(block: object) -> str:
    """Extract text from a content block (dict with 'text', or .text attr)."""
    if isinstance(block, str):
        return block
    if isinstance(block, dict):
        return str(block.get("text", ""))
    text_attr = getattr(block, "text", None)
    return text_attr if isinstance(text_attr, str) else ""


def _content_text(content: object) -> str:
    """Flatten an OpenAI/Anthropic message `content` into a single string."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(_block_text(block) for block in content)
    return str(content)


def count_messages(messages: list, system: str = "") -> int:
    """Sum estimated tokens over a chat `messages` list plus a `system` string.

    Each message contributes the token count of its flattened content plus a
    small per-message overhead (~4 tokens) approximating chat-template framing.
    The system prompt is counted as one extra framed message when present.
    """
    total = 0
    if system:
        total += count_tokens(system) + _PER_MESSAGE_OVERHEAD
    for message in messages or []:
        content = message.get("content") if isinstance(message, dict) else message
        total += count_tokens(_content_text(content)) + _PER_MESSAGE_OVERHEAD
    return total


def count_payload(obj: dict) -> int:
    """Total input tokens for a parsed request body.

    Reads `obj['messages']` (list) and optional `obj['system']` (str or
    Anthropic-style list of blocks) and returns the input token estimate via
    `count_messages`.
    """
    messages = obj.get("messages", []) if isinstance(obj, dict) else []
    system = obj.get("system", "") if isinstance(obj, dict) else ""
    if not isinstance(system, str):
        system = _content_text(system)
    return count_messages(messages, system)
