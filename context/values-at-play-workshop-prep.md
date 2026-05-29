# Workshop Prep: Values at Play Discovery — Source Material for 10 New PiTech Fellows

You are preparing physical, cut-out-able source material for a Values at Play / Conscientious Design workshop run for the new cohort of PiTech Fellows at Cornell Tech. The fellows will use these printed sheets to do the **Discovery** phase of the exercise on paper — replacing what was previously done on a digital Figma canvas. Each fellow will receive a packet of source-text snippets from their host organization's public web presence, organized by the four Discovery heuristic sources. They will then read the snippets, cut them out, and write/attach value words to each snippet as they identify what values that source surfaces.

**Critical rule: you gather source text only. You do NOT extract or infer values.** The whole point of the exercise is for fellows to do that themselves. If you find yourself writing "this surfaces the value of X" — stop. Just include the quote.

## Deliverable

One PDF per fellow, named `[fellow-lastname]_[org-shortname].pdf`. Multi-page if needed. Letter size (8.5" × 11"), portrait. Each PDF contains a packet of snippet cards the fellow can cut out.

## Step 1 — Find the fellows

The current/new cohort is listed on the PiTech site:
- Start at https://www.pi.tech.cornell.edu/ and look for the current Siegel PiTech PhD Impact Fellows cohort page (usually under "Fellowships" or "Fellows").
- For each fellow, capture: fellow's full name, host organization name, host organization website, project description as posted on PiTech site.
- If there are more or fewer than 10, work with what's there. Note the count in your final summary.

If you can't determine which cohort is "new" (incoming vs. current), ask before proceeding. Don't guess.

## Step 2 — Gather source material per fellow

For each fellow's host organization, browse the organization's website and any directly linked public sources (annual reports, press releases, founder bios, etc.). Gather raw excerpts organized by the Discovery heuristics below.

**What counts as a snippet:** a discrete passage of 1–4 sentences (or a tight bullet list) lifted nearly verbatim from a public source. Light copy-edits for clarity (e.g., removing nav-bar artifacts) are fine. Substantial paraphrasing is not — the fellows need the org's *own words* to identify values.

**Length target:** aim for 12–20 snippets per fellow, distributed across the heuristics. Skip any sub-category where the web yields nothing meaningful — better to have 12 substantive snippets than 20 padded ones.

### Heuristic 1: Functional Description — what the org and its core product do & care about

- **Mission Statement** — the org's stated mission or vision, usually on an About page.
- **Problems Solved** — what issues the org addresses, what gap it fills. Often in About, Impact, or Why We Exist pages.
- **Stated Goals** — explicit objectives, strategic priorities, slogans, program goals. Often in strategic plans, annual reports, campaign pages.

### Heuristic 2: Key Actors & Stakeholders — underlying values of the people involved

Skip "PiTech Fellow" (the fellow brings their own positionality). Gather for the rest:

- **Target Audience** — who the org primarily serves. Look for demographic descriptions, who-we-serve pages.
- **Users / Beneficiaries** — first-person or quoted statements from people the org serves; testimonials; case studies.
- **Founders** — founder bios, founding story, original vision. Especially valuable when founders are explicitly quoted about why they started the org.
- **Funders / Investors** — major funders' statements about why they support the org; donor pages; sponsor language. Government funders count.
- **Affected Communities** — extended community impact: neighborhoods, peer organizations, advocacy groups, families. Look at community partnership pages.
- **Employees / Creators** — staff perspectives, "why we work here," careers pages with culture/values statements, employee spotlights.
- **Partners** — partner organizations, corporate partnerships, coalition memberships. Partner pages often surface what the org chooses to align with.

### Heuristic 3: Technical / Material Constraints — values carried in from what's possible

These are harder to find on public sites but worth probing for:

- **Platform Limitations** — what tech the org uses or builds on; commercial vs. open source; accessibility features mentioned.
- **Data Requirements** — what data the org collects/handles; privacy policies; consent language; HIPAA/FERPA/etc. compliance statements.
- **Infrastructure Requirements** — physical sites, equipment, connectivity (especially relevant for orgs serving rural/low-resource areas).
- **Resource Constraints** — budget/staffing language, "we are a small team" framing, volunteer reliance, grant dependency.

