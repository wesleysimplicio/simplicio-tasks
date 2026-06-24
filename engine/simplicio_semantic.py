#!/usr/bin/env python3
"""simplicio_semantic — REVERSIBLE extractive "semantic-lite" compression.

This is the honest, deterministic alternative to a trained ONNX/embedding
semantic model. It does NOT learn anything, does NOT call a model, and does NOT
approximate sentence vectors. It scores each line/sentence by a transparent
heuristic (TF-IDF-ish term importance blended with position and length), keeps
the most salient fraction, and stashes the elided remainder so the original is
fully recoverable.

What this is:
    - Deterministic *extractive* compression: keep the top-scoring lines/sentences,
      replace dropped runs with a `‹simplicio:elided N lines #ID›` marker.
    - Lossless: `semantic_restore` reinserts the exact dropped text at each
      marker -> byte-for-byte original. Round-trip safe.
    - Near-dedup via SimHash: folds NON-consecutive near-duplicate multi-line
      blocks that exact dedup misses (semantically-similar repeats).

What this is NOT:
    - NOT a trained embedding/ONNX/transformer model.
    - NOT abstractive summarization (it never rewrites; it only selects + elides).
    - NOT lossy: every dropped byte is retained in `restore_blob` for retrieval.

Use for LARGE content where context budget matters: tool outputs, RAG chunks,
docs. The proxy can elide aggressively and retrieve the original on demand
(see CCR integration below).

Stdlib only (re, math, hashlib, collections). No network, no ML libs.

Public API:
    semantic_compress(text, keep=0.5) -> (compressed_text, restore_blob)
    semantic_restore(compressed_text, restore_blob) -> str   # byte-exact
    simhash(text) -> int                                     # 64-bit
    near_dup_fold(text, threshold=3) -> str
    semantic_compress_ccr(text, key_prefix) -> (compressed_text, key|None)

CLI:
    python3 simplicio_semantic.py [--keep 0.5] [--restore-test]   # reads stdin
"""

from __future__ import annotations

import hashlib
import math
import re
import sys
from collections import Counter

__all__ = [
    "semantic_compress",
    "semantic_restore",
    "simhash",
    "near_dup_fold",
    "semantic_compress_ccr",
]

# Marker template for an elided run. The ID is unique per dropped run within a
# single compress() call so restore can map it back to the exact text.
_MARKER_FMT = "‹simplicio:elided {n} lines #{id}›"
_MARKER_RE = re.compile(
    r"‹simplicio:elided (?P<n>\d+) lines #(?P<id>[0-9a-f]+)›"
)

# A near-dup fold marker (used by near_dup_fold). Not part of the lossless
# restore path — folding is a separate, opt-in shrink that points back at the
# first occurrence's block id.
_DUP_MARKER_FMT = "‹simplicio:near-dup of block #{id} ({n} lines)›"

# Lines we always keep regardless of score (structurally/diagnostically load-bearing).
_KEYWORD_RE = re.compile(
    r"(?i)\b(error|errors|fail(?:ed|ure)?|exception|traceback|fatal|panic|"
    r"warn(?:ing)?|critical|denied|refused|timeout|abort(?:ed)?)\b"
)
# Markdown / structural headers, list/section markers, code fences.
_HEADER_RE = re.compile(
    r"^\s*(?:#{1,6}\s|={3,}\s*$|-{3,}\s*$|```|\[[^\]]+\]\s*$|"
    r"[A-Z][A-Z0-9 _-]{2,}:?\s*$)"
)

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
# Sentence splitter for prose (keeps the delimiter so joining is reversible-ish;
# we only use sentence mode when the text looks like prose, not line-structured).
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

# Very common English stopwords — down-weighted so scoring tracks content terms.
_STOPWORDS = frozenset(
    "a an and are as at be by for from has have in is it its of on or that the "
    "this to was were will with not no you your we our they their he she".split()
)


def _tokens(line: str):
    """Lowercased content tokens of a line (stopwords dropped)."""
    return [
        t for t in (m.group(0).lower() for m in _TOKEN_RE.finditer(line))
        if t not in _STOPWORDS
    ]


def _looks_like_prose(text: str) -> bool:
    """Heuristic: prose = few newlines relative to sentence punctuation.

    Line-structured content (logs, code, configs) stays in line mode so we never
    break a line across a marker boundary.
    """
    nlines = text.count("\n") + 1
    nsent = len(_SENT_SPLIT_RE.findall(text)) + 1
    # Prose when there are far more sentences than physical lines.
    return nlines <= 3 and nsent >= 4


