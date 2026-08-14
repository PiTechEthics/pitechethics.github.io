#!/usr/bin/env python3
"""Build the 5-minute final-presentation slide template for the 2026 PiTech
fellows (DLI Conscientious Tech Design Workshop).

The deck is a *template*: 4 front-matter slides explaining the ask, then a
7-slide section per fellow with name + host org already filled in. Everything
else is placeholder text the fellow overwrites.

Design constraints:
  - 16:9, built for upload to Google Slides (File > Import slides / Upload).
  - Plain text boxes and rectangles only — no groups, no masters, no SmartArt —
    so every element stays directly editable after the Slides conversion.
  - Arial + Georgia only. Both are guaranteed present in Google Slides, so
    nothing silently reflows on import.

Output: output/pptx/2026-VAP-Fellow-Final-Presentation-Template.pptx
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "pptx"
OUT.mkdir(parents=True, exist_ok=True)

# ---- palette (same ink/brick/teal family as the printed workshop material) --

INK        = RGBColor(0x22, 0x1C, 0x1B)
INK_SOFT   = RGBColor(0x5D, 0x54, 0x50)
MUTED      = RGBColor(0x9A, 0x91, 0x8C)   # placeholder prose
BRICK      = RGBColor(0xB7, 0x55, 0x52)
BRICK_DARK = RGBColor(0x8F, 0x2D, 0x2A)
BRICK_TINT = RGBColor(0xF3, 0xE6, 0xE4)
TEAL       = RGBColor(0x2F, 0x8D, 0x90)
TEAL_TINT  = RGBColor(0xE1, 0xEF, 0xEF)
BRONZE     = RGBColor(0xA0, 0x76, 0x4F)
BRONZE_TINT= RGBColor(0xF2, 0xEA, 0xE2)
PAPER      = RGBColor(0xFA, 0xF6, 0xF2)
LINE       = RGBColor(0xD8, 0xD0, 0xCA)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)

SANS  = "Arial"
SERIF = "Georgia"

# ---- geometry ---------------------------------------------------------------

SW, SH = 13.333, 7.5           # slide, inches
M      = 0.62                  # side margin
CW     = SW - 2 * M            # content width
FOOT_Y = 6.86                  # footer baseline


# ---- 2026 cohort ------------------------------------------------------------
# (first+last, host org as it appears on the PiTech site / index.html)

FELLOWS = [
    ("Alaa Daffalla",     "Maimonides Medical Center",              "Maimonides"),
    ("Daniel Enriquez",   "Center for Family Support",              "CFS"),
    ("Hal Triedman",      "NYC Mayor's Office of Contract Services", "MOCS"),
    ("Isabel Corpus",     "NYC Office of Technology & Innovation",  "NYC OTI"),
    ("Jingruo Chen",      "NYC Department for the Aging",           "NYC Aging"),
    ("Nanyi Jiang",       "National Women's Hall of Fame",          "NWHF"),
    ("Suvadip Sana",      "NYC Council Data Team",                  "NYC Council"),
    ("Tan Gemicioglu",    "Ability Beyond",                         "Ability Beyond"),
    ("Tanvir Ahmed",      "Environmental Defense Fund — MethaneSAT", "MethaneSAT"),
    ("Ulysse Hennebelle", "New York Police Department",             "NYPD"),
]


# ---- primitives -------------------------------------------------------------

def rect(slide, x, y, w, h, fill=None, line=None, lw=0.75, dash=False,
         shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.shadow.inherit = False
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
        if dash:
            # python-pptx has no dash enum on LineFormat in all versions; set XML
            from pptx.oxml.ns import qn
            ln = s.line._get_or_add_ln()
            d = ln.makeelement(qn("a:prstDash"), {"val": "dash"})
            ln.append(d)
    s.text_frame.text = ""
    return s


def text(slide, x, y, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         wrap=True):
    """runs: list of dicts {t, size, bold, italic, color, font, space_after,
    space_before, line}. Each dict is one paragraph."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    for i, r in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = r.get("align", align)
        if r.get("space_after"):
            p.space_after = Pt(r["space_after"])
        if r.get("space_before"):
            p.space_before = Pt(r["space_before"])
        if r.get("line"):
            p.line_spacing = r["line"]
        run = p.add_run()
        run.text = r["t"]
        f = run.font
        f.size = Pt(r.get("size", 14))
        f.bold = r.get("bold", False)
        f.italic = r.get("italic", False)
        f.color.rgb = r.get("color", INK)
        f.name = r.get("font", SANS)
    return box


