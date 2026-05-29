#!/usr/bin/env python3
"""Build one HTML packet per fellow from context/snippets/_all.json.

Each packet is paginated as 6 snippet cards per page (2-col × 3-row grid)
with a running fellow/org header. Output goes to output/html/; convert to
PDF afterwards with scripts/build_pdfs.sh (headless Chrome).
"""

from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALL_JSON = ROOT / "context" / "snippets" / "_all.json"
HTML_OUT = ROOT / "output" / "html"
HTML_OUT.mkdir(parents=True, exist_ok=True)

CARDS_PER_PAGE = 6
HEURISTIC_ORDER = ["functional", "stakeholders", "constraints", "societal"]

CSS = r"""
@page { size: letter portrait; margin: 0.5in; }

* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body {
  margin: 0; padding: 0;
  font-family: -apple-system, "Helvetica Neue", "Segoe UI", Arial, sans-serif;
  color: #221c1b;
}

.page {
  width: 7.5in;          /* 8.5 - 1.0 in horizontal margin */
  height: 10in;          /* 11  - 1.0 in vertical margin   */
  page-break-after: always;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.page:last-child { page-break-after: auto; }

.fellow-header {
  height: 0.7in;
  border-bottom: 1pt solid #b75552;
  padding-bottom: 0.10in;
  margin-bottom: 0.18in;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex: 0 0 auto;
}
.fellow-header .left .name {
  font-family: Georgia, "Iowan Old Style", "Palatino Linotype", serif;
  font-size: 16pt;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #221c1b;
  line-height: 1.05;
}
.fellow-header .left .org {
  font-size: 10.5pt;
  color: #5d5450;
  margin-top: 0.04in;
}
.fellow-header .right { text-align: right; }
.fellow-header .right .pagenum {
  font-size: 8pt;
  color: #8a8076;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.fellow-header .right .packet-tag {
  font-size: 7pt;
  color: #b75552;
  letter-spacing: 0.10em;
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 0.04in;
}

.cards-grid {
  flex: 1 1 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: repeat(3, 1fr);
  gap: 0.16in;
  min-height: 0;
}

.card {
  border: 0.75pt solid #b5aea8;
  border-radius: 4pt;
  padding: 0.14in 0.16in 0.12in;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
  break-inside: avoid;
}
.card .category {
  font-size: 7.5pt;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #b75552;
  margin-bottom: 0.06in;
  padding-bottom: 0.05in;
  border-bottom: 0.5pt solid #f3e6e4;
  flex: 0 0 auto;
}
.card .body {
  flex: 1 1 auto;
  font-size: 9.5pt;
  line-height: 1.32;
  color: #2a2422;
  overflow: hidden;
}
.card .body p { margin: 0 0 0.06in; }
.card .body p:last-child { margin-bottom: 0; }
.card .body ul {
  margin: 0;
  padding-left: 0.18in;
}
.card .body li { margin-bottom: 0.04in; }

.card .attrib {
  flex: 0 0 auto;
  margin-top: 0.08in;
  padding-top: 0.06in;
  border-top: 0.5pt dotted #cfcac4;
  font-size: 6.5pt;
  color: #8a8076;
  line-height: 1.3;
  word-break: break-word;
}
.card .v {
  /* tiny verbatim marker — not self-explanatory, just for Hauke */
  color: #2f8d90;
  font-weight: 700;
  margin-right: 0.05in;
}

/* font-size buckets based on body length */
.card.size-m .body { font-size: 9pt;  line-height: 1.30; }
.card.size-s .body { font-size: 8pt;  line-height: 1.28; }
.card.size-xs .body { font-size: 7pt; line-height: 1.26; }

/* On-screen preview (ignored when printing) */
@media screen {
  body { background: #e6e2dd; padding: 0.4in 0; }
  .page {
    background: #fff;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12);
    margin: 0 auto 0.4in;
    padding: 0.5in;          /* draw the page margin on-screen */
    width: 8.5in;
    height: 11in;
  }
}
"""


def size_class(body: str) -> str:
    n = len(body)
    if n >= 700:
        return "card size-xs"
    if n >= 500:
        return "card size-s"
    if n >= 320:
        return "card size-m"
    return "card"


def fmt_body(body: str) -> str:
    escaped = html.escape(body)
    paras = [p.strip() for p in escaped.split("\n\n") if p.strip()]
    if not paras:
        paras = [escaped]
    return "".join(f"<p>{p.replace(chr(10), '<br>')}</p>" for p in paras)


def card_html(snippet: dict) -> str:
    score = snippet.get("verify_score")
    mark = '<span class="v">✓</span>' if (isinstance(score, (int, float)) and score >= 0.95) else ""
    return (
        f'<div class="{size_class(snippet["body"])}">'
        f'  <div class="category">{html.escape(snippet["category"])}</div>'
        f'  <div class="body">{fmt_body(snippet["body"])}</div>'
        f'  <div class="attrib">{mark}{html.escape(snippet["attribution"])}</div>'
        f"</div>"
    )


def build_fellow(fellow_key: str, data: dict) -> str:
    snippets = sorted(
        data["snippets"], key=lambda s: HEURISTIC_ORDER.index(s["heuristic"])
    )
    n_pages = (len(snippets) + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE

    pages_html = []
    for i in range(n_pages):
        chunk = snippets[i * CARDS_PER_PAGE : (i + 1) * CARDS_PER_PAGE]
        cards = "\n".join(card_html(s) for s in chunk)
        pages_html.append(
            f'<section class="page">'
            f'  <header class="fellow-header">'
            f'    <div class="left">'
            f'      <div class="name">{html.escape(data["fellow"])}</div>'
            f'      <div class="org">{html.escape(data["org_full"])}</div>'
            f"    </div>"
            f'    <div class="right">'
            f'      <div class="packet-tag">VAP &middot; Discovery</div>'
            f'      <div class="pagenum">Page {i+1} of {n_pages}</div>'
            f"    </div>"
            f"  </header>"
            f'  <div class="cards-grid">{cards}</div>'
            f"</section>"
        )

    body = "\n".join(pages_html)
    return (
        '<!DOCTYPE html>\n'
        '<html lang="en"><head><meta charset="utf-8">'
        f'<title>{html.escape(data["fellow"])} — VAP Discovery Packet</title>'
        f"<style>{CSS}</style></head><body>{body}</body></html>\n"
    )


def main() -> None:
    with open(ALL_JSON) as f:
        combined = json.load(f)

    print(f"Building packets for {len(combined)} fellows from {ALL_JSON.name}")
    for key in sorted(combined):
        data = combined[key]
        html_doc = build_fellow(key, data)
        org_short = data["org_short"].lower().replace(" ", "-")
        out_path = HTML_OUT / f"{key}_{org_short}.html"
        out_path.write_text(html_doc, encoding="utf-8")
        n = len(data["snippets"])
        n_pages = (n + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE
        print(f"  {key:<12} {n:>2} snippets / {n_pages} page(s) -> {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
