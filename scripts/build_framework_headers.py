#!/usr/bin/env python3
"""Build printable empty-template framework headers + fellow name banners
for the VAP **Discovery** in-person workshop.

Discovery has 4 heuristics (Functional Description, Key Actors & Stakeholders,
Technical & Material Constraints, Societal Context) with 18 sub-categories
total. The same structure that organizes each fellow's snippet packet — these
headers go on the workshop posters so fellows can sort their snippets +
value-word stickies underneath the right heuristic.

Format: **letter LANDSCAPE**. The header occupies the top half of each page;
the bottom half is intentionally white so you can cut along the dashed line
and keep only the header strip.

Outputs:
  output/html/framework-headers.html  +  output/pdf/framework-headers.pdf
    4 heuristic headers (one per page). Print 1 set per fellow (×10) or share.

  output/html/fellow-banners.html  +  output/pdf/fellow-banners.pdf
    10 pages, one per fellow: huge name + host org.
"""

from __future__ import annotations
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_HTML = ROOT / "output" / "html"
OUT_HTML.mkdir(parents=True, exist_ok=True)


# ---- Discovery heuristics + sub-categories -------------------------------
# Sub-category names match the snippet packets' category labels exactly,
# so fellows can carry the same vocabulary from snippet card to poster.

HEURISTICS = [
    {
        "num": "1",
        "title": "Functional",
        "title_line2": "Description",
        "tagline": "What does the org and its product do — and care about?",
        "subcats": [
            "Mission Statement",
            "Problems Solved",
            "Stated Goals",
        ],
    },
    {
        "num": "2",
        "title": "Key Actors",
        "title_line2": "& Stakeholders",
        "tagline": "Whose values shape this technology?",
        "subcats": [
            "Target Audience",
            "Users / Beneficiaries",
            "Founders",
            "Funders / Investors",
            "Affected Communities",
            "Employees / Creators",
            "Partners",
        ],
    },
    {
        "num": "3",
        "title": "Technical &",
        "title_line2": "Material Constraints",
        "tagline": "What values does the tech itself carry in?",
        "subcats": [
            "Platform Limitations",
            "Data Requirements",
            "Infrastructure Requirements",
            "Resource Constraints",
        ],
    },
    {
        "num": "4",
        "title": "Societal",
        "title_line2": "Context",
        "tagline": "What does the world around it carry in?",
        "subcats": [
            "Legal & Compliance Landscape",
            "Cultural Norms",
            "Industry Standards",
            "Geographic Context",
        ],
    },
]


# 10 fellows of the 2026 cohort (kept in sync with index.html).
FELLOWS = [
    ("Alaa",     "Daffalla",    "Maimonides Medical Center"),
    ("Daniel",   "Enriquez",    "Center for Family Support (CFS)"),
    ("Hal",      "Triedman",    "NYC Mayor's Office of Contract Services"),
    ("Isabel",   "Corpus",      "NYC Office of Technology & Innovation"),
    ("Jingruo",  "Chen",        "NYC Department for the Aging"),
    ("Nanyi",    "Jiang",       "National Women's Hall of Fame"),
    ("Suvadip",  "Sana",        "NYC Council Data Team"),
    ("Tan",      "Gemicioglu",  "Ability Beyond"),
    ("Tanvir",   "Ahmed",       "Environmental Defense Fund — MethaneSAT"),
    ("Ulysse",   "Hennebelle",  "New York Police Department"),
]