def eyebrow(t, color=BRICK, size=10.5):
    return {"t": t.upper(), "size": size, "bold": True, "color": color,
            "font": SANS}


def prompt(t, size=11):
    """The question we are asking the fellow."""
    return {"t": t, "size": size, "bold": True, "color": INK, "font": SANS}


def fill_in(t, size=12, space_after=0):
    """Grey placeholder prose the fellow overwrites."""
    return {"t": t, "size": size, "italic": True, "color": MUTED, "font": SANS,
            "space_after": space_after, "line": 1.18}


def rule(slide, x, y, w, color=LINE, weight=0.75):
    ln = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                                Inches(w), Emu(int(weight * 12700)))
    ln.shadow.inherit = False
    ln.fill.solid()
    ln.fill.fore_color.rgb = color
    ln.line.fill.background()
    return ln


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def footer(slide, fellow, org, n, total, timing):
    rule(slide, M, FOOT_Y - 0.16, CW)
    text(slide, M, FOOT_Y, CW * 0.6, 0.28, [
        {"t": f"{fellow}  ·  {org}", "size": 9, "color": MUTED, "font": SANS},
    ])
    text(slide, M + CW * 0.6, FOOT_Y, CW * 0.4, 0.28, [
        {"t": f"{n} of {total}  ·  aim for {timing}", "size": 9,
         "color": MUTED, "font": SANS, "align": PP_ALIGN.RIGHT},
    ])


def slide_title(slide, kicker, title, sub=None):
    """Returns the y at which slide content may start.

    The title box grows to two lines past ~50 characters, so the subtitle and
    the content below it move down with it. Keeps the layout intact if these
    strings get edited later.
    """
    y = 0.52
    text(slide, M, y, CW, 0.24, [eyebrow(kicker)])
    n_lines = 1 if len(title) <= 50 else 2
    th = 0.50 * n_lines
    text(slide, M, y + 0.28, CW, th + 0.12, [
        {"t": title, "size": 30, "bold": True, "color": INK, "font": SERIF,
         "line": 1.05},
    ])
    if sub:
        sy = y + 0.30 + th + 0.08
        text(slide, M, sy, CW, 0.34, [
            {"t": sub, "size": 12, "color": INK_SOFT, "font": SANS, "line": 1.2},
        ])
        return sy + 0.52
    return y + 0.30 + th + 0.20


def notes(slide, body):
    slide.notes_slide.notes_text_frame.text = body


def image_drop(slide, x, y, w, h, caption):
    """A dashed box the fellow deletes and replaces with a pasted image."""
    rect(slide, x, y, w, h, fill=PAPER, line=BRICK, lw=1.0, dash=True)
    text(slide, x + 0.3, y + h / 2 - 0.42, w - 0.6, 0.84, [
        {"t": "PASTE YOUR IMAGE HERE", "size": 12, "bold": True,
         "color": BRICK, "font": SANS, "align": PP_ALIGN.CENTER,
         "space_after": 5},
        {"t": caption, "size": 10, "italic": True, "color": MUTED,
         "font": SANS, "align": PP_ALIGN.CENTER, "line": 1.2},
    ], anchor=MSO_ANCHOR.MIDDLE)


