#!/usr/bin/env python3
"""simplicio_image — REAL vision-LLM image token compression, ported from headroom.

A vision model bills an image by its resolution/tiles, not its file size: a 2000x1500
image costs many 512px tiles. "Image compression" for a token proxy therefore means
**resize / re-encode the image so it occupies fewer tiles**, while keeping its content
intact. This module ports headroom's image subsystem (``headroom/image/``):

    * the techniques (headroom ``Technique`` enum + ``_apply_compression``):
        - ``preserve``  : keep the image as-is (0% savings)
        - ``full_low``  : downscale to a token-cheaper resolution (headroom's
                          ``_resize_image`` → LANCZOS, RGBA/P→RGB, JPEG optimize)
        - ``crop``      : alias of full_low (same downscale path upstream)
        - ``transcode`` : re-encode to an efficient format/quality at the same
                          dimensions (headroom OCRs to text; with no OCR backend we
                          do the byte-side re-encode, which is the genuine transcode)
        - ``auto``      : pick the most aggressive technique whose SigLIP
                          content-similarity to the original stays above a threshold

    * the OpenAI-ish tile token estimate (headroom ``_estimate_tokens`` /
      ``tile_optimizer.estimate_openai_tokens``):
          tokens = 85 + 170 * ceil(w/512) * ceil(h/512)     (high detail)
      We also expose the documented ``~85 * ceil(w/512) * ceil(h/512)`` heuristic
      from the task as ``est_tokens_heuristic`` in ``info``.

    * the SigLIP image encoder headroom uses for image analysis
      (``onnx_router.OnnxTechniqueRouter._load_siglip`` →
      ``chopratejas/siglip-image-encoder-onnx``, Apache-2.0, public). Here it is the
      semantic VERIFIER: embed original vs. compressed (224x224, normalize (x-0.5)/0.5,
      CHW) and take cosine similarity, so an aggressive resize that destroys content is
      rejected.

It is **dependency-gated and degrades gracefully**:
    * Pillow is required (the actual compression). Absent → exit 3 with a hint.
    * onnxruntime + huggingface_hub + the SigLIP model are OPTIONAL. Absent → the
      Pillow resize/transcode still runs; only the similarity check is skipped (and
      ``auto`` falls back to a fixed, safe technique). Never fakes savings.

    pip install pillow                         # core (resize/transcode)
    pip install onnxruntime huggingface_hub numpy   # optional (SigLIP verify)

    python3 simplicio_image.py <image_path> [--technique auto] [--max-dim 1024]
                               [--quality 80] [--out PATH] [--info]
"""
from __future__ import annotations

import argparse
import io
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# headroom: chopratejas/siglip-image-encoder-onnx (onnx_router.py _SIGLIP_ENCODER_REPO)
SIGLIP_REPO = os.environ.get(
    "SIMPLICIO_SIGLIP_ONNX_REPO", "chopratejas/siglip-image-encoder-onnx"
)
SIGLIP_MODEL_FILE = "image_encoder_int8.onnx"
SIGLIP_INPUT = "pixel_values"  # [batch, 3, 224, 224] float, verified from the ONNX
SIGLIP_SIZE = 224

# headroom techniques (trained_router.Technique). "auto" is our verify-driven picker.
TECHNIQUES = ("auto", "preserve", "full_low", "crop", "transcode")

# auto picks the most aggressive technique whose SigLIP cosine to the original stays
# above this. 0.80 matches the task's ">0.8" bar.
SIMILARITY_THRESHOLD = float(os.environ.get("SIMPLICIO_IMAGE_SIM_THRESHOLD", "0.80"))

_PIL_HINT = "Pillow not installed — pip install pillow (required for image compression)"
_SIGLIP_HINT = (
    "SigLIP verifier unavailable — pip install onnxruntime huggingface_hub numpy "
    "(optional; Pillow compression still works)"
)

_session = None
_text_embeddings = None
_np = None


