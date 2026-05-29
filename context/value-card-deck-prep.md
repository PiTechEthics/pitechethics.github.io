# Workshop Prep: Value Card Deck for Values at Play Discovery

This is a companion to the `values-at-play-workshop-prep.md` source-material spec. The fellows will use **both** at the workshop: their personal packet of source-text snippets from their host org, **and** this shared deck of value cards. During Discovery, they read a snippet, then either grab a pre-printed value card that matches what the snippet surfaces, or write a new one on a blank.

The deck is a **seed list** — explicitly not exhaustive. Blanks are included so participants can add what's missing.

## Design rationale (for context)

The list combines three sources:

- **Schwartz's Universal Values framework** as the backbone (empirically grounded, cross-cultural, covers the full motivational space).
- **VAP / ethical-political tradition** patches in values Schwartz under-represents: Privacy, Consent, Dignity, Accountability, Transparency. These are exactly what technology design makes salient.
- **Civic-tech functional values** that always show up in PiTech projects but don't appear on most "values" lists: Accuracy, Reliability, Efficiency, Accessibility, Usability.

Schwartz's "power/tradition" values (Status, Wealth, Conformity) are deliberately included even though they aren't aspirational, because half the point of VAP is surfacing values that are *operating* in a project regardless of whether participants would claim them. If a project is driven by funder-impressiveness, "Status" needs to be a card you can pick up.

## The deck — 10 color-coded groups

Each card carries: the **value word** (large, centered, bold), the **group name** in small caps below, and a **colored background** (full card or thick top stripe — see Layout).

### Group 1 · Care & Solidarity
**Color:** warm yellow (`#F5C95D`)
Values: Care, Compassion, Empathy, Kindness, Generosity, Cooperation, Solidarity, Community, Sympathy, Hospitality

### Group 2 · Justice & Inclusion
**Color:** green (`#7DB46C`)
Values: Justice, Fairness, Equality, Equity, Inclusion, Diversity, Accessibility, Tolerance, Egalitarianism, Non-discrimination

### Group 3 · Autonomy & Agency
**Color:** blue (`#5B8DBF`)
Values: Autonomy, Freedom, Liberty, Independence, Self-determination, Empowerment, Choice, Self-direction, Voice

### Group 4 · Privacy, Dignity & Respect
**Color:** purple (`#9B6BB0`)
Values: Privacy, Dignity, Respect, Consent, Anonymity, Confidentiality, Honor, Recognition

### Group 5 · Trust & Integrity
**Color:** magenta (`#C76B98`)
Values: Honesty, Transparency, Trust, Accountability, Integrity, Authenticity, Truthfulness, Responsibility

### Group 6 · Safety & Wellbeing
**Color:** coral (`#E08672`)
Values: Safety, Security, Health, Wellbeing, Peace, Stability, Resilience, Comfort

### Group 7 · Quality & Effectiveness
**Color:** slate grey (`#8B95A3`)
Values: Efficiency, Accuracy, Reliability, Usability, Robustness, Scalability, Mastery, Performance

### Group 8 · Creativity & Stimulation
**Color:** teal (`#5BAFA8`)
Values: Creativity, Innovation, Curiosity, Playfulness, Humor, Beauty, Imagination, Style, Pleasure

### Group 9 · Stewardship & Sustainability
**Color:** forest green (`#4A7C59`)
Values: Sustainability, Environmentalism, Stewardship, Future generations, Conservation, Long-term thinking

### Group 10 · Tradition, Power & Status
**Color:** bronze (`#A0764F`)
Values: Tradition, Heritage, Loyalty, Belonging, Conformity, Achievement, Status, Power, Wealth, Prestige

**Total: 86 value cards** across 10 groups.

## Blank cards

For each group, include **3 blank cards** of that color (same layout, value word area empty, with a faint underline for hand-writing). The group name in small caps stays at the top so participants writing in a value still anchor it to a category.

**Total blanks: 30 cards.**

## Combined deck

**~116 cards total.** At 10 per page (see Layout) that's **12 pages** to print.

## Card layout

Match the format of the existing GAGCards reference deck (which Hauke shared as a reference):

- **Letter page, portrait, 0.5" margins.**
- **2 columns × 5 rows of cards per page = 10 cards/page.**
- **Each card: ~3.75" wide × 1.85" tall**, with a 0.1" gutter between cards for scissor clearance.
- **Card content:**
  - Full-card colored background (light tint, ~30% saturation so black text is legible) — OR — top stripe ~25% of card height in full color with white card body. **Recommendation: full-card light tint.** It's faster for participants to spot from across a table.
  - **Value word**: bold sans-serif (Inter, Helvetica, or Arial), ~28–32pt, centered, black, vertically centered with slight bias upward.
  - **Group label**: small caps, ~8pt, ~50% black, centered below the value word, e.g. "PRIVACY, DIGNITY & RESPECT".
  - **Thin border**: 0.75pt mid-grey (cut guide).
