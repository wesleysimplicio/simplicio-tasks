#!/usr/bin/env python3
"""simplicio_kompress — REAL headroom ONNX semantic token-pruning compressor.

Wraps the public `chopratejas/kompress-v2-base` model (Apache-2.0, headroom labs)
to compress text by dropping low-importance tokens. The model is a dual-head
ModernBERT (token keep/discard + span importance CNN) exported to ONNX so the two
heads are fused into a single per-token `final_scores` output in [0,1].

This is the actual headroom inference, not a substitute:
  - downloads the real ONNX weights + tokenizer from HuggingFace (cached),
  - runs onnxruntime with the model's real I/O signature
    (input_ids,attention_mask int64 -> final_scores float [batch,seq]),
  - scores every token, reduces to per-word scores (max over the word's tokens,
    exactly as headroom does via `word_ids`), keeps the top `keep_rate` fraction,
  - drops the rest and reconstructs the kept text.

Reversibility: `restore_info` carries the original word list and the kept indices,
so `kompress_restore(restore_info)` rebuilds the original byte-for-byte.

CLI:
    echo "<text>" | python3 simplicio_kompress.py [--keep 0.6] [--info]

Env:
    SIMPLICIO_KOMPRESS_REPO   model repo id (default chopratejas/kompress-v2-base)
    SIMPLICIO_KOMPRESS_ONNX   onnx file in repo (default onnx/kompress-int8-wo.onnx)

Graceful: if deps/model are absent it prints an install hint and exits 3.
"""
from __future__ import annotations

import json
import os
import sys
import threading
from typing import Any

# Default model — the real headroom kompress-v2-base. Overridable via env.
DEFAULT_REPO = os.environ.get("SIMPLICIO_KOMPRESS_REPO", "chopratejas/kompress-v2-base")
# ONNX artifacts to try in order (mirrors headroom's fall-through: weight-only
# int8 first at 274MB, lossless fp32 next). An explicit env pins one file first.
_DEFAULT_ONNX_CANDIDATES = ("onnx/kompress-int8-wo.onnx", "onnx/kompress-fp32.onnx")
# Inference config, matched to how kompress-v2-base was trained/served.
CHUNK_WORDS = 350      # headroom KompressConfig.chunk_words default
MAX_LENGTH = 512       # ModernBERT max sequence (headroom truncation)
SCORE_THRESHOLD = 0.5  # headroom score_threshold (used when keep_rate is None)

_MISSING_DEPS_MSG = (
    "kompress model not available — pip install onnxruntime huggingface_hub tokenizers"
)

# Lazy, thread-safe cache of (session, tokenizer, meta).
_cache: dict[str, tuple[Any, Any, dict[str, Any]]] = {}
_lock = threading.Lock()


def _onnx_candidates() -> tuple[str, ...]:
    override = os.environ.get("SIMPLICIO_KOMPRESS_ONNX", "").strip()
    if override:
        return (override, *(c for c in _DEFAULT_ONNX_CANDIDATES if c != override))
    return _DEFAULT_ONNX_CANDIDATES


def _import_deps() -> tuple[Any, Any, Any, Any] | None:
    """Import the hard deps. Return modules or None if any is missing."""
    try:
        import numpy as np
        import onnxruntime as ort
        from huggingface_hub import hf_hub_download
        from tokenizers import Tokenizer
    except ImportError:
        return None
    return np, ort, hf_hub_download, Tokenizer


def kompress_available(repo: str = DEFAULT_REPO) -> bool:
    """True iff deps import AND the model+tokenizer are downloadable/cached.

    Tries the local cache first (no network), then a network download. Returns
    False on any failure so callers can degrade gracefully.
    """
    deps = _import_deps()
    if deps is None:
        return False
    _np, _ort, hf_hub_download, _Tokenizer = deps
    # Tokenizer must resolve.
    if not _resolve(hf_hub_download, repo, "tokenizer.json"):
        return False
    # At least one ONNX artifact must resolve.
    for cand in _onnx_candidates():
        if _resolve(hf_hub_download, repo, cand):
            return True
    return False


def _resolve(hf_hub_download: Any, repo: str, filename: str) -> str | None:
    """Resolve a repo file to a local path: cache-only first, then network."""
    for local_only in (True, False):
        try:
            return hf_hub_download(repo, filename, local_files_only=local_only)
        except Exception:
            continue
    return None


