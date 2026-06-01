#!/usr/bin/env python3
"""Build printable empty-template framework headers + fellow name banners
for the VAP Implementation in-person workshop.

Source structure: the workshop's existing FigJam Implementation canvas
(Value Definition → Value Hierarchy Trees → Map Value Tensions →
Resolve Conflicts). Verbatim instructions are taken from that canvas;
all example/filled content is stripped — fellows fill in on Post-it
posters.

Outputs:
  output/html/framework-headers.html  +  output/pdf/framework-headers.pdf
    7 pages: 4 framework section headers + 3 conflict-resolution sub-column
    headers. Print 1 set per fellow (×10) or however many you need.

  output/html/fellow-banners.html  +  output/pdf/fellow-banners.pdf
    10 pages, one per fellow: huge name + host org, ready to tape to the
    top of their poster pair.

Letter portrait, 0.5" margins, sans-serif, brick-red brand accent. Designed
to read from across the workshop room.
"""

from __future__ import annotations
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_HTML = ROOT / "output" / "html"
OUT_HTML.mkdir(parents=True, exist_ok=True)


# ---- Data: 4 Implementation sections + 3 conflict-resolution columns ----

SECTIONS = [
    {
        "num": "1",
        "title": "Value Definition",
        "phase": "Card creation",
        "instruction": (
            "Define your top 3 values — abstract concepts — in "
            "operational terms."
        ),
        "subprompts": [
            ("ABSTRACT MEANING", "What does this value generally mean?"),
            ("OPERATIONAL DEFINITION",
             "How would you recognize this value in practice? What would it look like concretely?"),
            ("EXAMPLES", "Where in your project does it show up?"),
        ],
        "diagram": None,
    },
    {
        "num": "2",
        "title": "Value Hierarchy Trees",
        "phase": "Part 1 · 25 minutes",
        "instruction": (
            "Translate your 2–3 chosen and operationalized key values into "
            "norms and design requirements (after Van de Poel)."
        ),
        "subprompts": [],
        "diagram": "hierarchy",  # VALUE → NORM → REQUIREMENT
    },
    {
        "num": "3",
        "title": "Map Value Tensions",
        "phase": "Part 2a · 15 minutes",
        "instruction": (
            "Trace value tensions within your project. Focus on the most critical ones. "
            "Tensions can occur between values, but also between norms and requirements."
        ),
        "subprompts": [],
        "diagram": "tension",  # VALUE ↔ VALUE
    },
    {
        "num": "4",
        "title": "Resolve Conflicts",
        "phase": "Part 2b · 15 minutes",
        "instruction": (
            "Resolve traced conflicts by dissolving, compromising, or trading-off. "
            "As conflicts resolve, they become new design requirements."
        ),
        "subprompts": [
            ("\U0001F7E2 DISSOLVE",
             "Innovative design avoids the conflict entirely."),
            ("\U0001F7E1 COMPROMISE",
             "Both values are partially satisfied."),
            ("\U0001F534 TRADE-OFF",
             "Prioritize one value; note the consequence and any future mitigations."),
        ],
        "diagram": None,
    },
]

CONFLICT_COLUMNS = [
    {
        "marker": "\U0001F7E2",
        "title": "Dissolved",
        "subtitle": "Innovative design avoids the conflict",
        "fields": ["Value conflict", "Value outcome", "Dissolution solution"],
        "color": "#2f8d90",  # teal
        "tint": "#e3f0f0",
    },
    {
        "marker": "\U0001F7E1",
        "title": "Compromised",
        "subtitle": "Both values partially satisfied",
        "fields": ["Value conflict", "Value outcome", "Compromise solution"],
        "color": "#b6892f",  # mustard
        "tint": "#f7eecf",
    },
    {
        "marker": "\U0001F534",
        "title": "Trade-off",
        "subtitle": "Prioritize one value; document the consequence",
        "fields": ["Value conflict", "Value trade-off consequence", "Trade-off decision",
                   "Potential future mitigations"],
        "color": "#b75552",  # brick
        "tint": "#f3e6e4",
    },
]

# 10 fellows of the 2026 cohort (kept in sync with index.html).
FELLOWS = [
    ("Alaa", "Daffalla",       "Maimonides Medical Center"),
    ("Daniel", "Enriquez",      "Center for Family Support (CFS)"),
    ("Hal", "Triedman",            "NYC Mayor's Office of Contract Services"),
    ("Isabel", "Corpus",        "NYC Office of Technology & Innovation"),
    ("Jingruo", "Chen",         "NYC Department for the Aging"),
    ("Nanyi", "Jiang",          "National Women's Hall of Fame"),
    ("Suvadip", "Sana",         "NYC Council Data Team"),
    ("Tan", "Gemicioglu",       "Ability Beyond"),
    ("Tanvir", "Ahmed",         "Environmental Defense Fund — MethaneSAT"),
    ("Ulysse", "Hennebelle",    "New York Police Department"),
]