def chip(slide, x, y, w, h, label, fill, fg):
    rect(slide, x, y, w, h, fill=fill, line=None,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(slide, x, y, w, h, [
        {"t": label.upper(), "size": 9.5, "bold": True, "color": fg,
         "font": SANS, "align": PP_ALIGN.CENTER},
    ], anchor=MSO_ANCHOR.MIDDLE)


# =============================================================================
# Front matter
# =============================================================================

def s_cover(prs):
    s = blank(prs)
    rect(s, 0, 0, SW, SH, fill=PAPER, line=None)
    rect(s, 0, 0, SW, 0.22, fill=BRICK, line=None)

    text(s, M, 1.55, CW, 0.3, [eyebrow(
        "DLI Conscientious Tech Design Workshop 2026  ·  Final session")])
    text(s, M, 1.95, CW * 0.82, 2.1, [
        {"t": "Values in Practice", "size": 62, "bold": True, "color": INK,
         "font": SERIF, "line": 1.0, "space_after": 6},
        {"t": "What we actually did with the values we committed to",
         "size": 21, "color": BRICK_DARK, "font": SERIF, "italic": True,
         "line": 1.15},
    ])
    rule(s, M, 4.32, 2.2, color=BRICK, weight=2.5)
    text(s, M, 4.62, CW * 0.85, 1.4, [
        {"t": "Ten Siegel PiTech PhD Impact Fellows  ·  Five minutes each",
         "size": 15, "color": INK, "font": SANS, "space_after": 7},
        {"t": "Monday, August 17  ·  Cornell Tech + Zoom", "size": 13,
         "color": INK_SOFT, "font": SANS, "space_after": 7},
        {"t": "Digital Life Initiative × Public Interest Technology, Cornell Tech",
         "size": 11.5, "color": MUTED, "font": SANS},
    ])
    return s


def s_the_ask(prs):
    s = blank(prs)
    y = slide_title(
        s, "What we are asking for",
        "Five minutes on how you put values into your project",
        "Not a project overview. We already know your project. Spend the whole "
        "five minutes on the values work — and show us the artifacts.")

    cols = [
        ("01", "Who you are, where you worked",
         "Your name, your host organization, one line on what you built or "
         "shaped this summer. A photo with your team if you have one."),
        ("02", "The values you committed to",
         "Two to four. Named, defined in your own words, and traced back to "
         "where in Discovery they came from."),
        ("03", "What you actually did about them",
         "Each value → the design requirement it produced → the concrete move "
         "you made. And whether that move shipped or is still a plan."),
        ("04", "The artifacts",
         "Screenshots, Figma frames, rubrics, code, docs, workshop photos. "
         "This is the part we most want to see. Show, don't summarise."),
        ("05", "Where values collided",
         "Which values conflicted — and which you dissolved, which you "
         "compromised, which you traded off and at what cost."),
        ("06", "Framework, verification, next steps",
         "Where Values at Play earned its keep and where it did not. How you "
         "would check the values actually landed. What happens after August."),
    ]

    cw = (CW - 2 * 0.42) / 3
    for i, (num, head, body) in enumerate(cols):
        cx = M + (i % 3) * (cw + 0.42)
        cy = y + (i // 3) * 2.28
        rect(s, cx, cy, cw, 2.0, fill=PAPER, line=LINE)
        text(s, cx + 0.26, cy + 0.24, cw - 0.52, 1.6, [
            {"t": num, "size": 13, "bold": True, "color": BRICK, "font": SERIF,
             "space_after": 6},
            {"t": head, "size": 14, "bold": True, "color": INK, "font": SANS,
             "line": 1.12, "space_after": 7},
            {"t": body, "size": 10.5, "color": INK_SOFT, "font": SANS,
             "line": 1.24},
        ])

    rule(s, M, FOOT_Y - 0.16, CW)
    text(s, M, FOOT_Y, CW, 0.3, [
        {"t": "Five minutes is short and we have ten of you — we will hold the "
              "time. Rehearse it once.",
         "size": 10.5, "italic": True, "color": BRICK_DARK, "font": SANS},
    ])
    return s


def s_how_to(prs):
    s = blank(prs)
    y = slide_title(
        s, "How to use this template",
        "Find your name, fill in your seven slides, delete nothing else",
        "Your section is already labelled with your name and host organization. "
        "Everything in grey italics is a placeholder — click it and type over it.")

    left = [
        ("Work only in your own section.",
         "Scroll to the slide with your name on it. The six slides after it are "
         "yours. Please leave everyone else's slides alone."),
        ("Overwrite the grey italic text.",
         "Grey italic = a prompt for you. Black text = a heading to keep. If a "
         "prompt does not apply to you, delete that line rather than leaving it."),
        ("Replace the dashed boxes with images.",
         "Click the dashed box, delete it, then Insert → Image. Screenshots from "
         "Figma, your repo, your host's system, or photos from the June workshop "
         "all work."),
        ("Need more room for artifacts?",
         "Duplicate your artifact slide (right-click → Duplicate slide). Only one "
         "artifact? Delete the second one. Just keep the whole thing to five "
         "minutes."),
    ]
    right = [
        ("Nothing confidential.",
         "Blur, crop, or mock up anything your host organization would not want "
         "on a shared screen. Names, addresses, case data, live credentials — "
         "check before you paste."),
        ("Speaker notes are yours.",
         "Use the notes field for what you will say. We will not read them, and "
         "they are not part of the five minutes."),
        ("\"Planned\" is a real answer.",
         "We would rather see one honest \"designed but not shipped\" than a "
         "slide that implies more landed than did. Say which is which."),
        ("Bring it back to the canvas.",
         "Most of what goes on these slides is already in your Figma Discovery "
         "and Implementation canvas. Fill the canvas first, then harvest it."),
    ]

    cw = (CW - 0.6) / 2
    for col, items in ((0, left), (1, right)):
        cx = M + col * (cw + 0.6)
        cy = y
        for head, body in items:
            text(s, cx, cy, cw, 0.9, [
                {"t": head, "size": 13, "bold": True, "color": INK,
                 "font": SANS, "space_after": 4},
                {"t": body, "size": 10.5, "color": INK_SOFT, "font": SANS,
                 "line": 1.26},
            ])
            cy += 1.16

    return s


def s_checklist(prs):
    """The four completion requirements, so they are visible to anyone who
    opens the deck rather than living only in the email."""
    s = blank(prs)
    y = slide_title(
        s, "Completing the workshop",
        "Four things, and only one of them is these slides",
        "The slides are Monday. The rest is what closes out your participation "
        "in the 2026 Conscientious Tech Design Workshop.")

    items = [
        ("Your Figma canvas", "Do this first",
         "Discovery and Implementation both filled in — Verification too if you "
         "went that route. Most of you are already there. If you are behind, "
         "finish the canvas before you touch the slides: the slides are a "
         "harvest of the canvas, not a substitute for it.", BRICK, BRICK_TINT),
        ("Both 1:1 check-ins", "Required",
         "If you have only had one, book the second with Hauke or Jae June this "
         "week. We cannot sign off on your participation without both.",
         BRICK, BRICK_TINT),
        ("These five minutes", "Due Monday",
         "Fill in the seven slides in your section of this deck before the "
         "session starts. We present straight from this deck.", BRICK,
         BRICK_TINT),
        ("The reflective write-up", "Not due Monday",
         "In the template we have shared separately. It is not due for the "
         "session — but drafting it first makes the slides much easier to "
         "write, because it is the same material in longer form.", TEAL,
         TEAL_TINT),
    ]

    cw = (CW - 3 * 0.32) / 4
    for i, (head, when, body, accent, tint) in enumerate(items):
        cx = M + i * (cw + 0.32)
        rect(s, cx, y, cw, 3.35, fill=WHITE, line=LINE)
        rect(s, cx, y, cw, 0.12, fill=accent, line=None)
        chip(s, cx + 0.24, y + 0.36, 1.62, 0.3, when, tint, accent)
        text(s, cx + 0.24, y + 0.82, cw - 0.48, 2.4, [
            {"t": head, "size": 16, "bold": True, "color": INK, "font": SERIF,
             "line": 1.1, "space_after": 9},
            {"t": body, "size": 10.5, "color": INK_SOFT, "font": SANS,
             "line": 1.28},
        ])

    rule(s, M, FOOT_Y - 0.16, CW)
    text(s, M, FOOT_Y, CW, 0.3, [
        {"t": "Links to the Figma canvas and the write-up template are in the "
              "email — replace this line with them once you have added them.",
         "size": 10, "italic": True, "color": MUTED, "font": SANS},
    ])
    notes(s, "Admin slide. Delete before presenting if you would rather not "
             "spend session time on it.")
    return s


def s_bar(prs):
    s = blank(prs)
    y = slide_title(
        s, "What a strong slide looks like",
        "Specific, evidenced, honest about the gaps",
        "Same three prompts, answered two ways. The right-hand column is what "
        "we are looking for.")

    rows = [
        ("Naming a value",
         "\"We cared about privacy.\"",
         "\"Confidentiality — for us, that a care worker can see an alert "
         "without seeing the resident's room. It came from the org's HIPAA "
         "language and from the two staff I shadowed.\""),
        ("Showing the work",
         "\"I added privacy features to the interface.\"",
         "\"Screenshot: the alert card now shows a posture icon, not a video "
         "frame. Before/after on the right. Merged into the prototype on "
         "July 22.\""),
        ("Handling a conflict",
         "\"Safety and privacy were in tension.\"",
         "\"Traded off: staff get an immediate alert, resident is notified "
         "second. Cost: the resident learns about an escalation after someone "
         "else does. We chose it knowingly; here is the note we wrote for the "
         "host.\""),
    ]

    colw = [2.5, 4.35, CW - 2.5 - 4.35 - 0.7]
    xs = [M, M + colw[0] + 0.35, M + colw[0] + colw[1] + 0.7]

    text(s, xs[1], y, colw[1], 0.3, [eyebrow("Too thin", color=MUTED)])
    text(s, xs[2], y, colw[2], 0.3, [eyebrow("What we want", color=TEAL)])
    y += 0.4

    for head, weak, strong in rows:
        h = 1.24
        rect(s, xs[1], y, colw[1], h, fill=PAPER, line=LINE)
        rect(s, xs[2], y, colw[2], h, fill=TEAL_TINT, line=TEAL, lw=1.0)
        text(s, xs[0], y + 0.06, colw[0], h, [
            {"t": head, "size": 13, "bold": True, "color": INK, "font": SANS,
             "line": 1.15},
        ])
        text(s, xs[1] + 0.22, y + 0.18, colw[1] - 0.44, h - 0.36, [
            {"t": weak, "size": 11, "italic": True, "color": MUTED,
             "font": SANS, "line": 1.25},
        ], anchor=MSO_ANCHOR.MIDDLE)
        text(s, xs[2] + 0.22, y + 0.18, colw[2] - 0.44, h - 0.36, [
            {"t": strong, "size": 10.5, "color": INK, "font": SANS,
             "line": 1.28},
        ], anchor=MSO_ANCHOR.MIDDLE)
        y += h + 0.18

    rule(s, M, FOOT_Y - 0.16, CW)
    text(s, M, FOOT_Y, CW, 0.3, [
        {"t": "The example above is invented — it is not anyone's project. Use "
              "your own words and your own evidence.",
         "size": 10, "italic": True, "color": MUTED, "font": SANS},
    ])
    return s


# =============================================================================
# Per-fellow section — 7 slides
# =============================================================================

TOTAL = 7


def f1_identity(prs, name, org, short):
    s = blank(prs)
    rect(s, 0, 0, SW, SH, fill=PAPER, line=None)
    rect(s, 0, 0, 0.26, SH, fill=BRICK, line=None)

    text(s, M + 0.2, 1.15, CW * 0.56, 0.3, [
        eyebrow("Values in practice  ·  PiTech Fellow 2026")])
    text(s, M + 0.2, 1.52, CW * 0.56, 1.35, [
        {"t": name, "size": 46, "bold": True, "color": INK, "font": SERIF,
         "line": 1.02},
    ])
    text(s, M + 0.2, 2.92, CW * 0.56, 0.5, [
        {"t": org, "size": 20, "color": BRICK_DARK, "font": SERIF,
         "italic": True, "line": 1.1},
    ])
    rule(s, M + 0.2, 3.62, 1.8, color=BRICK, weight=2.0)

    text(s, M + 0.2, 3.92, CW * 0.56, 1.5, [
        prompt("What I worked on this summer", 11),
        fill_in("One sentence. The thing itself, not the values — you have six "
                "more slides for those.", 12, space_after=10),
        prompt("My role in it", 11),
        fill_in("Designer? Analyst? The person who wrote the model? Say what you "
                "personally had your hands on.", 12),
    ])

    # photo column
    px = M + CW * 0.60
    pw = CW - (CW * 0.60)
    image_drop(s, px, 1.15, pw, 3.90,
               "You with your host-organization team, or a photo from the June "
               "workshop. Optional but nice.")
    text(s, px, 5.20, pw, 0.9, [
        prompt("Who I worked with", 11),
        fill_in("Names/roles of the people at " + short + " you did this with.",
                11),
    ])

    footer(s, name, short, 1, TOTAL, "30 sec")
    notes(s, "~30 seconds. Say your name, the org, and what the thing is — "
             "then move on. The values work is what the other six slides are "
             "for; do not spend your five minutes on a project overview.")
    return s


def f2_values(prs, name, org, short):
    s = blank(prs)
    y = slide_title(
        s, "Discovery  →  commitment",
        "The values I committed to",
        "Two to four values. Pull them straight off your Figma Discovery canvas "
        "— including any you brought yourself as the PiTech Fellow.")

    n = 3
    cw = (CW - (n - 1) * 0.38) / n
    for i in range(n):
        cx = M + i * (cw + 0.38)
        rect(s, cx, y, cw, 4.1, fill=WHITE, line=LINE)
        rect(s, cx, y, cw, 0.1, fill=BRICK if i < 2 else LINE, line=None)
        text(s, cx + 0.26, y + 0.38, cw - 0.52, 3.5, [
            {"t": "VALUE " + str(i + 1) + (" (optional)" if i == 2 else ""),
             "size": 9, "bold": True, "color": MUTED, "font": SANS,
             "space_after": 6},
            fill_in("Name the value", 22, space_after=12),
            prompt("In my project this means…", 10.5),
            fill_in("Your own definition, one sentence. Not the dictionary — "
                    "what it demands of this specific system.", 10.5,
                    space_after=11),
            prompt("Where it came from", 10.5),
            fill_in("Functional description / Key actors & stakeholders / "
                    "Technical & material constraints / Societal context / "
                    "me, the fellow — delete the rest.", 10.5,
                    space_after=11),
            prompt("Who benefits if we get it right", 10.5),
            fill_in("Be concrete about the person.", 10.5),
        ])

    footer(s, name, short, 2, TOTAL, "45 sec")
    notes(s, "~45 seconds. Two values done well beats four done thinly — "
             "delete the third card if you only committed to two. The 'where "
             "it came from' line matters: it is the difference between a value "
             "you discovered and a value you assumed. If you introduced a value "
             "nobody at the org asked for, say so — that is a real finding.")
    return s


def f3_moves(prs, name, org, short):
    s = blank(prs)
    y = slide_title(
        s, "Implementation",
        "How I operationalized each value",
        "Value → the design requirement it produced → the concrete thing that "
        "changed. Mark honestly whether it shipped or stayed a plan.")

    heads = ["Value", "What it demanded (design requirement)",
             "What I actually changed", "Status"]
    widths = [2.05, 3.55, 4.75, 1.75]
    xs, acc = [], M
    for w in widths:
        xs.append(acc)
        acc += w + 0.14

    for x, w, h in zip(xs, widths, heads):
        text(s, x, y, w, 0.28, [eyebrow(h)])
    y += 0.36
    rule(s, M, y - 0.08, CW, color=INK, weight=1.2)

    rowh = 1.10
    for r in range(3):
        ry = y + r * (rowh + 0.14)
        rect(s, xs[0], ry, widths[0], rowh, fill=BRICK_TINT, line=None)
        text(s, xs[0] + 0.16, ry + 0.14, widths[0] - 0.32, rowh - 0.28, [
            fill_in("Value " + str(r + 1), 13),
        ], anchor=MSO_ANCHOR.MIDDLE)

        rect(s, xs[1], ry, widths[1], rowh, fill=PAPER, line=LINE)
        text(s, xs[1] + 0.18, ry + 0.14, widths[1] - 0.36, rowh - 0.28, [
            fill_in("\"To honour this, the system has to ______.\" The "
                    "requirement, not the feature.", 10.5),
        ], anchor=MSO_ANCHOR.MIDDLE)

        rect(s, xs[2], ry, widths[2], rowh, fill=WHITE, line=LINE)
        text(s, xs[2] + 0.18, ry + 0.14, widths[2] - 0.36, rowh - 0.28, [
            fill_in("The specific move: the field you removed, the threshold you "
                    "changed, the consent step you added, the section you wrote "
                    "into the rubric. Name the artifact it lives in.", 10.5),
        ], anchor=MSO_ANCHOR.MIDDLE)

        rect(s, xs[3], ry, widths[3], rowh, fill=WHITE, line=LINE)
        text(s, xs[3] + 0.12, ry + 0.13, widths[3] - 0.24, rowh - 0.26, [
            {"t": "Shipped", "size": 10, "bold": True, "color": TEAL,
             "font": SANS, "space_after": 3},
            {"t": "Partially", "size": 10, "bold": True, "color": BRONZE,
             "font": SANS, "space_after": 3},
            {"t": "Planned only", "size": 10, "bold": True, "color": MUTED,
             "font": SANS, "space_after": 3},
            {"t": "keep one", "size": 8, "italic": True, "color": MUTED,
             "font": SANS},
        ], anchor=MSO_ANCHOR.MIDDLE)

    by = y + 3 * (rowh + 0.14) + 0.06
    rect(s, M, by, CW, 0.52, fill=TEAL_TINT, line=None)
    text(s, M + 0.22, by, CW - 0.44, 0.52, [
        {"t": "Add rows if you have more. If a value produced no change at all, "
              "keep the row and say so — that is a finding, not a failure.",
         "size": 10.5, "italic": True, "color": INK, "font": SANS},
    ], anchor=MSO_ANCHOR.MIDDLE)

    footer(s, name, short, 3, TOTAL, "60 sec")
    notes(s, "~60 seconds. This is the operationalization slide — the one that "
             "answers 'what did you actually do about it'. Keep the middle "
             "column at the level of a requirement ('the system must not store "
             "X') and the third column at the level of a change ('removed the "
             "X field from the intake form'). Be strict with the status column: "
             "'Planned only' is a perfectly good answer and we would much "
             "rather hear it than discover it later.")
    return s


def f_artifact(prs, name, org, short, idx, page):
    s = blank(prs)
    label = "The artifact" if idx == 1 else "The artifact, continued"
    sub = ("Show it. A screenshot, a Figma frame, a rubric, a diff, a document, "
           "a photo of the wall. Talk us through what we are looking at."
           if idx == 1 else
           "A second artifact, a before/after, or a close-up. Duplicate this "
           "slide if you need more — delete it if you do not.")
    y = slide_title(s, "Evidence", label, sub)

    iw = 7.85
    image_drop(s, M, y, iw, 4.28,
               "Screenshot / Figma frame / document / photo. Crop tight and blur "
               "anything sensitive.")

    cx = M + iw + 0.45
    cwid = CW - iw - 0.45
    text(s, cx, y, cwid, 4.28, [
        prompt("What am I looking at?", 11),
        fill_in("Name the artifact and where it lives.", 11, space_after=14),
        prompt("Which value is in here?", 11),
        fill_in("Point at the specific pixel, clause, or line.", 11,
                space_after=14),
        prompt("What did it look like before?", 11),
        fill_in("What the default would have been if you had not done the "
                "values work.", 11, space_after=14),
        prompt("Is it live?", 11),
        fill_in("Shipped / in review with the host / prototype only / "
                "recommendation in a memo.", 11),
    ])

    footer(s, name, short, page, TOTAL, "60 sec")
    if idx == 1:
        notes(s, "~60 seconds and the most important slide in your five "
                 "minutes. Put the artifact on screen and talk over it. If you "
                 "have a before/after, show both. Screenshots from Figma, your "
                 "repo, your host's system, a rubric, a memo, or a photo of the "
                 "workshop wall all count. Blur anything your host would not "
                 "want on a shared screen.")
    else:
        notes(s, "Optional. Duplicate this slide for a third artifact, or "
                 "delete it if one was enough. Whatever you keep, the whole "
                 "talk still has to land in five minutes.")
    return s


def f6_conflict(prs, name, org, short):
    s = blank(prs)
    y = slide_title(
        s, "Values in conflict",
        "What collided — and what I did about it",
        "Use the three moves from Chapter 6. Fill the ones that happened to you; "
        "delete the ones that did not.")

    cols = [
        ("Dissolved", TEAL, TEAL_TINT,
         "Redesigned so the conflict went away — both values fully honoured.",
         "What made it dissolvable?"),
        ("Compromised", BRICK, BRICK_TINT,
         "Both values partly satisfied; neither got everything.",
         "What did each value give up?"),
        ("Traded off", BRONZE, BRONZE_TINT,
         "One value explicitly prioritized over another.",
         "What is the cost, and who pays it?"),
    ]

    cw = (CW - 2 * 0.38) / 3
    for i, (head, accent, tint, blurb, last_q) in enumerate(cols):
        cx = M + i * (cw + 0.38)
        rect(s, cx, y, cw, 4.15, fill=WHITE, line=accent, lw=1.25)
        rect(s, cx, y, cw, 0.62, fill=tint, line=None)
        text(s, cx + 0.24, y, cw - 0.48, 0.62, [
            {"t": head.upper(), "size": 13, "bold": True, "color": accent,
             "font": SANS},
        ], anchor=MSO_ANCHOR.MIDDLE)
        text(s, cx + 0.24, y + 0.78, cw - 0.48, 3.2, [
            {"t": blurb, "size": 10, "italic": True, "color": INK_SOFT,
             "font": SANS, "line": 1.22, "space_after": 13},
            prompt("Which values collided", 10.5),
            fill_in("Value A vs. Value B", 10.5, space_after=12),
            prompt("What I did", 10.5),
            fill_in("The concrete move.", 10.5, space_after=12),
            prompt(last_q, 10.5),
            fill_in("Be specific.", 10.5),
        ])

    footer(s, name, short, 6, TOTAL, "60 sec")
    notes(s, "~60 seconds. Dissolution is rare and worth dwelling on if you "
             "managed one. Most real projects land on compromise or trade-off, "
             "and naming the cost out loud is the point of the exercise — a "
             "trade-off you can state is a trade-off someone else can contest. "
             "If nothing conflicted, say that and say why you think so.")
    return s


def f7_next(prs, name, org, short):
    s = blank(prs)
    y = slide_title(
        s, "The framework, and what happens next",
        "What the framework did, and what I do now",
        "Be candid on the left. Be concrete on the right.")

    cw = (CW - 0.5) / 2

    rect(s, M, y, cw, 4.15, fill=PAPER, line=LINE)
    text(s, M + 0.28, y + 0.3, cw - 0.56, 3.6, [
        eyebrow("The framework", size=10),
        {"t": "", "size": 4},
        prompt("Where it changed my thinking", 11),
        fill_in("The moment it gave you a word, a reason, or an argument you "
                "did not have before.", 11, space_after=13),
        prompt("Where it changed the artifact", 11),
        fill_in("Naming something and building something differently are two "
                "different wins. Which did you get?", 11, space_after=13),
        prompt("Where it did not help", 11),
        fill_in("Too late in the project? Too abstract for your host? Missing "
                "the people most affected? Say so — this is genuinely useful "
                "to us.", 11),
    ])

    rx = M + cw + 0.5
    rect(s, rx, y, cw, 4.15, fill=WHITE, line=TEAL, lw=1.25)
    rect(s, rx, y, cw, 0.1, fill=TEAL, line=None)
    text(s, rx + 0.28, y + 0.3, cw - 0.56, 3.6, [
        eyebrow("Verification & next steps", color=TEAL, size=10),
        {"t": "", "size": 4},
        prompt("How would I check the values actually landed?", 11),
        fill_in("A test, a metric, a review, someone to ask. Who would have to "
                "look, and at what?", 11, space_after=13),
        prompt("What I am handing over", 11),
        fill_in("What stays with your host organization after August, and who "
                "owns it.", 11, space_after=13),
        prompt("What I carry into my own research", 11),
        fill_in("One thing you will do differently in your next project.", 11),
    ])

    footer(s, name, short, 7, TOTAL, "60 sec")
    notes(s, "~60 seconds, and please be honest on the left half. 'It helped "
             "me name something but did not change the build' is a finding we "
             "want, not a disappointment. Last year's cohort told us the "
             "framework would have done more for them if it had arrived earlier "
             "— if that is true for you too, say it here. On the right, name a "
             "check someone could actually run, not an aspiration.")
    return s


# =============================================================================

def build():
    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)

    s_cover(prs)
    s_the_ask(prs)
    s_how_to(prs)
    s_bar(prs)
    s_checklist(prs)

    for name, org, short in FELLOWS:
        f1_identity(prs, name, org, short)
        f2_values(prs, name, org, short)
        f3_moves(prs, name, org, short)
        f_artifact(prs, name, org, short, 1, 4)
        f_artifact(prs, name, org, short, 2, 5)
        f6_conflict(prs, name, org, short)
        f7_next(prs, name, org, short)

    path = OUT / "2026-VAP-Fellow-Final-Presentation-Template.pptx"
    prs.save(path)
    print(f"wrote {path}  ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
    return path


if __name__ == "__main__":
    build()