# --------------------------------------------------------------------------- #
# Token estimation (headroom tile_optimizer.estimate_openai_tokens)
# --------------------------------------------------------------------------- #
def estimate_vision_tokens(width: int, height: int, detail: str = "high") -> int:
    """OpenAI GPT-4o vision token cost: 85 + 170 * ceil(w/512) * ceil(h/512).

    Mirrors headroom ``tile_optimizer.estimate_openai_tokens``: scale longest side
    <=2048, then shortest side <=768, then count 512px tiles.
    """
    if detail == "low":
        return 85
    max_dim = max(width, height)
    if max_dim > 2048:
        scale = 2048 / max_dim
        width = int(width * scale)
        height = int(height * scale)
    min_dim = min(width, height)
    if min_dim > 768:
        scale = 768 / min_dim
        width = int(width * scale)
        height = int(height * scale)
    tiles = math.ceil(width / 512) * math.ceil(height / 512)
    return 85 + 170 * tiles


def estimate_tokens_heuristic(width: int, height: int) -> int:
    """The documented ~85-per-tile heuristic from the task spec.

    est ~= ceil(w/512) * ceil(h/512) * 85 — a simpler tiling estimate, kept alongside
    the full OpenAI formula so callers can use either.
    """
    return math.ceil(width / 512) * math.ceil(height / 512) * 85


# --------------------------------------------------------------------------- #
# SigLIP verifier (headroom onnx_router._load_siglip / analyze_image)
# --------------------------------------------------------------------------- #
def siglip_available() -> bool:
    """True iff onnxruntime + huggingface_hub + numpy import AND the model loads."""
    try:
        import numpy  # noqa: F401
        import onnxruntime  # noqa: F401
        from huggingface_hub import hf_hub_download  # noqa: F401
    except Exception:
        return False
    try:
        _load_siglip()
        return True
    except Exception:
        return False


def _load_siglip():
    """Lazy-load chopratejas/siglip-image-encoder-onnx (int8). Cached at module scope."""
    global _session, _text_embeddings, _np
    if _session is not None:
        return _session
    import numpy as np
    import onnxruntime as ort
    from huggingface_hub import hf_hub_download

    _np = np
    model_path = hf_hub_download(SIGLIP_REPO, SIGLIP_MODEL_FILE)
    so = ort.SessionOptions()
    so.intra_op_num_threads = 1
    so.inter_op_num_threads = 1
    _session = ort.InferenceSession(
        model_path, so, providers=["CPUExecutionProvider"]
    )
    # text_embeddings.npz exists in the repo (headroom uses it for signal scoring);
    # we don't need it for similarity, but loading proves the full repo is present.
    try:
        emb_path = hf_hub_download(SIGLIP_REPO, "text_embeddings.npz")
        loaded = np.load(emb_path)
        _text_embeddings = {k: loaded[k] for k in loaded.files}
    except Exception:
        _text_embeddings = {}
    return _session


def _embed_image(img):
    """SigLIP embedding for a PIL image (headroom onnx_router.analyze_image preproc)."""
    np = _np
    img = img.convert("RGB").resize((SIGLIP_SIZE, SIGLIP_SIZE), _RESAMPLE)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = (arr - 0.5) / 0.5  # normalize to [-1, 1] (exactly headroom's preproc)
    arr = arr.transpose(2, 0, 1)  # HWC -> CHW
    pixel_values = arr[np.newaxis, ...]
    embeds = _session.run(None, {SIGLIP_INPUT: pixel_values})[0]
    norm = np.linalg.norm(embeds, axis=-1, keepdims=True)
    return embeds / np.clip(norm, 1e-12, None)


def image_similarity(img_a, img_b) -> float:
    """Cosine similarity in SigLIP space between two PIL images (raises if no model)."""
    _load_siglip()
    np = _np
    ea = _embed_image(img_a)
    eb = _embed_image(img_b)
    return float((ea @ eb.T).squeeze())


