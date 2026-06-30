#!/usr/bin/env bash
# Driver de render do vídeo-tutorial multilíngue do simplicio-loop (hyperframes 0.7.x / HeyGen).
#
#   bash video/render.sh                 # gera composições + renderiza os 4 idiomas (EN ZH ES PT)
#   bash video/render.sh pt-BR           # só um idioma
#   bash video/render.sh reel            # concatena os 4 num único MP4 (EN→ZH→ES→PT)
#
# Requisitos (BLOCK se faltar, nunca fake-pass): Node.js 22+, FFmpeg, hyperframes (via npx).
# Saída: video/out/simplicio-loop_<lang>.mp4 e (modo reel) video/out/simplicio-loop_reel.mp4
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/out"
LANGS=(en zh-CN es pt-BR)
FPS=30
QUALITY=high
mkdir -p "$OUT"

preflight() {
  command -v node >/dev/null || { echo "BLOCKED: Node.js 22+ ausente"; exit 3; }
  command -v ffmpeg >/dev/null || { echo "BLOCKED: FFmpeg ausente"; exit 3; }
  local major; major="$(node -p 'process.versions.node.split(".")[0]')"
  [ "$major" -ge 22 ] || { echo "BLOCKED: Node $major (precisa 22+)"; exit 3; }
}

render_lang() {
  local lang="$1"
  echo "▸ render $lang"
  ( cd "$HERE/hyperframes/$lang" && npx --yes hyperframes lint >/dev/null 2>&1 || true
    npx --yes hyperframes render . -o "$OUT/simplicio-loop_$lang.mp4" -f "$FPS" -q "$QUALITY" )
  echo "  ✓ $OUT/simplicio-loop_$lang.mp4"
}

build_reel() {
  local list="$OUT/_concat.txt"; : > "$list"
  for lang in "${LANGS[@]}"; do
    [ -f "$OUT/simplicio-loop_$lang.mp4" ] && echo "file 'simplicio-loop_$lang.mp4'" >> "$list"
  done
  echo "▸ reel EN→ZH→ES→PT"
  ffmpeg -y -f concat -safe 0 -i "$list" -c copy "$OUT/simplicio-loop_reel.mp4"
  echo "  ✓ $OUT/simplicio-loop_reel.mp4"
}

preflight
python3 "$HERE/build_composition.py" >/dev/null
python3 "$HERE/build_srt.py" >/dev/null

case "${1:-all}" in
  reel) for l in "${LANGS[@]}"; do render_lang "$l"; done; build_reel ;;
  all)  for l in "${LANGS[@]}"; do render_lang "$l"; done ;;
  *)    render_lang "$1" ;;
esac
echo "done."