# ---- CSS shared across all pages -----------------------------------------

CSS = r"""
@page { size: letter portrait; margin: 0.5in; }

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
  width: 7.5in;
  height: 10in;
  page-break-after: always;
  position: relative;
  padding: 0;
  display: flex;
  flex-direction: column;
}
.page:last-child { page-break-after: auto; }

/* ---------- Framework section header ---------- */

.section-header { position: relative; height: 100%; display: flex; flex-direction: column; }

.section-num {
  position: absolute;
  top: -0.1in;
  right: 0;
  font-family: "Newsreader", Georgia, serif;
  font-size: 220pt;
  font-weight: 400;
  line-height: 0.85;
  color: var(--brick-tint);
  z-index: 0;
}

.section-eyebrow {
  font-size: 11pt;
  font-weight: 600;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  color: var(--brick);
  margin-bottom: 0.25in;
  z-index: 1;
}

.section-title {
  font-family: "Inter", -apple-system, "Helvetica Neue", Arial, sans-serif;
  font-size: 108pt;
  font-weight: 800;
  line-height: 0.94;
  letter-spacing: -0.025em;
  color: var(--ink);
  margin: 0 0 0.30in;
  z-index: 1;
}

.section-instruction {
  font-size: 22pt;
  font-weight: 400;
  line-height: 1.30;
  color: var(--ink);
  margin: 0 0 0.45in;
  max-width: 6.5in;
  z-index: 1;
}

.section-subprompts {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.20in;
  margin-top: auto;
  margin-bottom: 0;
  z-index: 1;
}
.section-subprompt {
  border-top: 1.5pt solid var(--ink);
  padding-top: 0.12in;
}
.section-subprompt .sp-label {
  font-size: 12pt;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink);
  margin-bottom: 0.06in;
  line-height: 1.15;
}
.section-subprompt .sp-help {
  font-size: 10.5pt;
  color: var(--ink-soft);
  line-height: 1.30;
}

.section-diagram {
  margin: 0.3in 0 0;
  z-index: 1;
}

/* ----- diagram-specific (hierarchy / tension) ----- */

.hierarchy {
  display: flex;
  flex-direction: column;
  gap: 0.18in;
  align-items: flex-start;
}
.hierarchy .level {
  display: flex;
  align-items: center;
  gap: 0.18in;
}
.hierarchy .chip {
  font-size: 14pt;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0.10in 0.22in;
  border-radius: 4pt;
}
.hierarchy .v   { background: #e3f0f0; color: var(--teal); }
.hierarchy .n   { background: #faf2c8; color: #786420; }
.hierarchy .r   { background: #faf2c8; color: #786420; }
.hierarchy .arrow {
  font-size: 14pt; color: var(--ink-soft); font-weight: 700;
}

.tension {
  display: flex;
  align-items: center;
  gap: 0.30in;
  font-size: 14pt;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.tension .v {
  background: #e3f0f0;
  color: var(--teal);
  padding: 0.10in 0.22in;
  border-radius: 4pt;
}
.tension .vs {
  color: var(--brick);
  font-size: 22pt;
}

/* ---------- Conflict resolution sub-column header ---------- */

.conflict-page { display: flex; flex-direction: column; height: 100%; }

.conflict-marker {
  font-size: 90pt;
  line-height: 1;
  margin-bottom: 0.20in;
}
.conflict-eyebrow {
  font-size: 12pt;
  font-weight: 600;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  margin-bottom: 0.12in;
}
.conflict-title {
  font-size: 76pt;
  font-weight: 800;
  line-height: 0.94;
  letter-spacing: -0.030em;
  margin: 0 0 0.20in;
}
.conflict-subtitle {
  font-size: 22pt;
  font-weight: 400;
  line-height: 1.30;
  color: var(--ink-soft);
  margin: 0 0 0.45in;
  max-width: 6.5in;
}
.conflict-fields {
  display: flex;
  flex-direction: column;
  gap: 0.20in;
  margin-top: auto;
}
.conflict-field {
  border-top: 1.5pt solid var(--line);
  padding-top: 0.10in;
  font-size: 18pt;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--ink);
}

/* ---------- Fellow name banner ---------- */

.banner {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.banner-eyebrow {
  font-size: 12pt;
  font-weight: 600;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  color: var(--brick);
  margin-bottom: 0.20in;
}
.banner-name {
  font-size: 84pt;
  font-weight: 800;
  line-height: 0.96;
  letter-spacing: -0.030em;
  color: var(--ink);
  margin: 0;
}
.banner-name .first { display: block; }
.banner-name .last  { display: block; color: var(--brick); }
.banner-org {
  margin-top: 0.45in;
  font-size: 28pt;
  font-weight: 500;
  line-height: 1.20;
  color: var(--ink);
  max-width: 6.5in;
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
    width: 8.5in;
    height: 11in;
    padding: 0.5in;
  }
}
"""


