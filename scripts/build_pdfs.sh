#!/usr/bin/env bash
# Convert each output/html/*.html to output/pdf/*.pdf using headless Chrome.
# Usage: scripts/build_pdfs.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ ! -x "$CHROME" ]; then
  echo "Chrome not found at: $CHROME" >&2
  exit 1
fi

mkdir -p output/pdf

shopt -s nullglob
files=(output/html/*.html)
if [ "${#files[@]}" -eq 0 ]; then
  echo "No HTML files in output/html/. Run scripts/build_packets.py first." >&2
  exit 1
fi

for f in "${files[@]}"; do
  base="$(basename "$f" .html)"
  out="output/pdf/${base}.pdf"
  echo "  $base.html  ->  $out"
  "$CHROME" \
    --headless=new \
    --disable-gpu \
    --no-sandbox \
    --no-pdf-header-footer \
    --print-to-pdf="$out" \
    --virtual-time-budget=2000 \
    "file://$ROOT/$f" \
    >/dev/null 2>&1
done

echo
echo "PDFs:"
ls -lh output/pdf/*.pdf | awk '{print "  " $9 "  " $5}'