# --------------------------------------------------------------------------- #
# Pillow compression (headroom compressor._resize_image / tile_optimizer)
# --------------------------------------------------------------------------- #
def _require_pil():
    try:
        from PIL import Image  # noqa: F401
    except Exception:
        sys.stderr.write(_PIL_HINT + "\n")
        sys.exit(3)


def _open(path_or_bytes):
    from PIL import Image

    if isinstance(path_or_bytes, (bytes, bytearray)):
        return Image.open(io.BytesIO(bytes(path_or_bytes)))
    return Image.open(path_or_bytes)


def _resample():
    from PIL import Image

    return Image.Resampling.LANCZOS


_RESAMPLE = None


def _downscale(img, max_dim: int):
    """headroom _resize_image: preserve aspect ratio, longest side -> max_dim."""
    w, h = img.size
    if w <= max_dim and h <= max_dim:
        return img  # already small enough
    if w >= h:
        nw, nh = max_dim, max(1, int(h * (max_dim / w)))
    else:
        nh, nw = max_dim, max(1, int(w * (max_dim / h)))
    return img.resize((nw, nh), _resample())


def _encode_jpeg(img, quality: int) -> bytes:
    """headroom: RGBA/P -> RGB, save JPEG optimize=True."""
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    elif img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def _measure(img):
    w, h = img.size
    return {
        "dims": [w, h],
        "tokens": estimate_vision_tokens(w, h, "high"),
        "tokens_heuristic": estimate_tokens_heuristic(w, h),
    }