def _score_units(units):
    """Score each unit (line/sentence) by TF-IDF-ish importance + position + length.

    importance(unit) = sum over content terms of tf(term in unit) * idf(term)
        idf(term) = log( (N + 1) / (lf(term) + 1) ) + 1
        where lf = number of units containing the term (line frequency).
    Blended with:
        position: first/last units weighted up (intros/conclusions/summaries).
        length:   mild preference for substantive units, capped (avoid log spam).
    Returns a list of floats aligned with `units`.
    """
    n = len(units)
    if n == 0:
        return []
    unit_tokens = [_tokens(u) for u in units]
    # Line frequency: how many units contain each term at least once.
    lf = Counter()
    for toks in unit_tokens:
        for term in set(toks):
            lf[term] += 1
    idf = {
        term: math.log((n + 1) / (cnt + 1)) + 1.0
        for term, cnt in lf.items()
    }
    scores = []
    for i, toks in enumerate(unit_tokens):
        tf = Counter(toks)
        importance = sum(c * idf[term] for term, c in tf.items())
        # Normalize by sqrt(len) so long lines don't trivially dominate.
        denom = math.sqrt(len(toks)) if toks else 1.0
        importance /= denom
        # Position weight: first and last units get a boost (edges carry context).
        pos = 0.0
        if i == 0 or i == n - 1:
            pos = 1.5
        elif i == 1 or i == n - 2:
            pos = 0.6
        # Length weight: prefer substantive lines but cap so big blobs don't win.
        ln = len(units[i].strip())
        length_w = min(ln / 80.0, 1.0)
        scores.append(importance + pos + 0.5 * length_w)
    return scores


def _always_keep(unit: str) -> bool:
    """Structurally/diagnostically important lines kept regardless of score."""
    s = unit.strip()
    if not s:
        return False
    return bool(_KEYWORD_RE.search(unit) or _HEADER_RE.match(unit))


def _run_id(text: str, salt: int) -> str:
    """Deterministic short id for an elided run (stable per content+position)."""
    h = hashlib.blake2b(text.encode("utf-8", "surrogatepass"), digest_size=4)
    h.update(str(salt).encode("ascii"))
    return h.hexdigest()


def semantic_compress(text, keep=0.5):
    """Extractive, reversible compression.

    Split `text` into units (lines, or sentences for prose), score each, keep the
    top `keep` fraction (always keeping headers / error / keyword lines), and
    replace each maximal run of dropped units with a marker. Returns
    ``(compressed_text, restore_blob)`` where ``restore_blob`` maps marker-ID ->
    the exact dropped text. Only emits a compressed form if it actually shrinks
    the byte length; otherwise returns ``(text, {})``.

    Round-trip: ``semantic_restore(compressed_text, restore_blob) == text``.
    """
    if not isinstance(text, str) or not text:
        return text, {}
    try:
        keep = float(keep)
    except (TypeError, ValueError):
        keep = 0.5
    keep = min(max(keep, 0.0), 1.0)

    prose = _looks_like_prose(text)
    if prose:
        # Sentence mode: split keeping enough info to rejoin exactly. We capture
        # the inter-sentence whitespace so restore is byte-exact.
        units, seps = _split_keep_sep(text, _SENT_SPLIT_RE)
        joiner = None  # variable separators captured in `seps`
    else:
        # Line mode: preserve the original line terminators exactly. We split on
        # "\n" but remember whether the text ended with a trailing newline.
        units = text.split("\n")
        seps = ["\n"] * (len(units) - 1) + [""]
        joiner = "\n"

    n = len(units)
    if n < 4:
        return text, {}

    scores = _score_units(units)
    forced = [_always_keep(u) for u in units]

    # How many to keep (excluding forced lines, which are always kept on top).
    target_keep = max(1, int(math.ceil(n * keep)))
    # Rank non-forced units by score, keep the best until we hit target_keep.
    order = sorted(
        (i for i in range(n) if not forced[i]),
        key=lambda i: scores[i],
        reverse=True,
    )
    keepset = set(i for i in range(n) if forced[i])
    for i in order:
        if len(keepset) >= target_keep:
            break
        keepset.add(i)
    # If forcing already exceeded target, keepset may be > target_keep; fine.

    # Walk units; emit kept units verbatim, collapse maximal dropped runs into
    # one marker each. We rebuild using the original separators so restore is
    # byte-exact.
    out_parts = []
    restore_blob = {}
    i = 0
    salt = 0
    while i < n:
        if i in keepset:
            out_parts.append(units[i])
            out_parts.append(seps[i])
            i += 1
            continue
        # Start of a dropped run.
        j = i
        while j < n and j not in keepset:
            j += 1
        # The dropped run is units[i:j], with the separators that joined them AND
        # the separator that followed the last dropped unit (which we must also
        # preserve to be byte-exact). Reconstruct the exact original slice.
        dropped = _reassemble(units, seps, i, j, joiner)
        rid = _run_id(dropped, salt)
        # Guard against the (astronomically unlikely) id collision.
        while rid in restore_blob:
            salt += 1
            rid = _run_id(dropped, salt)
        restore_blob[rid] = dropped
        out_parts.append(_MARKER_FMT.format(n=(j - i), id=rid))
        # The marker stands in for everything in `dropped` INCLUDING its trailing
        # separator, so we do not append a separator here. But if the run is not
        # at the end, we need the boundary newline so the next kept unit starts
        # on its own line (in line mode). In prose mode the trailing sep is part
        # of `dropped`. To keep restore trivial, the marker replaces exactly the
        # `dropped` string, so append nothing.
        salt += 1
        i = j

    compressed = "".join(out_parts)
    # Only emit if it actually shrinks.
    if len(compressed.encode("utf-8")) >= len(text.encode("utf-8")):
        return text, {}
    return compressed, restore_blob