def _load(repo: str = DEFAULT_REPO) -> tuple[Any, Any, dict[str, Any]]:
    """Lazy-load and cache the ONNX session + tokenizer for `repo`.

    Raises RuntimeError if deps/model are unavailable.
    """
    if repo in _cache:
        return _cache[repo]
    with _lock:
        if repo in _cache:
            return _cache[repo]

        deps = _import_deps()
        if deps is None:
            raise RuntimeError(_MISSING_DEPS_MSG)
        _np, ort, hf_hub_download, Tokenizer = deps

        tok_path = _resolve(hf_hub_download, repo, "tokenizer.json")
        if not tok_path:
            raise RuntimeError(f"tokenizer.json not found in {repo}")

        session = None
        onnx_used = None
        last_err: Exception | None = None
        for cand in _onnx_candidates():
            onnx_path = _resolve(hf_hub_download, repo, cand)
            if not onnx_path:
                continue
            try:
                session = ort.InferenceSession(
                    onnx_path, providers=["CPUExecutionProvider"]
                )
                onnx_used = cand
                break
            except Exception as exc:  # e.g. MatMulNBits unsupported -> next file
                last_err = exc
                continue
        if session is None:
            raise RuntimeError(
                f"no loadable ONNX artifact in {repo}; tried {_onnx_candidates()}"
                + (f" ({last_err})" if last_err else "")
            )

        tokenizer = Tokenizer.from_file(tok_path)
        in_sig = [(i.name, i.type, list(i.shape)) for i in session.get_inputs()]
        out_sig = [(o.name, o.type, list(o.shape)) for o in session.get_outputs()]
        out_name = session.get_outputs()[0].name  # 'final_scores'
        meta = {
            "repo": repo,
            "onnx_file": onnx_used,
            "onnx_path": onnx_path,
            "tokenizer_path": tok_path,
            "inputs": in_sig,
            "outputs": out_sig,
            "output_name": out_name,
            "providers": session.get_providers(),
        }
        _cache[repo] = (session, tokenizer, meta)
        return _cache[repo]


def _word_scores_for_chunk(
    session: Any, tokenizer: Any, np: Any, chunk_words: list[str], out_name: str
) -> dict[int, float]:
    """Run the real ONNX model on one word-chunk -> {word_index: max_token_score}.

    Tokenizes the words split-into-words (so each token maps back to a source
    word via `word_ids`), runs the session, then reduces token scores to a
    per-word score with max — identical to headroom's reduction.
    """
    enc = tokenizer.encode(chunk_words, is_pretokenized=True)
    ids = enc.ids[:MAX_LENGTH]
    mask = enc.attention_mask[:MAX_LENGTH]
    word_ids = enc.word_ids[:MAX_LENGTH]

    input_ids = np.asarray([ids], dtype=np.int64)
    attention_mask = np.asarray([mask], dtype=np.int64)
    scores = session.run(
        [out_name], {"input_ids": input_ids, "attention_mask": attention_mask}
    )[0][0]  # [seq]

    word_scores: dict[int, float] = {}
    for idx, wid in enumerate(word_ids):
        if wid is None:
            continue
        s = float(scores[idx])
        if wid not in word_scores or s > word_scores[wid]:
            word_scores[wid] = s
    return word_scores