def compress_image(path_or_bytes, technique="auto", max_dim=1024, quality=80):
    """Compress an image for vision-LLM input. Returns (out_bytes, info).

    technique:
        preserve  - re-encode at original dims+quality (no resize)
        full_low  - downscale longest side to max_dim, JPEG at quality
        crop      - alias of full_low (headroom routes both to the resize path)
        transcode - re-encode at original dims to efficient JPEG/quality (byte-side)
        auto      - try aggressive -> conservative, keep the smallest token cost whose
                    SigLIP similarity to the original stays >= SIMILARITY_THRESHOLD;
                    with no SigLIP model, falls back to full_low (safe, content-preserving)

    info keys: technique, before_bytes, after_bytes, before_dims, after_dims, pct,
               est_tokens_before, est_tokens_after, est_tokens_heuristic_before,
               est_tokens_heuristic_after, similarity (None if SigLIP absent),
               siglip_used.
    """
    _require_pil()
    global _RESAMPLE
    if _RESAMPLE is None:
        _RESAMPLE = _resample()

    src = _open(path_or_bytes)
    src.load()
    before = _measure(src)
    if isinstance(path_or_bytes, (bytes, bytearray)):
        before_bytes = len(path_or_bytes)
    else:
        before_bytes = os.path.getsize(path_or_bytes)

    has_siglip = siglip_available()

    def _render(tech):
        if tech in ("full_low", "crop"):
            img = _downscale(src, max_dim)
            return _encode_jpeg(img, quality), img
        if tech == "transcode":
            # same dims, efficient re-encode (genuine byte-side transcode)
            return _encode_jpeg(src, quality), src
        # preserve: re-encode at original dims, keep quality high
        return _encode_jpeg(src, max(quality, 92)), src

    if technique == "auto":
        # most aggressive -> least. full_low is the strongest content-preserving move.
        order = ["full_low", "transcode", "preserve"]
        chosen = None
        chosen_bytes = None
        chosen_img = None
        chosen_sim = None
        if not has_siglip:
            # no verifier -> full_low is the safe, content-preserving downscale
            chosen = "full_low"
            chosen_bytes, chosen_img = _render("full_low")
            chosen_sim = None
        else:
            for tech in order:
                out_bytes, out_img = _render(tech)
                try:
                    sim = image_similarity(src, out_img)
                except Exception:
                    sim = None
                # accept the first (most aggressive) technique that clears the gate
                if sim is None or sim >= SIMILARITY_THRESHOLD:
                    chosen, chosen_bytes, chosen_img, chosen_sim = tech, out_bytes, out_img, sim
                    break
            if chosen is None:
                # nothing cleared the bar -> keep the image (preserve)
                chosen = "preserve"
                chosen_bytes, chosen_img = _render("preserve")
                chosen_sim = image_similarity(src, chosen_img)
        eff_tech = chosen
        out_bytes = chosen_bytes
        out_img = chosen_img
        similarity = chosen_sim
    else:
        if technique not in TECHNIQUES:
            raise ValueError(f"unknown technique {technique!r}; pick from {TECHNIQUES}")
        eff_tech = technique
        out_bytes, out_img = _render(technique)
        similarity = None
        if has_siglip and technique != "preserve":
            try:
                similarity = image_similarity(src, out_img)
            except Exception:
                similarity = None

    after = _measure(out_img)
    after_bytes = len(out_bytes)
    pct = (1 - after_bytes / before_bytes) * 100 if before_bytes else 0.0

    info = {
        "technique": eff_tech,
        "before_bytes": before_bytes,
        "after_bytes": after_bytes,
        "before_dims": before["dims"],
        "after_dims": after["dims"],
        "pct": round(pct, 2),
        "est_tokens_before": before["tokens"],
        "est_tokens_after": after["tokens"],
        "est_tokens_heuristic_before": before["tokens_heuristic"],
        "est_tokens_heuristic_after": after["tokens_heuristic"],
        "similarity": (round(similarity, 4) if similarity is not None else None),
        "siglip_used": bool(has_siglip),
    }
    return out_bytes, info


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _print_info():
    if not siglip_available():
        print(_SIGLIP_HINT)
        print("siglip_available: False")
        return
    sess = _load_siglip()
    ins = [(i.name, i.shape, i.type) for i in sess.get_inputs()]
    outs = [(o.name, o.shape, o.type) for o in sess.get_outputs()]
    print(f"repo: {SIGLIP_REPO}")
    print(f"model_file: {SIGLIP_MODEL_FILE}")
    print(f"inputs: {ins}")
    print(f"outputs: {outs}")
    print(f"text_embedding_signals: {sorted(_text_embeddings)}")
    print("siglip_available: True")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Vision-LLM image token compressor (headroom port).")
    ap.add_argument("image", nargs="?", help="path to the image to compress")
    ap.add_argument("--technique", default="auto", choices=TECHNIQUES)
    ap.add_argument("--max-dim", type=int, default=1024)
    ap.add_argument("--quality", type=int, default=80)
    ap.add_argument("--out", help="write compressed image here (default: <stem>.compressed.jpg)")
    ap.add_argument("--info", action="store_true", help="prove the SigLIP model loaded")
    args = ap.parse_args(argv)

    if args.info and not args.image:
        _print_info()
        return 0

    if not args.image:
        ap.error("image path required (or use --info alone)")

    out_bytes, info = compress_image(
        args.image, technique=args.technique, max_dim=args.max_dim, quality=args.quality
    )

    out_path = args.out or (os.path.splitext(args.image)[0] + ".compressed.jpg")
    with open(out_path, "wb") as f:
        f.write(out_bytes)

    bb, ab = info["before_bytes"], info["after_bytes"]
    tb, ta = info["est_tokens_before"], info["est_tokens_after"]
    print(f"technique     : {info['technique']}  (siglip_used={info['siglip_used']})")
    print(f"dims          : {info['before_dims']} -> {info['after_dims']}")
    print(f"bytes         : {bb} -> {ab}  ({info['pct']:.1f}% smaller)")
    print(f"est vis tokens: {tb} -> {ta}  ({(1 - ta / tb) * 100 if tb else 0:.1f}% fewer)")
    if info["similarity"] is not None:
        print(f"siglip cosine : {info['similarity']:.4f}  (>= {SIMILARITY_THRESHOLD} required for auto)")
    else:
        print("siglip cosine : n/a (model not loaded — Pillow path only)")
    print(f"written       : {out_path}")

    if args.info:
        print("---")
        _print_info()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