CSS = r"""
@page { size: letter landscape; margin: 0.5in; }

* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }

:root {
  --ink:        #221c1b;
  --ink-soft:   #5d5450;
  --paper:      #faf6f2;
  --brick:      #b75552;
  --brick-dark: #8f2d2a;
  --brick-tint: #f3e6e4;
  --teal:       #2f8d90;
  --line:       #1a1413;
}

html, body {
  margin: 0; padding: 0;
  font-family: "Inter", -apple-system, "Helvetica Neue", Arial, sans-serif;
  color: var(--ink);
  background: #fff;
}

.page {
  /* landscape letter, 0.5" margin → 10" × 7.5" interior */
  width: 10in;
  height: 7.5in;
  page-break-after: always;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.page:last-child { page-break-after: auto; }

/* ---------- Discovery heuristic header (landscape) ---------- */

.heuristic {
  /* takes the top half of the page; bottom half is intentionally blank */
  height: 4.4in;
  display: flex;
  flex-direction: column;
  position: relative;
}

.h-num {
  position: absolute;
  top: -0.15in;
  right: 0;
  font-family: "Newsreader", Georgia, serif;
  font-size: 230pt;
  font-weight: 400;
  line-height: 0.85;
  color: var(--brick-tint);
  z-index: 0;
}

.h-eyebrow {
  font-size: 11pt;
  font-weight: 600;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  color: var(--brick);
  margin-bottom: 0.18in;
  z-index: 1;
  position: relative;
}

.h-title {
  font-size: 84pt;
  font-weight: 800;
  line-height: 0.96;
  letter-spacing: -0.030em;
  margin: 0 0 0.20in;
  color: var(--ink);
  z-index: 1;
  position: relative;
}
.h-title .l2 { display: block; color: var(--brick); }

.h-tagline {
  font-size: 22pt;
  font-weight: 400;
  line-height: 1.25;
  color: var(--ink);
  margin: 0 0 0.20in;
  max-width: 8.5in;
  z-index: 1;
  position: relative;
}

.h-subcats {
  margin-top: auto;
  display: flex;
  flex-wrap: wrap;
  gap: 0.16in 0.30in;
  align-items: baseline;
  z-index: 1;
  position: relative;
}
.h-subcats .item {
  font-size: 13pt;
  font-weight: 700;
  letter-spacing: 0.10em;
  text-transform: uppercase;
  color: var(--ink);
  padding-bottom: 0.06in;
  border-bottom: 1.5pt solid var(--ink);
}

/* cut line + white space below */
.cutline {
  margin-top: 0.50in;
  height: 0;
  border-top: 1pt dashed #a8a8a8;
  position: relative;
}
.cutline::after {
  content: "✂ cut here";
  position: absolute;
  top: -0.13in;
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  padding: 0 0.10in;
  font-size: 8pt;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #a8a8a8;
}

.below-cut {
  flex: 1;
  /* intentionally empty white space for cutting */
}

/* ---------- Fellow name banner (landscape) ---------- */

.banner {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}
.banner-eyebrow {
  font-size: 12pt;
  font-weight: 600;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  color: var(--brick);
  margin-bottom: 0.30in;
}
.banner-name {
  font-size: 132pt;
  font-weight: 800;
  line-height: 0.94;
  letter-spacing: -0.030em;
  color: var(--ink);
  margin: 0;
}
.banner-name .first { display: block; }
.banner-name .last  { display: block; color: var(--brick); }
.banner-org {
  margin-top: 0.40in;
  font-size: 30pt;
  font-weight: 500;
  line-height: 1.20;
  color: var(--ink);
  max-width: 9in;
}
.banner-footer {
  margin-top: auto;
  border-top: 1pt solid var(--ink);
  padding-top: 0.12in;
  font-size: 10pt;
  font-weight: 600;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  color: var(--ink-soft);
  display: flex;
  justify-content: space-between;
}

/* On-screen preview */
@media screen {
  body { background: #e6e2dd; padding: 0.4in 0; }
  .page {
    background: #fff;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12);
    margin: 0 auto 0.4in;
    width: 11in;
    height: 8.5in;
    padding: 0.5in;
  }
}
"""


def heuristic_page(h: dict) -> str:
    subcats = "\n".join(
        f'<span class="item">{html.escape(s)}</span>' for s in h["subcats"]
    )
    return f"""
    <section class="page">
      <div class="heuristic">
        <div class="h-num">{html.escape(h['num'])}</div>
        <div class="h-eyebrow">Discovery · Heuristic {html.escape(h['num'])} of 4</div>
        <h1 class="h-title">
          {html.escape(h['title'])}<span class="l2">{html.escape(h['title_line2'])}</span>
        </h1>
        <p class="h-tagline">{html.escape(h['tagline'])}</p>
        <div class="h-subcats">{subcats}</div>
      </div>
      <div class="cutline"></div>
      <div class="below-cut"></div>
    </section>
    """


def banner_page(first: str, last: str, org: str) -> str:
    return f"""
    <section class="page">
      <div class="banner">
        <div class="banner-eyebrow">VAP · Discovery · Summer 2026</div>
        <div class="banner-name">
          <span class="first">{html.escape(first)}</span>
          <span class="last">{html.escape(last)}</span>
        </div>
        <div class="banner-org">{html.escape(org)}</div>
        <div class="banner-footer">
          <span>PiTech × DLI</span>
          <span>Cornell Tech · NYC</span>
        </div>
      </div>
    </section>
    """


def wrap(title: str, body: str) -> str:
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        f'<title>{html.escape(title)}</title>'
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Newsreader:opsz@6..72&display=swap" rel="stylesheet">'
        f'<style>{CSS}</style></head><body>{body}</body></html>'
    )


def main() -> None:
    fh_pages = [heuristic_page(h) for h in HEURISTICS]
    (OUT_HTML / "framework-headers.html").write_text(
        wrap("VAP Discovery — framework headers", "\n".join(fh_pages)),
        encoding="utf-8",
    )

    fb_pages = [banner_page(first, last, org) for (first, last, org) in FELLOWS]
    (OUT_HTML / "fellow-banners.html").write_text(
        wrap("VAP — fellow banners", "\n".join(fb_pages)),
        encoding="utf-8",
    )

    print(f"Wrote {len(fh_pages)} pages -> output/html/framework-headers.html")
    print(f"Wrote {len(fb_pages)} pages -> output/html/fellow-banners.html")


if __name__ == "__main__":
    main()
