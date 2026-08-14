#!/usr/bin/env python3
"""Build the 5-minute final-presentation slide template for the 2026 PiTech
fellows (DLI Conscientious Tech Design Workshop).

The deck is a *template*: 5 front-matter slides explaining the ask, then a
7-slide section per fellow with name + host org already filled in. Everything
else is placeholder text the fellow overwrites.

Design constraints:
  - 16:9, built for upload to Google Slides (File > Import slides / Upload).
  - Plain text boxes and rectangles only — no groups, no masters, no SmartArt —
    so every element stays directly editable after the Slides conversion.
  - Arial + Georgia only. Both are guaranteed present in Google Slides, so
    nothing silently reflows on import.
  - **Large type, high contrast.** Body copy bottoms out at 13pt and every text
    colour clears ~6:1 against its background — this gets projected in a room
    and read from the back. Copy is deliberately terse so the big type fits;
    if you add words here, check the render before shipping.

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

# ---- palette ----------------------------------------------------------------
# Same ink/brick/teal family as the printed workshop material, pushed darker.
# The *_TEXT variants are for type; the plain names are for fills and rules,
# where the lighter chroma still reads.

INK         = RGBColor(0x1A, 0x15, 0x14)
INK_SOFT    = RGBColor(0x45, 0x3D, 0x3A)
MUTED       = RGBColor(0x66, 0x5C, 0x57)   # placeholder prose — still readable
BRICK       = RGBColor(0xB7, 0x55, 0x52)
BRICK_TEXT  = RGBColor(0x8F, 0x2D, 0x2A)
BRICK_TINT  = RGBColor(0xF2, 0xE3, 0xE1)
TEAL        = RGBColor(0x2F, 0x8D, 0x90)
TEAL_TEXT   = RGBColor(0x1B, 0x66, 0x69)
TEAL_TINT   = RGBColor(0xDC, 0xED, 0xED)
BRONZE      = RGBColor(0xA0, 0x76, 0x4F)
BRONZE_TEXT = RGBColor(0x77, 0x52, 0x2F)
BRONZE_TINT = RGBColor(0xF0, 0xE7, 0xDD)
PAPER       = RGBColor(0xFA, 0xF6, 0xF2)
LINE        = RGBColor(0xB0, 0xA4, 0x9C)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)

SANS  = "Arial"
SERIF = "Georgia"

# ---- type scale -------------------------------------------------------------

T_TITLE   = 34
T_SUB     = 15
T_EYEBROW = 12.5
T_PROMPT  = 14.5
T_FILL    = 14
T_CARD_H  = 17
T_CARD_B  = 13.5
T_FOOT    = 11.5

# ---- geometry ---------------------------------------------------------------

SW, SH = 13.333, 7.5           # slide, inches
M      = 0.55                  # side margin
CW     = SW - 2 * M            # content width
FOOT_Y = 7.00                  # footer baseline
FOOT_R = FOOT_Y - 0.16         # footer rule
BOTTOM = FOOT_R - 0.14         # lowest a content box may reach


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

def rect(slide, x, y, w, h, fill=None, line=None, lw=1.0, dash=False,
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
            # python-pptx exposes no dash enum on LineFormat; set it in the XML
            from pptx.oxml.ns import qn
            ln = s.line._get_or_add_ln()
            ln.append(ln.makeelement(qn("a:prstDash"), {"val": "dash"}))
    s.text_frame.text = ""
    return s


def text(slide, x, y, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         wrap=True):
    """runs: one dict per paragraph — {t, size, bold, italic, color, font,
    space_after, space_before, line, align}."""
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
        f.size = Pt(r.get("size", T_FILL))
        f.bold = r.get("bold", False)
        f.italic = r.get("italic", False)
        f.color.rgb = r.get("color", INK)
        f.name = r.get("font", SANS)
    return box


def eyebrow(t, color=BRICK_TEXT, size=T_EYEBROW):
    return {"t": t.upper(), "size": size, "bold": True, "color": color,
            "font": SANS}


def prompt(t, size=T_PROMPT):
    """The question we are asking the fellow."""
    return {"t": t, "size": size, "bold": True, "color": INK, "font": SANS}


def fill_in(t, size=T_FILL, space_after=0):
    """Placeholder prose the fellow overwrites."""
    return {"t": t, "size": size, "italic": True, "color": MUTED, "font": SANS,
            "space_after": space_after, "line": 1.16}


def rule(slide, x, y, w, color=LINE, weight=1.0):
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
    rule(slide, M, FOOT_R, CW, color=LINE, weight=1.0)
    text(slide, M, FOOT_Y, CW * 0.6, 0.3, [
        {"t": f"{fellow}  ·  {org}", "size": T_FOOT, "bold": True,
         "color": INK_SOFT, "font": SANS},
    ])
    text(slide, M + CW * 0.6, FOOT_Y, CW * 0.4, 0.3, [
        {"t": f"{n} of {total}  ·  aim for {timing}", "size": T_FOOT,
         "color": MUTED, "font": SANS, "align": PP_ALIGN.RIGHT},
    ])


def slide_title(slide, kicker, title, sub=None):
    """Returns the y at which slide content may start.

    The title box grows to two lines past ~48 characters and everything below
    it moves down, so the layout survives later edits to these strings.
    """
    y = 0.45
    text(slide, M, y, CW, 0.28, [eyebrow(kicker)])
    th = 0.58 * (1 if len(title) <= 48 else 2)
    text(slide, M, y + 0.31, CW, th + 0.14, [
        {"t": title, "size": T_TITLE, "bold": True, "color": INK,
         "font": SERIF, "line": 1.04},
    ])
    if sub:
        sy = y + 0.33 + th + 0.08
        text(slide, M, sy, CW, 0.40, [
            {"t": sub, "size": T_SUB, "color": INK_SOFT, "font": SANS,
             "line": 1.2},
        ])
        return sy + 0.58
    return y + 0.33 + th + 0.22


def notes(slide, body):
    slide.notes_slide.notes_text_frame.text = body


def image_drop(slide, x, y, w, h, caption):
    """A dashed box the fellow deletes and replaces with a pasted image."""
    rect(slide, x, y, w, h, fill=PAPER, line=BRICK, lw=1.5, dash=True)
    text(slide, x + 0.3, y + h / 2 - 0.5, w - 0.6, 1.0, [
        {"t": "PASTE YOUR IMAGE HERE", "size": 15, "bold": True,
         "color": BRICK_TEXT, "font": SANS, "align": PP_ALIGN.CENTER,
         "space_after": 6},
        {"t": caption, "size": 12.5, "italic": True, "color": MUTED,
         "font": SANS, "align": PP_ALIGN.CENTER, "line": 1.2},
    ], anchor=MSO_ANCHOR.MIDDLE)


def chip(slide, x, y, w, h, label, fill, fg):
    rect(slide, x, y, w, h, fill=fill, line=None,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(slide, x, y, w, h, [
        {"t": label.upper(), "size": 12, "bold": True, "color": fg,
         "font": SANS, "align": PP_ALIGN.CENTER},
    ], anchor=MSO_ANCHOR.MIDDLE)


# =============================================================================
# Front matter
# =============================================================================

def s_cover(prs):
    s = blank(prs)
    rect(s, 0, 0, SW, SH, fill=PAPER, line=None)
    rect(s, 0, 0, SW, 0.26, fill=BRICK, line=None)

    text(s, M, 1.45, CW, 0.34, [eyebrow(
        "DLI Conscientious Tech Design Workshop 2026  ·  Final session",
        size=14)])
    text(s, M, 1.88, CW * 0.88, 2.3, [
        {"t": "Values in Practice", "size": 72, "bold": True, "color": INK,
         "font": SERIF, "line": 1.0, "space_after": 8},
        {"t": "What we actually did with the values we committed to",
         "size": 25, "color": BRICK_TEXT, "font": SERIF, "italic": True,
         "line": 1.15},
    ])
    rule(s, M, 4.55, 2.4, color=BRICK, weight=3.0)
    text(s, M, 4.88, CW * 0.9, 1.6, [
        {"t": "Ten Siegel PiTech PhD Impact Fellows  ·  Five minutes each",
         "size": 19, "bold": True, "color": INK, "font": SANS,
         "space_after": 9},
        {"t": "Monday, August 17  ·  Cornell Tech + Zoom", "size": 16,
         "color": INK_SOFT, "font": SANS, "space_after": 9},
        {"t": "Digital Life Initiative × Public Interest Technology, Cornell Tech",
         "size": 14, "color": MUTED, "font": SANS},
    ])
    return s


def s_the_ask(prs):
    s = blank(prs)
    y = slide_title(
        s, "What we are asking for",
        "Five minutes on how you put values to work",
        "Not a project overview — we already know your project. Spend the whole "
        "five minutes on the values work, and show us the artifacts.")

    cols = [
        ("01", "Who you are, where you worked",
         "Name, host organization, one line on what you built."),
        ("02", "The values you committed to",
         "Two to four. Named, defined in your words, traced to Discovery."),
        ("03", "What you did about them",
         "Each value → the requirement → the change. Shipped, or still a plan?"),
        ("04", "The artifacts",
         "Screenshots, Figma frames, rubrics, docs, photos. The main event."),
        ("05", "Where values collided",
         "What you dissolved, what you compromised, what you traded off."),
        ("06", "Framework and next steps",
         "Where it helped and where it did not. How you would verify."),
    ]

    cw = (CW - 2 * 0.36) / 3
    ch = 2.15
    for i, (num, head, body) in enumerate(cols):
        cx = M + (i % 3) * (cw + 0.36)
        cy = y + (i // 3) * (ch + 0.24)
        rect(s, cx, cy, cw, ch, fill=PAPER, line=LINE)
        rect(s, cx, cy, cw, 0.09, fill=BRICK, line=None)
        text(s, cx + 0.26, cy + 0.28, cw - 0.52, ch - 0.5, [
            {"t": num, "size": 16, "bold": True, "color": BRICK_TEXT,
             "font": SERIF, "space_after": 7},
            {"t": head, "size": T_CARD_H, "bold": True, "color": INK,
             "font": SANS, "line": 1.1, "space_after": 8},
            {"t": body, "size": T_CARD_B, "color": INK_SOFT, "font": SANS,
             "line": 1.25},
        ])

    rule(s, M, FOOT_R, CW)
    text(s, M, FOOT_Y, CW, 0.32, [
        {"t": "Five minutes is short and there are ten of you — we will hold "
              "the time. Rehearse it once.",
         "size": 13, "bold": True, "italic": True, "color": BRICK_TEXT,
         "font": SANS},
    ])
    return s


def s_how_to(prs):
    s = blank(prs)
    y = slide_title(
        s, "How to use this template",
        "Fill in your seven slides, leave the rest alone",
        "Your section is already labelled with your name and host organization. "
        "Grey italic text is a placeholder — click it and type over it.")

    left = [
        ("Work only in your own section.",
         "Scroll to the slide with your name on it. The six slides after it are "
         "yours. Please leave everyone else's alone."),
        ("Overwrite the grey italics.",
         "Grey italic = a prompt for you. Black = a heading to keep. If a "
         "prompt does not apply, delete the line rather than leave it blank."),
        ("Replace the dashed boxes with images.",
         "Click the dashed box, delete it, then Insert → Image. Figma frames, "
         "screenshots, and June workshop photos all work."),
    ]
    right = [
        ("Need more room? Duplicate.",
         "Right-click → Duplicate slide for a third artifact; delete the second "
         "if one was enough. Speaker notes are yours and are not timed."),
        ("Nothing confidential.",
         "Blur, crop, or mock up anything your host would not want on a shared "
         "screen. Names, case data, credentials — check before you paste."),
        ("\"Planned\" is a real answer.",
         "One honest \"designed but not shipped\" beats a slide implying more "
         "landed than did. Say which is which."),
    ]

    cw = (CW - 0.7) / 2
    for col, items in ((0, left), (1, right)):
        cx = M + col * (cw + 0.7)
        cy = y
        for head, body in items:
            text(s, cx, cy, cw, 1.4, [
                {"t": head, "size": 16.5, "bold": True, "color": INK,
                 "font": SANS, "space_after": 5},
                {"t": body, "size": T_CARD_B, "color": INK_SOFT, "font": SANS,
                 "line": 1.3},
            ])
            cy += 1.58

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
         "\"Confidentiality — a care worker sees the alert without seeing the "
         "resident's room. From the org's HIPAA language and two staff I "
         "shadowed.\""),
        ("Showing the work",
         "\"I added privacy features.\"",
         "\"The alert card now shows a posture icon, not a video frame. "
         "Before/after on the right. Merged July 22.\""),
        ("Handling a conflict",
         "\"Safety and privacy were in tension.\"",
         "\"Traded off: staff alerted first, resident second. Cost: they learn "
         "of an escalation after someone else. We chose it knowingly.\""),
    ]

    colw = [2.45, 3.75, CW - 2.45 - 3.75 - 0.7]
    xs = [M, M + colw[0] + 0.35, M + colw[0] + colw[1] + 0.7]

    text(s, xs[1], y, colw[1], 0.3, [eyebrow("Too thin", color=MUTED)])
    text(s, xs[2], y, colw[2], 0.3, [eyebrow("What we want", color=TEAL_TEXT)])
    y += 0.42

    h = 1.32
    for head, weak, strong in rows:
        rect(s, xs[1], y, colw[1], h, fill=PAPER, line=LINE)
        rect(s, xs[2], y, colw[2], h, fill=TEAL_TINT, line=TEAL, lw=1.5)
        text(s, xs[0], y + 0.06, colw[0], h, [
            {"t": head, "size": 16.5, "bold": True, "color": INK, "font": SANS,
             "line": 1.14},
        ])
        text(s, xs[1] + 0.22, y + 0.16, colw[1] - 0.44, h - 0.32, [
            {"t": weak, "size": T_CARD_B, "italic": True, "color": MUTED,
             "font": SANS, "line": 1.26},
        ], anchor=MSO_ANCHOR.MIDDLE)
        text(s, xs[2] + 0.24, y + 0.16, colw[2] - 0.48, h - 0.32, [
            {"t": strong, "size": T_CARD_B, "color": INK, "font": SANS,
             "line": 1.28},
        ], anchor=MSO_ANCHOR.MIDDLE)
        y += h + 0.2

    rule(s, M, FOOT_R, CW)
    text(s, M, FOOT_Y, CW, 0.32, [
        {"t": "The example above is invented — it is not anyone's project.",
         "size": 12.5, "italic": True, "color": MUTED, "font": SANS},
    ])
    return s


def s_checklist(prs):
    """The four completion requirements, visible to anyone who opens the deck
    rather than living only in the email."""
    s = blank(prs)
    y = slide_title(
        s, "Completing the workshop",
        "Four things — only one of them is these slides",
        "The slides are Monday. The rest is what closes out your participation "
        "in the 2026 Conscientious Tech Design Workshop.")

    items = [
        ("Your Figma canvas", "Do this first",
         "Discovery and Implementation filled in — Verification too if you went "
         "that route. If you are behind, finish it before the slides.",
         BRICK, BRICK_TINT),
        ("Both 1:1 check-ins", "Required",
         "If you have had only one, book the second with Hauke or Jae June this "
         "week. We cannot sign off without both.", BRICK, BRICK_TINT),
        ("These five minutes", "Due Monday",
         "Fill in the seven slides in your section before the session starts. "
         "We present straight from this deck.", BRICK, BRICK_TINT),
        ("The reflective write-up", "Not due Monday",
         "In the template shared separately. Not due for the session — but it "
         "is the same material in longer form, so it makes the slides easier.",
         TEAL, TEAL_TINT),
    ]

    cw = (CW - 3 * 0.3) / 4
    for i, (head, when, body, accent, tint) in enumerate(items):
        cx = M + i * (cw + 0.3)
        rect(s, cx, y, cw, BOTTOM - y, fill=WHITE, line=LINE)
        rect(s, cx, y, cw, 0.13, fill=accent, line=None)
        chip(s, cx + 0.22, y + 0.36, 1.95, 0.34, when, tint,
             BRICK_TEXT if accent is BRICK else TEAL_TEXT)
        text(s, cx + 0.22, y + 0.9, cw - 0.44, BOTTOM - y - 1.1, [
            {"t": head, "size": 18, "bold": True, "color": INK, "font": SERIF,
             "line": 1.08, "space_after": 9},
            {"t": body, "size": T_CARD_B, "color": INK_SOFT, "font": SANS,
             "line": 1.28},
        ])

    rule(s, M, FOOT_R, CW)
    text(s, M, FOOT_Y, CW, 0.32, [
        {"t": "Links to the Figma canvas and the write-up template are in the "
              "email — paste them here.",
         "size": 12.5, "italic": True, "color": MUTED, "font": SANS},
    ])
    notes(s, "Admin slide. Delete before presenting if you would rather not "
             "spend session time on it.")
    return s


# =============================================================================
# Per-fellow section — 7 slides
# =============================================================================

TOTAL = 7


def f1_identity(prs, name, org, short):
    s = blank(prs)
    rect(s, 0, 0, SW, SH, fill=PAPER, line=None)
    rect(s, 0, 0, 0.30, SH, fill=BRICK, line=None)

    text(s, M + 0.28, 1.05, CW * 0.56, 0.34, [
        eyebrow("Values in practice  ·  PiTech Fellow 2026", size=14)])
    text(s, M + 0.28, 1.48, CW * 0.58, 1.5, [
        {"t": name, "size": 58, "bold": True, "color": INK, "font": SERIF,
         "line": 1.02},
    ])
    text(s, M + 0.28, 3.05, CW * 0.58, 0.6, [
        {"t": org, "size": 24, "color": BRICK_TEXT, "font": SERIF,
         "italic": True, "line": 1.1},
    ])
    rule(s, M + 0.28, 3.86, 2.0, color=BRICK, weight=3.0)

    text(s, M + 0.28, 4.18, CW * 0.56, 2.0, [
        prompt("What I worked on this summer"),
        fill_in("One sentence. The thing itself — you have six more slides for "
                "the values.", space_after=14),
        prompt("My role in it"),
        fill_in("Designer? Analyst? The person who wrote the model? What you "
                "personally had your hands on."),
    ])

    px = M + CW * 0.61
    pw = CW - (CW * 0.61)
    image_drop(s, px, 1.05, pw, 4.05,
               "You with your host-organization team, or a photo from the June "
               "workshop. Optional but nice.")
    text(s, px, 5.35, pw, 1.0, [
        prompt("Who I worked with"),
        fill_in("Names and roles of the people at " + short + "."),
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
        "Two to four values, straight off your Figma Discovery canvas — "
        "including any you brought yourself as the PiTech Fellow.")

    n = 3
    cw = (CW - (n - 1) * 0.36) / n
    ch = BOTTOM - y
    for i in range(n):
        cx = M + i * (cw + 0.36)
        rect(s, cx, y, cw, ch, fill=WHITE, line=LINE)
        rect(s, cx, y, cw, 0.13, fill=BRICK if i < 2 else LINE, line=None)
        text(s, cx + 0.26, y + 0.4, cw - 0.52, ch - 0.6, [
            {"t": "VALUE " + str(i + 1) + (" (OPTIONAL)" if i == 2 else ""),
             "size": 11.5, "bold": True, "color": MUTED, "font": SANS,
             "space_after": 8},
            fill_in("Name the value", 28, space_after=16),
            prompt("In my project this means…"),
            fill_in("Your own definition — what it demands of this system.",
                    space_after=16),
            prompt("Where it came from"),
            fill_in("Functional / Stakeholders / Constraints / Societal / me, "
                    "the fellow — keep one."),
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
        "Value → the requirement it produced → what actually changed. Mark "
        "honestly whether it shipped or stayed a plan.")

    heads = ["Value", "What it demanded", "What I actually changed", "Status"]
    widths = [2.15, 3.45, 4.35, 1.86]
    xs, acc = [], M
    for w in widths:
        xs.append(acc)
        acc += w + 0.14

    for x, w, h in zip(xs, widths, heads):
        text(s, x, y, w, 0.3, [eyebrow(h)])
    y += 0.4
    rule(s, M, y - 0.1, CW, color=INK, weight=1.75)

    rowh = 1.12
    for r in range(3):
        ry = y + r * (rowh + 0.14)
        rect(s, xs[0], ry, widths[0], rowh, fill=BRICK_TINT, line=None)
        text(s, xs[0] + 0.16, ry + 0.14, widths[0] - 0.32, rowh - 0.28, [
            fill_in("Value " + str(r + 1), 16),
        ], anchor=MSO_ANCHOR.MIDDLE)

        rect(s, xs[1], ry, widths[1], rowh, fill=PAPER, line=LINE)
        text(s, xs[1] + 0.18, ry + 0.14, widths[1] - 0.36, rowh - 0.28, [
            fill_in("\"The system has to ______.\" The requirement, not the "
                    "feature.", 13.5),
        ], anchor=MSO_ANCHOR.MIDDLE)

        rect(s, xs[2], ry, widths[2], rowh, fill=WHITE, line=LINE)
        text(s, xs[2] + 0.18, ry + 0.14, widths[2] - 0.36, rowh - 0.28, [
            fill_in("The field you removed, the threshold you changed, the "
                    "consent step you added. Name the artifact.", 13.5),
        ], anchor=MSO_ANCHOR.MIDDLE)

        rect(s, xs[3], ry, widths[3], rowh, fill=WHITE, line=LINE)
        text(s, xs[3] + 0.12, ry + 0.12, widths[3] - 0.24, rowh - 0.24, [
            {"t": "Shipped", "size": 13, "bold": True, "color": TEAL_TEXT,
             "font": SANS, "space_after": 4},
            {"t": "Partially", "size": 13, "bold": True, "color": BRONZE_TEXT,
             "font": SANS, "space_after": 4},
            {"t": "Planned only", "size": 13, "bold": True, "color": MUTED,
             "font": SANS, "space_after": 4},
            {"t": "keep one", "size": 10, "italic": True, "color": MUTED,
             "font": SANS},
        ], anchor=MSO_ANCHOR.MIDDLE)

    by = y + 3 * (rowh + 0.14) + 0.02
    rect(s, M, by, CW, 0.46, fill=TEAL_TINT, line=None)
    text(s, M + 0.24, by, CW - 0.48, 0.46, [
        {"t": "Add rows if you have more. If a value produced no change at "
              "all, keep the row and say so — that is a finding, not a failure.",
         "size": 13, "italic": True, "color": INK, "font": SANS},
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

    iw = 7.6
    image_drop(s, M, y, iw, BOTTOM - y,
               "Screenshot / Figma frame / document / photo. Crop tight and "
               "blur anything sensitive.")

    cx = M + iw + 0.45
    cwid = CW - iw - 0.45
    text(s, cx, y, cwid, BOTTOM - y, [
        prompt("What am I looking at?"),
        fill_in("Name the artifact and where it lives.", space_after=16),
        prompt("Which value is in here?"),
        fill_in("Point at the specific pixel, clause, or line.", space_after=16),
        prompt("What did it look like before?"),
        fill_in("The default you would have shipped without the values work.",
                space_after=16),
        prompt("Is it live?"),
        fill_in("Shipped / in review / prototype only / a recommendation in a "
                "memo."),
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
        "The three moves from Chapter 6. Fill the ones that happened to you; "
        "delete the ones that did not.")

    cols = [
        ("Dissolved", TEAL, TEAL_TEXT, TEAL_TINT,
         "Redesigned so the conflict went away — both values fully honoured.",
         "What made it dissolvable?"),
        ("Compromised", BRICK, BRICK_TEXT, BRICK_TINT,
         "Both values partly satisfied; neither got everything.",
         "What did each value give up?"),
        ("Traded off", BRONZE, BRONZE_TEXT, BRONZE_TINT,
         "One value explicitly prioritized over another.",
         "What is the cost, and who pays it?"),
    ]

    cw = (CW - 2 * 0.36) / 3
    ch = BOTTOM - y
    for i, (head, accent, fg, tint, blurb, last_q) in enumerate(cols):
        cx = M + i * (cw + 0.36)
        rect(s, cx, y, cw, ch, fill=WHITE, line=accent, lw=1.75)
        rect(s, cx, y, cw, 0.68, fill=tint, line=None)
        text(s, cx + 0.24, y, cw - 0.48, 0.68, [
            {"t": head.upper(), "size": 16.5, "bold": True, "color": fg,
             "font": SANS},
        ], anchor=MSO_ANCHOR.MIDDLE)
        text(s, cx + 0.24, y + 0.86, cw - 0.48, ch - 1.0, [
            {"t": blurb, "size": 12.5, "italic": True, "color": INK_SOFT,
             "font": SANS, "line": 1.22, "space_after": 15},
            prompt("Which values collided"),
            fill_in("Value A vs. Value B", space_after=14),
            prompt("What I did"),
            fill_in("The concrete move.", space_after=14),
            prompt(last_q),
            fill_in("Be specific."),
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
    ch = BOTTOM - y

    rect(s, M, y, cw, ch, fill=PAPER, line=LINE)
    text(s, M + 0.3, y + 0.34, cw - 0.6, ch - 0.6, [
        eyebrow("The framework", size=13),
        {"t": "", "size": 6},
        prompt("Where it changed my thinking"),
        fill_in("The moment it gave you a word, a reason, or an argument you "
                "did not have before.", space_after=16),
        prompt("Where it changed the artifact"),
        fill_in("Naming something and building something differently are two "
                "different wins. Which did you get?", space_after=16),
        prompt("Where it did not help"),
        fill_in("Too late? Too abstract for your host? Missing the people most "
                "affected? Say so — this is genuinely useful to us."),
    ])

    rx = M + cw + 0.5
    rect(s, rx, y, cw, ch, fill=WHITE, line=TEAL, lw=1.75)
    rect(s, rx, y, cw, 0.13, fill=TEAL, line=None)
    text(s, rx + 0.3, y + 0.4, cw - 0.6, ch - 0.66, [
        eyebrow("Verification & next steps", color=TEAL_TEXT, size=13),
        {"t": "", "size": 6},
        prompt("How would I check the values actually landed?"),
        fill_in("A test, a metric, a review, someone to ask. Who looks, and at "
                "what?", space_after=16),
        prompt("What I am handing over"),
        fill_in("What stays with your host organization after August, and who "
                "owns it.", space_after=16),
        prompt("What I carry into my own research"),
        fill_in("One thing you will do differently next time."),
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
    print(f"wrote {path}  ({len(prs.slides._sldIdLst)} slides)")
    return path


if __name__ == "__main__":
    build()
