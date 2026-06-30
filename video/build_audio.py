#!/usr/bin/env python3
"""Monta a faixa de áudio do vídeo: narração TTS por cena (macOS `say`) + trilha sintetizada
(ffmpeg) + mix, e faz o mux no MP4 renderizado pelo hyperframes.

Saída: video/out/simplicio-loop_<lang>_av.mp4 (vídeo + som)

Uso:
    python3 video/build_audio.py pt-BR
Requer: macOS `say`, ffmpeg, ffprobe. O vídeo mudo deve existir em
video/out/simplicio-loop_<lang>.mp4 (gerado por `npx hyperframes render`).
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
TMP = OUT / "_audio_tmp"
LANG_DIR = HERE / "lang"

# voz `say` por idioma (pt-BR confirmado: Luciana). Outras best-effort.
VOICE = {"pt-BR": "Luciana", "en": "Samantha", "es": "Monica", "zh-CN": "Tingting"}
SR = 48000


def run(argv):
    subprocess.run(argv, check=True, capture_output=True)


def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def main():
    lang = sys.argv[1] if len(sys.argv) > 1 else "pt-BR"
    voice = VOICE.get(lang, "Samantha")
    data = json.loads((LANG_DIR / ("%s.json" % lang)).read_text(encoding="utf-8"))
    video = OUT / ("simplicio-loop_%s.mp4" % lang)
    if not video.exists():
        print("BLOCKED: vídeo mudo ausente: %s (rode hyperframes render antes)" % video)
        return 3
    TMP.mkdir(parents=True, exist_ok=True)
    total = dur(video)

    # 1) narração por cena → wav 48k mono, colocada no start_s da cena (adelay)
    inputs, delays, idx = [], [], 0
    for sc in data["scenes"]:
        text = sc.get("narration", "").strip()
        if not text:
            continue
        aiff = TMP / ("n%02d.aiff" % sc["id"]); wav = TMP / ("n%02d.wav" % sc["id"])
        run(["say", "-v", voice, "-r", "185", "-o", str(aiff), text])
        run(["ffmpeg", "-y", "-i", str(aiff), "-ar", str(SR), "-ac", "1", str(wav)])
        inputs += ["-i", str(wav)]
        delays.append((idx, int(float(sc["start_s"]) * 1000)))
        idx += 1

    # 2) trilha tech: drone (root+fifth detuned) + tremolo, baixinho sob a narração
    bed = TMP / "bed.wav"
    run(["ffmpeg", "-y",
         "-f", "lavfi", "-t", "%g" % total, "-i", "sine=frequency=82.4:sample_rate=%d" % SR,
         "-f", "lavfi", "-t", "%g" % total, "-i", "sine=frequency=123.47:sample_rate=%d" % SR,
         "-f", "lavfi", "-t", "%g" % total, "-i", "sine=frequency=164.81:sample_rate=%d" % SR,
         "-filter_complex",
         "[0:a]volume=0.5[a0];[1:a]volume=0.32[a1];[2:a]volume=0.22[a2];"
         "[a0][a1][a2]amix=inputs=3:normalize=0,tremolo=f=4:d=0.35,"
         "highpass=f=60,lowpass=f=1600,volume=0.16,afade=t=in:st=0:d=2,"
         "afade=t=out:st=%g:d=2.5[bed]" % max(0.0, total - 2.5),
         "-map", "[bed]", "-ar", str(SR), "-ac", "1", str(bed)])

    # 3) mix narração (delayed) + bed → master
    master = TMP / "master.wav"
    fc = []
    for i, ms in delays:
        fc.append("[%d:a]adelay=%d|%d,volume=1.35[d%d];" % (i, ms, ms, i))
    nar_lbls = "".join("[d%d]" % i for i, _ in delays)
    nbed = len(inputs) // 2
    fc.append("%s[%d:a]amix=inputs=%d:normalize=0:dropout_transition=0,alimiter=limit=0.95[mix]"
              % (nar_lbls, nbed, len(delays) + 1))
    run(["ffmpeg", "-y", *inputs, "-i", str(bed),
         "-filter_complex", "".join(fc), "-map", "[mix]",
         "-ar", str(SR), "-ac", "2", str(master)])

    # 4) mux no vídeo
    av = OUT / ("simplicio-loop_%s_av.mp4" % lang)
    run(["ffmpeg", "-y", "-i", str(video), "-i", str(master),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(av)])
    print("wrote %s" % av.relative_to(HERE.parent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