def _split_keep_sep(text, sep_re):
    """Split prose into sentences while capturing the exact separators.

    Returns (units, seps) where ``units[k] + seps[k]`` concatenated over k
    reproduces `text` exactly.
    """
    units = []
    seps = []
    pos = 0
    for m in sep_re.finditer(text):
        units.append(text[pos:m.start()])
        seps.append(text[m.start():m.end()])
        pos = m.end()
    units.append(text[pos:])
    seps.append("")
    return units, seps


def _reassemble(units, seps, i, j, joiner):
    """Reconstruct the exact original substring spanning units[i:j] + its seps.

    This is the text the marker stands in for, so restore is byte-exact.
    """
    parts = []
    for k in range(i, j):
        parts.append(units[k])
        parts.append(seps[k])
    return "".join(parts)


def semantic_restore(compressed_text, restore_blob):
    """Reinsert elided runs at their markers -> byte-exact original.

    Inverse of ``semantic_compress``. Unknown marker IDs are left untouched
    (fail-open) rather than raising.
    """
    if not isinstance(compressed_text, str) or not restore_blob:
        return compressed_text

    def _sub(m):
        rid = m.group("id")
        if rid in restore_blob:
            return restore_blob[rid]
        return m.group(0)

    return _MARKER_RE.sub(_sub, compressed_text)


# ---------------------------------------------------------------------------
# SimHash near-duplicate detection (catches non-consecutive similar blocks).
# ---------------------------------------------------------------------------

_HASH_BITS = 64


def _shingles(text):
    """Token bigram shingles for SimHash features (more robust than raw tokens)."""
    toks = [m.group(0).lower() for m in _TOKEN_RE.finditer(text)]
    if not toks:
        return []
    if len(toks) == 1:
        return [toks[0]]
    return [toks[k] + " " + toks[k + 1] for k in range(len(toks) - 1)]


def simhash(text):
    """64-bit SimHash of `text`.

    Deterministic, stdlib-only (blake2b per feature). Similar texts -> small
    Hamming distance between their hashes.
    """
    if not isinstance(text, str) or not text:
        return 0
    feats = Counter(_shingles(text))
    if not feats:
        return 0
    vec = [0] * _HASH_BITS
    for feat, weight in feats.items():
        h = int.from_bytes(
            hashlib.blake2b(feat.encode("utf-8"), digest_size=8).digest(),
            "big",
        )
        for b in range(_HASH_BITS):
            if (h >> b) & 1:
                vec[b] += weight
            else:
                vec[b] -= weight
    out = 0
    for b in range(_HASH_BITS):
        if vec[b] > 0:
            out |= (1 << b)
    return out


def _hamming(a, b):
    """Hamming distance between two 64-bit ints."""
    return bin(a ^ b).count("1")


def _split_blocks(text):
    """Split `text` into blank-line-delimited blocks, keeping the delimiters.

    Returns a list of (block_text, trailing_sep) so the blocks can be rejoined
    byte-exactly.
    """
    # Split on runs of >=1 blank line, capturing the separator.
    parts = re.split(r"(\n[ \t]*\n+)", text)
    blocks = []
    k = 0
    while k < len(parts):
        body = parts[k]
        sep = parts[k + 1] if k + 1 < len(parts) else ""
        blocks.append((body, sep))
        k += 2
    return blocks