# ---- HTML builders -------------------------------------------------------

def hierarchy_diagram_html() -> str:
    return """
    <div class="section-diagram">
      <div class="hierarchy">
        <div class="level"><span class="chip v">Value</span></div>
        <div class="level"><span class="arrow">↳</span>
                           <span class="chip n">Norm</span>
                           <span class="arrow">·</span>
                           <span class="chip n">Norm</span></div>
        <div class="level"><span class="arrow" style="margin-left:0.4in">↳</span>
                           <span class="chip r">Requirement</span>
                           <span class="arrow">·</span>
                           <span class="chip r">Requirement</span></div>
      </div>
    </div>
    """


def tension_diagram_html() -> str:
    return """
    <div class="section-diagram">
      <div class="tension">
        <span class="v">Value A</span>
        <span class="vs">↔</span>
        <span class="v">Value B</span>
      </div>
    </div>
    """


def section_page(section: dict) -> str:
    eyebrow = html.escape(section["phase"])
    title = html.escape(section["title"]).replace(" ", "<br>")
    instruction = html.escape(section["instruction"])

    diagram = ""
    if section.get("diagram") == "hierarchy":
        diagram = hierarchy_diagram_html()
    elif section.get("diagram") == "tension":
        diagram = tension_diagram_html()

    subs = ""
    if section.get("subprompts"):
        items = "\n".join(
            f'<div class="section-subprompt">'
            f'  <div class="sp-label">{html.escape(lbl)}</div>'
            f'  <div class="sp-help">{html.escape(help_)}</div>'
            f"</div>"
            for (lbl, help_) in section["subprompts"]
        )
        subs = f'<div class="section-subprompts">{items}</div>'

    return f"""
    <section class="page">
      <div class="section-header">
        <div class="section-num">{html.escape(section['num'])}</div>
        <div class="section-eyebrow">{eyebrow}</div>
        <h1 class="section-title">{title}</h1>
        <p class="section-instruction">{instruction}</p>
        {diagram}
        {subs}
      </div>
    </section>
    """


def conflict_page(column: dict) -> str:
    fields = "\n".join(
        f'<div class="conflict-field">{html.escape(f)}</div>'
        for f in column["fields"]
    )
    return f"""
    <section class="page">
      <div class="conflict-page" style="border-top: 6pt solid {column['color']};
                                       padding-top: 0.25in;">
        <div class="conflict-marker">{column['marker']}</div>
        <div class="conflict-eyebrow" style="color: {column['color']};">
          Resolve conflicts
        </div>
        <h1 class="conflict-title" style="color: {column['color']};">
          {html.escape(column['title'])}
        </h1>
        <p class="conflict-subtitle">{html.escape(column['subtitle'])}</p>
        <div class="conflict-fields">{fields}</div>
      </div>
    </section>
    """


def banner_page(first: str, last: str, org: str) -> str:
    return f"""
    <section class="page">
      <div class="banner">
        <div class="banner-eyebrow">VAP · Implementation · Summer 2026</div>
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
    # framework-headers.pdf: 4 section headers + 3 conflict columns = 7 pages
    fh_pages = [section_page(s) for s in SECTIONS] + [
        conflict_page(c) for c in CONFLICT_COLUMNS
    ]
    (OUT_HTML / "framework-headers.html").write_text(
        wrap("VAP Implementation — framework headers", "\n".join(fh_pages)),
        encoding="utf-8",
    )

    # fellow-banners.pdf: 10 fellow name banners
    fb_pages = [banner_page(first, last, org) for (first, last, org) in FELLOWS]
    (OUT_HTML / "fellow-banners.html").write_text(
        wrap("VAP — fellow banners", "\n".join(fb_pages)),
        encoding="utf-8",
    )

    print(f"Wrote {len(fh_pages)} pages -> output/html/framework-headers.html")
    print(f"Wrote {len(fb_pages)} pages -> output/html/fellow-banners.html")


if __name__ == "__main__":
    main()
