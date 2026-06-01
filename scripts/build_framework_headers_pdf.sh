#!/usr/bin/env bash
# Render framework-headers and fellow-banners HTML to PDF via headless Chrome.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Chrome not found at: $CHROME" >&2; exit 1; }

mkdir -p output/pdf

for base in framework-headers fellow-banners; do
  src="output/html/${base}.html"
  out="output/pdf/${base}.pdf"
  [ -f "$src" ] || { echo "Missing $src — run scripts/build_framework_headers.py first." >&2; exit 1; }
  echo "  $src  ->  $out"
  "$CHROME" \
    --headless=new \
    --disable-gpu \
    --no-sandbox \
    --no-pdf-header-footer \
    --print-to-pdf="$out" \
    --virtual-time-budget=3000 \
    "file://$ROOT/$src" \
    >/dev/null 2>&1
done

echo
ls -lh output/pdf/framework-headers.pdf output/pdf/fellow-banners.pdf | awk '{print "  " $9 "  " $5}'
