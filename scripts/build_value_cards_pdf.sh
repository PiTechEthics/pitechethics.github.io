#!/usr/bin/env bash
# Render output/html/value-card-deck.html to output/pdf/value-card-deck.pdf via headless Chrome.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Chrome not found at: $CHROME" >&2; exit 1; }

SRC="output/html/value-card-deck.html"
OUT="output/pdf/value-card-deck.pdf"
[ -f "$SRC" ] || { echo "Missing $SRC — run scripts/build_value_cards.py first." >&2; exit 1; }

mkdir -p output/pdf
echo "  $SRC  ->  $OUT"
"$CHROME" \
  --headless=new \
  --disable-gpu \
  --no-sandbox \
  --no-pdf-header-footer \
  --print-to-pdf="$OUT" \
  --virtual-time-budget=2000 \
  "file://$ROOT/$SRC" \
  >/dev/null 2>&1

ls -lh "$OUT" | awk '{print "  " $9 "  " $5}'