def kompress_compress(
    text: str, keep_rate: float = 0.6, repo: str = DEFAULT_REPO
) -> tuple[str, dict[str, Any]]:
    """Compress `text` by dropping low-importance words, per the real model.

    Two scoring modes, both using the real model's per-token `final_scores`:

      - keep_rate < 1.0 (a budget): pure top-k per chunk, keeping the top
        `keep_rate` fraction of words by score. This is headroom's
        `target_ratio` path — a hard budget, so the % saved tracks keep_rate.
      - keep_rate >= 1.0 (model decides): keep every word the model scores
        above SCORE_THRESHOLD (headroom's default keep-mask). The model alone
        sets how much is dropped.

    Args:
        text: input prose / log / structured output.
        keep_rate: target fraction of words to keep per chunk. 1.0 -> let the
            model decide via its 0.5 threshold; <1.0 -> hard top-k budget.
        repo: model repo id (default kompress-v2-base).

    Returns:
        (compressed_text, restore_info). `restore_info` is reversible:
        kompress_restore(restore_info) -> original text byte-for-byte.
    """
    session, tokenizer, meta = _load(repo)
    deps = _import_deps()
    assert deps is not None  # _load would have raised
    np = deps[0]

    words = text.split()
    n_words = len(words)
    out_name = meta["output_name"]

    # Tiny inputs: keep verbatim (headroom passes through <10 words).
    if n_words < 10:
        info = {
            "repo": repo,
            "original_words": words,
            "kept_indices": list(range(n_words)),
            "n_words": n_words,
            "n_kept": n_words,
            "keep_rate": keep_rate,
            "model_ran": False,
            "reason": "too_short",
        }
        return text, info

    keep_rate = max(0.0, min(1.0, float(keep_rate)))
    kept_indices: set[int] = set()

    for chunk_start in range(0, n_words, CHUNK_WORDS):
        chunk = words[chunk_start : chunk_start + CHUNK_WORDS]
        word_scores = _word_scores_for_chunk(session, tokenizer, np, chunk, out_name)
        if not word_scores:
            # Reduction produced nothing — keep this chunk verbatim, lossless.
            kept_indices.update(range(chunk_start, chunk_start + len(chunk)))
            continue
        if keep_rate >= 1.0:
            # Model-decides mode: keep words scored above the 0.5 threshold
            # (headroom's default keep-mask).
            for wid, sc in word_scores.items():
                if sc > SCORE_THRESHOLD:
                    kept_indices.add(wid + chunk_start)
        else:
            # Budget mode: pure top-k by score (headroom's target_ratio path).
            ordered = sorted(word_scores, key=lambda w: word_scores[w], reverse=True)
            num_keep = max(1, int(round(len(ordered) * keep_rate)))
            for wid in ordered[:num_keep]:
                kept_indices.add(wid + chunk_start)

    kept_sorted = sorted(i for i in kept_indices if i < n_words)
    compressed = " ".join(words[i] for i in kept_sorted)

    info = {
        "repo": repo,
        "onnx_file": meta["onnx_file"],
        "original_words": words,
        "kept_indices": kept_sorted,
        "n_words": n_words,
        "n_kept": len(kept_sorted),
        "keep_rate": keep_rate,
        "model_ran": True,
    }
    return compressed, info


def kompress_restore(restore_info: dict[str, Any]) -> str:
    """Rebuild the original text from `restore_info` (byte-for-byte)."""
    words = restore_info.get("original_words", [])
    return " ".join(words)


def _percent_saved(info: dict[str, Any]) -> float:
    n = info.get("n_words", 0)
    if not n:
        return 0.0
    return (1.0 - info.get("n_kept", n) / n) * 100.0


def _model_info_dict(repo: str) -> dict[str, Any]:
    _s, _t, meta = _load(repo)
    return {
        "repo": meta["repo"],
        "onnx_file": meta["onnx_file"],
        "onnx_path": meta["onnx_path"],
        "tokenizer_path": meta["tokenizer_path"],
        "providers": meta["providers"],
        "inputs": meta["inputs"],
        "outputs": meta["outputs"],
    }


def _main(argv: list[str]) -> int:
    keep = 0.6
    want_info = False
    repo = DEFAULT_REPO
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--keep" and i + 1 < len(argv):
            try:
                keep = float(argv[i + 1])
            except ValueError:
                print(f"invalid --keep value: {argv[i + 1]}", file=sys.stderr)
                return 2
            i += 2
            continue
        if a == "--info":
            want_info = True
            i += 1
            continue
        if a == "--repo" and i + 1 < len(argv):
            repo = argv[i + 1]
            i += 2
            continue
        if a in ("-h", "--help"):
            print(__doc__)
            return 0
        print(f"unknown arg: {a}", file=sys.stderr)
        return 2

    if not kompress_available(repo):
        print(_MISSING_DEPS_MSG, file=sys.stderr)
        return 3

    if want_info:
        try:
            print(json.dumps(_model_info_dict(repo), indent=2))
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 3
        return 0

    text = sys.stdin.read()
    if not text.strip():
        print("(no input on stdin)", file=sys.stderr)
        return 2

    try:
        compressed, info = kompress_compress(text, keep_rate=keep, repo=repo)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 3

    sys.stdout.write(compressed)
    if not compressed.endswith("\n"):
        sys.stdout.write("\n")

    saved = _percent_saved(info)
    print(
        f"[simplicio-kompress] repo={info.get('repo')} "
        f"onnx={info.get('onnx_file', 'n/a')} model_ran={info.get('model_ran')} "
        f"words {info.get('n_words')}->{info.get('n_kept')} "
        f"keep_rate={info.get('keep_rate')} saved={saved:.1f}%",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