def near_dup_fold(text, threshold=3):
    """Fold NON-consecutive near-duplicate multi-line blocks via SimHash.

    Splits `text` into blank-line-delimited blocks, SimHashes each multi-line
    block, and replaces later blocks within `threshold` Hamming distance of an
    earlier block with a `‹simplicio:near-dup of block #ID (N lines)›` marker.
    Catches semantically-similar repeats that exact dedup misses. Only emits if
    it shrinks; otherwise returns `text` unchanged.

    NOTE: This fold is a SEPARATE, lossy-by-default shrink (the marker points at
    the first occurrence, not at retained bytes). It is independent of the
    lossless ``semantic_compress`` path. Single-line blocks are never folded.
    """
    if not isinstance(text, str) or not text:
        return text
    try:
        threshold = int(threshold)
    except (TypeError, ValueError):
        threshold = 3

    blocks = _split_blocks(text)
    if len(blocks) < 2:
        return text

    seen = []  # list of (hash, block_id) for blocks we kept as canonical
    out = []
    changed = False
    for body, sep in blocks:
        nlines = body.count("\n") + 1
        # Only consider multi-line blocks for folding.
        if nlines < 2 or not body.strip():
            out.append(body)
            out.append(sep)
            continue
        h = simhash(body)
        match_id = None
        for prev_h, prev_id in seen:
            if _hamming(h, prev_h) <= threshold:
                match_id = prev_id
                break
        if match_id is not None:
            out.append(_DUP_MARKER_FMT.format(id=match_id, n=nlines))
            out.append(sep)
            changed = True
        else:
            bid = hashlib.blake2b(
                body.encode("utf-8"), digest_size=3
            ).hexdigest()
            seen.append((h, bid))
            out.append(body)
            out.append(sep)

    folded = "".join(out)
    if not changed or len(folded.encode("utf-8")) >= len(text.encode("utf-8")):
        return text
    return folded


# ---------------------------------------------------------------------------
# Optional CCR (compress-cache-retrieve) integration with simplicio_memory.
# ---------------------------------------------------------------------------

def _load_memory():
    """Import the sibling memory store if available; else None (graceful degrade)."""
    try:
        from . import simplicio_memory as mem  # type: ignore
        return mem
    except (ImportError, ValueError):
        pass
    try:
        import simplicio_memory as mem  # type: ignore
        return mem
    except ImportError:
        return None


def semantic_compress_ccr(text, key_prefix):
    """Compress, stash the restore_blob in the memory store, return (text, key).

    If ``simplicio_memory`` is importable, the elided remainder is serialized and
    stored under a generated key (``<key_prefix>:<digest>``), so the caller can
    elide aggressively and retrieve the original on demand via ``recall(key)``.

    Returns ``(compressed_text, key)``. If nothing was elided OR the memory store
    is unavailable, returns ``(text_or_compressed, None)`` and never raises.
    """
    import json

    compressed, blob = semantic_compress(text)
    if not blob:
        # Nothing elided — nothing to stash.
        return compressed, None

    mem = _load_memory()
    if mem is None:
        # No store: fail-open by returning the compressed text inline. The caller
        # gets the marker-bearing text but no recovery key. Degrade gracefully.
        return compressed, None

    payload = json.dumps(
        {"compressed": compressed, "restore_blob": blob},
        ensure_ascii=False,
    )
    digest = hashlib.blake2b(payload.encode("utf-8"), digest_size=6).hexdigest()
    key = f"{key_prefix}:{digest}"
    try:
        mem.remember(key, payload)
    except Exception:
        # Store failed (disk, perms): degrade to inline, no key.
        return compressed, None
    return compressed, key


def ccr_restore(key):
    """Retrieve and restore the byte-exact original for a CCR key, or None."""
    import json

    mem = _load_memory()
    if mem is None:
        return None
    payload = mem.recall(key)
    if not payload:
        return None
    try:
        obj = json.loads(payload)
        return semantic_restore(obj["compressed"], obj["restore_blob"])
    except (ValueError, KeyError, TypeError):
        return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv):
    keep = 0.5
    restore_test = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--keep":
            i += 1
            if i < len(argv):
                try:
                    keep = float(argv[i])
                except ValueError:
                    pass
        elif a.startswith("--keep="):
            try:
                keep = float(a.split("=", 1)[1])
            except ValueError:
                pass
        elif a == "--restore-test":
            restore_test = True
        i += 1
    return keep, restore_test


def main(argv):
    keep, restore_test = _parse_args(argv)
    text = sys.stdin.read()
    compressed, blob = semantic_compress(text, keep=keep)

    raw_bytes = len(text.encode("utf-8"))
    comp_bytes = len(compressed.encode("utf-8"))
    saved = raw_bytes - comp_bytes
    pct = (saved / raw_bytes * 100.0) if raw_bytes else 0.0

    sys.stdout.write(compressed)
    if compressed and not compressed.endswith("\n"):
        sys.stdout.write("\n")

    sys.stderr.write(
        f"[simplicio_semantic] raw={raw_bytes}B compressed={comp_bytes}B "
        f"saved={saved}B ({pct:.1f}%) elided_runs={len(blob)}\n"
    )

    if restore_test:
        restored = semantic_restore(compressed, blob)
        ok = restored == text
        sys.stderr.write(
            f"[simplicio_semantic] round-trip: {'OK' if ok else 'FAIL'}\n"
        )
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