- **Blank cards**: same as above, but value word area is replaced with a single horizontal line at the same vertical position, drawn at 0.5pt black. Group label still shown.

## File output

Single PDF: `value-card-deck.pdf` — 12 pages, ready for color printing on letter cardstock.

Optional second output: `value-card-deck-bw.pdf` — same deck but with group identity carried by a pattern (diagonal stripes, dots, crosshatch, etc.) instead of color, for environments without color printing. **Only produce this if asked** — color is the primary path.

## Production approach

Same pipeline as the source-material spec: HTML + CSS + WeasyPrint, with CSS Grid for the 2×5 layout and a CSS class per group carrying the background color. Input is the structured value data below.

## Values data (JSON, for the pipeline)

```json
{
  "groups": [
    {
      "id": "care",
      "name": "Care & Solidarity",
      "color": "#F5C95D",
      "values": ["Care", "Compassion", "Empathy", "Kindness", "Generosity", "Cooperation", "Solidarity", "Community", "Sympathy", "Hospitality"]
    },
    {
      "id": "justice",
      "name": "Justice & Inclusion",
      "color": "#7DB46C",
      "values": ["Justice", "Fairness", "Equality", "Equity", "Inclusion", "Diversity", "Accessibility", "Tolerance", "Egalitarianism", "Non-discrimination"]
    },
    {
      "id": "autonomy",
      "name": "Autonomy & Agency",
      "color": "#5B8DBF",
      "values": ["Autonomy", "Freedom", "Liberty", "Independence", "Self-determination", "Empowerment", "Choice", "Self-direction", "Voice"]
    },
    {
      "id": "dignity",
      "name": "Privacy, Dignity & Respect",
      "color": "#9B6BB0",
      "values": ["Privacy", "Dignity", "Respect", "Consent", "Anonymity", "Confidentiality", "Honor", "Recognition"]
    },
    {
      "id": "trust",
      "name": "Trust & Integrity",
      "color": "#C76B98",
      "values": ["Honesty", "Transparency", "Trust", "Accountability", "Integrity", "Authenticity", "Truthfulness", "Responsibility"]
    },
    {
      "id": "safety",
      "name": "Safety & Wellbeing",
      "color": "#E08672",
      "values": ["Safety", "Security", "Health", "Wellbeing", "Peace", "Stability", "Resilience", "Comfort"]
    },
    {
      "id": "quality",
      "name": "Quality & Effectiveness",
      "color": "#8B95A3",
      "values": ["Efficiency", "Accuracy", "Reliability", "Usability", "Robustness", "Scalability", "Mastery", "Performance"]
    },
    {
      "id": "creativity",
      "name": "Creativity & Stimulation",
      "color": "#5BAFA8",
      "values": ["Creativity", "Innovation", "Curiosity", "Playfulness", "Humor", "Beauty", "Imagination", "Style", "Pleasure"]
    },
    {
      "id": "stewardship",
      "name": "Stewardship & Sustainability",
      "color": "#4A7C59",
      "values": ["Sustainability", "Environmentalism", "Stewardship", "Future generations", "Conservation", "Long-term thinking"]
    },
    {
      "id": "tradition",
      "name": "Tradition, Power & Status",
      "color": "#A0764F",
      "values": ["Tradition", "Heritage", "Loyalty", "Belonging", "Conformity", "Achievement", "Status", "Power", "Wealth", "Prestige"]
    }
  ],
  "blanks_per_group": 3,
  "layout": {
    "page_size": "letter",
    "orientation": "portrait",
    "margin_inches": 0.5,
    "columns": 2,
    "rows": 5,
    "cards_per_page": 10,
    "gutter_inches": 0.1
  }
}
```

## Print recommendation

- **White cardstock**, 65lb or 80lb cover weight, color print.
- One full deck per workshop table of 3–4 fellows is enough — they share. **Print 3 decks** for a 10-person workshop.
- Trim with a paper cutter, not scissors, if available — straight edges matter for handling.

## Final summary to produce

After generating the PDF, output a short markdown summary:
- Total card count, broken down by group + blanks.
- Confirmation that all 10 group colors render distinguishably in a test print (if printer available; otherwise note skipped).
- Any values where the word length pushed font size below 24pt (these may need a smaller-font variant card).
