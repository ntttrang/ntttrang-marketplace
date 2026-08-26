---
name: drawio-convention-lint
description: 'Use when the user shares a .drawio/.xml/.svg diagram (or a folder of them) and wants it checked, reviewed, validated, audited, linted, or improved for quality and consistency — or asks "is this diagram good", "review my diagram", "check this against our conventions". Checks naming conventions, unlabeled lines/connectors/edges, missing legend when color encodes meaning, page/layer/node metadata, placeholder labels, C4-style abstraction-level mixing, orphan nodes and dangling edges, and outputs a review-style Markdown report with concrete fixes. Use it even when the user only mentions one of these concerns (e.g. just "label check") — the review covers all categories. Not for explaining what a diagram depicts (that is drawio-understand), not for creating or editing diagrams from scratch.'
---

# Lint a draw.io diagram against conventions

You are reviewing a diagram the way a senior engineer reviews a pull request: not "does it parse" but "will a teammate misread this six months from now?". Every finding should explain **why it hurts readability** and **how to fix it** — a rule ID alone teaches nobody anything.

## Inputs

- `.drawio` / `.xml` file (uncompressed or base64+deflate compressed) — best input
- `.svg` exported from draw.io (embedded `content=` attribute)
- Images alone can't be convention-linted reliably — if only an image is given, say so and do a best-effort visual review, clearly marked as lower confidence

## Workflow

### Step 1 — Run the lint script (do not eyeball XML)

```bash
python <skill-dir>/scripts/drawio_lint.py <file> [--page <name-or-index>] --pretty
```

It returns JSON with three parts:

1. `findings` — machine-checkable rule violations (`rule`, `severity`, `message`, `elements`)
2. `signals` — raw evidence for the judgment calls the script can't make (color variety, legend presence, C4 level indicators, casing distribution, metadata coverage). **These are not violations.**
3. `stats` — counts used for the summary

### Step 2 — Apply judgment to the signals

The script deliberately does not decide these; you do, because they're contextual:

- **Legend needed?** (`signals.legend`) — if the diagram uses ≥3 fill colors or mixes dashed/solid with different meanings but has no legend box, that's a real finding. If color is purely decorative lane-striping, it isn't — say nothing.
- **Level mixing?** (`signals.c4_levels`) — the classic C4 failure is one canvas showing a Person next to a specific service *and* that service's internal components, or containers side-by-side with the components inside them. Weigh the signals (actors + tech-annotated labels + deep container nesting + container-boundary-crossing edges). If genuinely mixed, name which elements belong to which level and suggest splitting the page.
- **Metadata consistency?** (`signals.metadata`) — the problem isn't "some nodes have `<object>` attributes"; it's *inconsistency*: half the services tagged with an owner and half not, or metadata keys that drift (`tech` vs `technology`). Report drift, not absence, unless the user asked for mandatory metadata.

### Step 3 — Write the review-style Markdown report

Use exactly this structure (rename the title to the file/page):

```markdown
# Diagram review: <file — page name>

## Verdict
One or two sentences: is this publishable, or what must change first?
Counts: 🚨 N errors · ⚠️ N warnings · ℹ️ N notes

## Metadata
Page/layer naming, node metadata consistency. Skip section if clean ("Clean — pages and layers are meaningfully named").

## Naming
Placeholder labels, casing drift, duplicate labels. Show the actual labels.

## Line labels
Unlabeled edges — list them as `source → target`, say what the label should convey
(e.g. "reads/writes? sync or async?"). One unlabeled edge in a 30-edge diagram is a note,
not a warning — calibrate severity to the ratio in `stats`.

## Legend
Only if color/style carries meaning without a key. Say what the colors appear to mean
(so the user can confirm) and what the legend box should contain.

## Abstraction levels
Only if level mixing is real. Show the mixed elements grouped by level,
and recommend the split (e.g. "page 1 = container level, page 2 = component detail of X").

## Structure
Orphan nodes, dangling/floating edges — elements a reader can't place.

## Fix list
Numbered, ordered by impact. Concrete enough to do in draw.io without re-deciding anything:
"Label the 4 edges from Auth Service — start with the Redis one ('session lookup')".
```

Tone: direct but constructive. Quote real labels and IDs so the user can Ctrl-F them in draw.io's editor. Never invent elements that aren't in the file.

## Severity calibration

- 🚨 **error** — the diagram actively misleads: dangling edges, placeholder labels still shipped, level mixing that makes the system look different than it is
- ⚠️ **warning** — a reader will stumble: unlabeled edges that carry semantics, no legend for meaningful colors, casing/naming drift
- ℹ️ **note** — polish: single unlabeled edge, duplicate labels when disambiguated by containers, decorative color without legend

A clean diagram deserves a clean report — do not manufacture findings to seem thorough.

## What NOT to flag

- Visual layout (overlaps, routing, alignment) — out of scope unless the user asks
- Personal style choices with no readability cost
- Things the legend already explains (legend overrides conventions, same as in drawio-understand)

## References

- `references/conventions.md` — full rule catalog: every check, its rationale, and what a good fix looks like. Read it when you're unsure whether something is a violation, or when the user asks "what conventions exactly?".
