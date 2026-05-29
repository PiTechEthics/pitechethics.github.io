#!/usr/bin/env python3
"""Build the shared Value Card Deck for the VAP Discovery workshop.

86 value cards + 30 blank cards = 116 cards across 10 color-coded groups,
10 cards per letter page (2 cols × 5 rows) = 12 pages.

Writes output/html/value-card-deck.html. Convert to PDF afterwards with
scripts/build_value_cards_pdf.sh (headless Chrome).

Spec: context/value-card-deck-prep.md
"""

from __future__ import annotations
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_HTML = ROOT / "output" / "html"
OUT_HTML.mkdir(parents=True, exist_ok=True)

CARDS_PER_PAGE = 10  # 2 cols × 5 rows
BLANKS_PER_GROUP = 3

GROUPS = [
    {"id": "care",        "name": "Care & Solidarity",            "color": "#F5C95D",
     "values": ["Care", "Compassion", "Empathy", "Kindness", "Generosity",
                "Cooperation", "Solidarity", "Community", "Sympathy", "Hospitality"]},
    {"id": "justice",     "name": "Justice & Inclusion",          "color": "#7DB46C",
     "values": ["Justice", "Fairness", "Equality", "Equity", "Inclusion",
                "Diversity", "Accessibility", "Tolerance", "Egalitarianism", "Non-discrimination"]},
    {"id": "autonomy",    "name": "Autonomy & Agency",            "color": "#5B8DBF",
     "values": ["Autonomy", "Freedom", "Liberty", "Independence", "Self-determination",
                "Empowerment", "Choice", "Self-direction", "Voice"]},
    {"id": "dignity",     "name": "Privacy, Dignity & Respect",   "color": "#9B6BB0",
     "values": ["Privacy", "Dignity", "Respect", "Consent", "Anonymity",
                "Confidentiality", "Honor", "Recognition"]},
    {"id": "trust",       "name": "Trust & Integrity",            "color": "#C76B98",
     "values": ["Honesty", "Transparency", "Trust", "Accountability", "Integrity",
                "Authenticity", "Truthfulness", "Responsibility"]},
    {"id": "safety",      "name": "Safety & Wellbeing",           "color": "#E08672",
     "values": ["Safety", "Security", "Health", "Wellbeing", "Peace",
                "Stability", "Resilience", "Comfort"]},
    {"id": "quality",     "name": "Quality & Effectiveness",      "color": "#8B95A3",
     "values": ["Efficiency", "Accuracy", "Reliability", "Usability", "Robustness",
                "Scalability", "Mastery", "Performance"]},
    {"id": "creativity",  "name": "Creativity & Stimulation",     "color": "#5BAFA8",
     "values": ["Creativity", "Innovation", "Curiosity", "Playfulness", "Humor",
                "Beauty", "Imagination", "Style", "Pleasure"]},
    {"id": "stewardship", "name": "Stewardship & Sustainability", "color": "#4A7C59",
     "values": ["Sustainability", "Environmentalism", "Stewardship",
                "Future generations", "Conservation", "Long-term thinking"]},
    {"id": "tradition",   "name": "Tradition, Power & Status",    "color": "#A0764F",
     "values": ["Tradition", "Heritage", "Loyalty", "Belonging", "Conformity",
                "Achievement", "Status", "Power", "Wealth", "Prestige"]},
]


def tint(hex_color: str, mix: float = 0.28) -> str:
    """Blend hex color with white. mix=0.28 → 28% color, 72% white (light tint)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = round(255 - (255 - r) * mix)
    g = round(255 - (255 - g) * mix)
    b = round(255 - (255 - b) * mix)
    return f"rgb({r},{g},{b})"


def size_class(value: str) -> str:
    """Bucket the value-word font size based on character length."""
    n = len(value)
    if n >= 17:
        return " size-xs"
    if n >= 13:
        return " size-s"
    if n >= 10:
        return " size-m"
    return ""


# Build flat card list group-by-group: values then blanks for each group
cards: list[dict] = []
for g in GROUPS:
    for v in g["values"]:
        cards.append({"group": g, "value": v, "blank": False})
    for _ in range(BLANKS_PER_GROUP):
        cards.append({"group": g, "value": None, "blank": True})

n_pages = (len(cards) + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE


def group_css() -> str:
    rules = []
    for g in GROUPS:
        rules.append(f".g-{g['id']} {{ background: {tint(g['color'])}; }}")
    return "\n".join(rules)


CSS = """
@page { size: letter portrait; margin: 0.5in; }

* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body {
  margin: 0; padding: 0;
  font-family: "Inter", -apple-system, "Helvetica Neue", Arial, sans-serif;
  color: #181615;
}

.page {
  width: 7.5in;
  height: 10in;
  page-break-after: always;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: repeat(5, 1fr);
  gap: 0.10in;
}
.page:last-child { page-break-after: auto; }

.card {
  border: 0.75pt solid #9c948e;
  border-radius: 4pt;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0.16in 0.30in 0.18in;
  text-align: center;
  break-inside: avoid;
  overflow: hidden;
}

.card .value {
  font-size: 32pt;
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -0.015em;
  color: #181615;
  word-break: break-word;
  hyphens: auto;
}
.card.size-m .value { font-size: 26pt; }
.card.size-s .value { font-size: 22pt; }
.card.size-xs .value { font-size: 18pt; line-height: 1.10; }

.card .group {
  margin-top: 0.10in;
  font-size: 7pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(0,0,0,0.50);
  line-height: 1.1;
}

/* Blank-card variant: replace value with a guide line for hand-writing */
.card.blank .value-line {
  width: 2.6in;
  height: 0;
  border-bottom: 0.5pt solid #1a1a1a;
  margin-bottom: 0.05in;
}

__GROUP_COLORS__

/* On-screen preview */
@media screen {
  body { background: #e6e2dd; padding: 0.4in 0; }
  .page {
    background: #fff;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12);
    margin: 0 auto 0.4in;
    width: 8.5in;
    height: 11in;
    padding: 0.5in;
  }
}
"""


def card_html(c: dict) -> str:
    g = c["group"]
    if c["blank"]:
        body = '<div class="value-line"></div>'
    else:
        body = f'<div class="value">{html.escape(c["value"])}</div>'
    klass = f"card g-{g['id']}"
    if c["blank"]:
        klass += " blank"
    else:
        klass += size_class(c["value"])
    return f'<div class="{klass}">{body}<div class="group">{html.escape(g["name"])}</div></div>'


def main() -> None:
    pages_html: list[str] = []
    for i in range(n_pages):
        chunk = cards[i * CARDS_PER_PAGE : (i + 1) * CARDS_PER_PAGE]
        cards_inner = "\n".join(card_html(c) for c in chunk)
        pages_html.append(f'<section class="page">{cards_inner}</section>')

    style = CSS.replace("__GROUP_COLORS__", group_css())
    doc = (
        '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
        '<title>VAP Value Card Deck</title>'
        f'<style>{style}</style></head><body>{chr(10).join(pages_html)}</body></html>\n'
    )
    out = OUT_HTML / "value-card-deck.html"
    out.write_text(doc, encoding="utf-8")

    n_values = sum(len(g["values"]) for g in GROUPS)
    n_blanks = len(GROUPS) * BLANKS_PER_GROUP
    print(f"Wrote {out.relative_to(ROOT)}")
    print(f"  {len(cards)} cards = {n_values} values + {n_blanks} blanks across {len(GROUPS)} groups")
    print(f"  {n_pages} pages at {CARDS_PER_PAGE} cards/page")
    # Flag values that dropped below 24pt
    small = [v for g in GROUPS for v in g["values"] if size_class(v).strip() in ("size-s", "size-xs")]
    if small:
        print(f"  values below 24pt due to word length: {small}")


if __name__ == "__main__":
    main()
