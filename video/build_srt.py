#!/usr/bin/env python3
"""Gera arquivos .srt por idioma a partir de video/lang/*.json (timing do storyboard).

Determinístico, stdlib-only. Uso:
    python3 video/build_srt.py            # gera todos os idiomas
    python3 video/build_srt.py en pt-BR   # subconjunto
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANG_DIR = HERE / "lang"
LANGS = ["en", "zh-CN", "es", "pt-BR"]


def _ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build(lang: str) -> Path:
    data = json.loads((LANG_DIR / f"{lang}.json").read_text(encoding="utf-8"))
    lines = []
    for i, sc in enumerate(data["scenes"], start=1):
        start = float(sc["start_s"])
        end = start + float(sc["duration_s"])
        # legenda = narração (fala do vídeo); recua 0.1s do fim p/ respiro
        text = sc.get("narration", sc.get("caption", "")).strip()
        lines.append(str(i))
        lines.append(f"{_ts(start)} --> {_ts(max(start + 0.5, end - 0.1))}")
        lines.append(text)
        lines.append("")
    out = LANG_DIR / f"{lang}.srt"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    targets = sys.argv[1:] or LANGS
    for lang in targets:
        if lang not in LANGS:
            print(f"skip: unknown lang {lang}")
            continue
        out = build(lang)
        print(f"wrote {out.relative_to(HERE.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