### Heuristic 4: Societal Context — values carried in from the broader world

- **Legal & Compliance Landscape** — laws, regulations the org operates under (HIPAA, FERPA, ADA, Local Law 30, OPWDD directives, IRB requirements, municipal codes, etc.).
- **Cultural Norms** — cultural framings the org operates within or pushes against; community values; family/cultural traditions referenced.
- **Industry Standards** — sector standards, accreditation, professional norms. Mentions of best practices, certifications.
- **Geographic Context** — where the org operates and what that implies (US/Medicaid system, NYC vs. rural, federal vs. local funding, etc.).

## Step 3 — Per-snippet format

Each snippet card includes:

- **Category label** at top — one of the 18 sub-categories above (e.g., "Mission Statement", "Founders", "Legal & Compliance").
- **Body text** — the excerpt itself. Preserve quotation marks if it's a direct quote from a person; otherwise just include the passage.
- **Tiny attribution at bottom** — `[Org Name] · [source page title or short URL]`. ~6–7pt font, light grey.

## Step 4 — Page layout

- **Letter size, portrait, 0.5" margins.**
- **Header band** (top ~0.75"): Fellow full name (large, ~16pt) and host organization name (medium, ~12pt). Repeated on every page for that fellow with a "Page X of Y" indicator.
- **Body**: 2 × 3 grid of snippet cards = **6 cards per page**. Each card is approximately **3.25" wide × 3" tall**, with a 0.15" gutter between cards so scissors have room.
- **Card styling**: thin 1pt grey border (a guide for cutting). Category label in bold small caps at top of card. Body text in 9.5–10pt serif or humanist sans. Tiny attribution at the bottom in 6.5pt light grey.
- **Overflow handling**: if a snippet doesn't fit at 9.5pt, drop to 9pt; if still too long, split into "(1/2)" and "(2/2)" cards rather than truncating.
- **Multiple pages per fellow**: expect 3–4 pages per fellow at 6 cards/page for 18–24 snippets.

## Step 5 — Production

Suggested approach: HTML + CSS rendered to PDF with WeasyPrint (Python). Reasons: precise typography control, easy CSS grid for the 2×3 layout, page break control via `page-break-inside: avoid` on cards. Reportlab also works but is more verbose for this kind of layout.

Sketch:
```
- One Python script that takes a JSON input file (one entry per fellow with snippets organized by category)
- Renders an HTML template per fellow
- Calls WeasyPrint to produce one PDF per fellow
- Outputs to ./output/[lastname]_[org].pdf
```

Stage in two passes:
1. **Gathering pass** — build the JSON of snippets, ask for review before generating PDFs.
2. **Production pass** — generate all 10 PDFs.

This lets a human (Hauke) sanity-check coverage before printing.

## Quality notes

- **Don't pad.** A category with no real material is better left out than filled with generic boilerplate. Empty sub-categories are themselves diagnostic for the workshop.
- **Variety of voices matters.** Try to surface direct quotes from founders, beneficiaries, and partners where available — not just the org's own marketing copy. The exercise reveals more when the source mix is varied.
- **Don't editorialize.** No "this is important" framing. No section intros. Just the snippets.
- **Keep attribution honest.** If a quote is from a press release rather than the org's site, say so. Source URLs should be specific pages, not just the org homepage.
- **Watch for paywalls/JS-rendered sites.** If a key page won't load, note it in a "gaps" section of the summary and move on.

## Final summary to produce

After generating all PDFs, output a short markdown summary:
- Number of fellows / PDFs produced.
- Per fellow: count of snippets by heuristic source (e.g., "Functional: 4, Stakeholders: 9, Constraints: 2, Societal: 4").
- Any orgs where coverage was thin and why.
- Any sub-categories that came up empty across multiple fellows (this is useful workshop intel).
