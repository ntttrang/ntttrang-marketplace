# Convention catalog — what the lint checks and why

Each rule: ID, severity default, what it catches, why it matters, and what a good fix looks like.
The script handles the mechanical checks (`findings`); judgment rules read `signals`.
Severity may be raised or lowered per diagram — defaults are guidance, context is king.

## Metadata

### META-001 · default page name (⚠️ warning)
Page still called `Page-1`, `Page-2`… — draw.io's default. Tabs are the diagram's table of contents;
in a 5-page file, nobody finds "the deployment view" if it's called Page-3.
**Fix:** rename to what the page shows (`Container view`, `Checkout flow — detail`).

### META-002 · unnamed layers (ℹ️ note, ⚠️ if ≥2 unnamed)
Multi-layer file where layers are named `Layer 1`/their raw id. Layers are toggles —
"show me just the physical view" only works if layers are named after views.
**Fix:** name each layer by what it toggles.

### META-003 · node metadata drift (⚠️ warning, judgment)
draw.io lets you wrap a shape in `<object>` to attach custom attributes (owner, technology, tags…).
The smell is **inconsistency**: half the services carry `owner=`, half don't; or keys drift
(`tech` on one node, `technology` on another). Absence everywhere is a style choice —
drift is an accident. **Fix:** either strip the stray attributes or complete the set.

## Naming

### NAME-001 · placeholder labels (🚨 error)
`New Shape`, `Rectangle`, `Untitled`, `Copy of …`, bare whitespace, or an empty label on a real node.
These ship to production docs more often than anyone admits. **Fix:** name it or delete it.

### NAME-002 · duplicate labels (ℹ️ note)
Two nodes with the identical label and no container to disambiguate. Readers (and tools that
resolve by label — like the sibling inventory script) can't tell them apart. If duplicates sit in
different swimlanes/containers, downgrade or skip: the boundary disambiguates.
**Fix:** qualify one (`Auth Service` → `Auth Service (EU)`), or merge if it's really one thing.

### NAME-003 · casing drift (⚠️ warning, judgment)
Labels mix `API Gateway`, `api-gateway`, `APIGATEWAY` within the same diagram. Not about grammar —
about the reader pattern-matching "same shape of name = same kind of thing". Ignore tech annotations
in `[brackets]`, version suffixes, and acronyms (URL, S3, CI/CD are fine as-is). Only report when
there's a clear dominant style and a meaningful minority deviating (see `signals.naming`).
**Fix:** pick the majority style (usually whatever the codebase/registry uses) and align.

## Line labels

### LINE-001 · unlabeled edges (⚠️ warning / ℹ️ note, calibrated)
An edge with no label. Unlabeled lines are the #1 source of "wait, who calls whom?" in reviews.
Calibrate to the ratio: majority unlabeled → warning per missing edge; a few in a large diagram →
one summary note listing them. Some edges need no label: undirected associations in ERDs,
obvious containment, arrows whose meaning a legend already defines.
**Fix:** say what travels and in what direction — `reads`, `publishes events`, `syncs via cron`.

## Legend

### LEGEND-001 · meaningful colors without a legend (⚠️ warning, judgment)
≥3 distinct fill colors (or dashed-vs-solid with distinct meanings) and no legend box.
Color without a key is private knowledge — the author knows red = external, everyone else guesses.
Not a finding when color is only decorative lane striping or a single accent.
**Fix:** add a small legend box (top-right corner is conventional) mapping each color/style to meaning.

## Abstraction levels (C4)

### LEVEL-001 · mixed abstraction levels (🚨 error, judgment)
One canvas mixing C4 zoom levels. Classic patterns:
- a Person (context level) wired directly to a component inside a container (detail level)
- containers and their own internal components both appearing as peers
- tech-annotated labels (`[Node.js]`) — a container-level convention — on blobs next to raw actors
The diagram lies about the system's shape: everything looks equally important and no boundary is visible.
**Fix:** split into pages per level (page 1: container view; page 2: component detail of the hot spot),
or drop the out-of-place elements. See `signals.c4_levels` for the evidence to weigh.

## Structure

### STRUC-001 · dangling edge (🚨 error)
Edge whose `source` or `target` points to a cell that doesn't exist — usually a deleted node.
Renders as an arrow to nowhere or silently vanishes. **Fix:** reconnect or delete the edge.

### STRUC-002 · floating edge (🚨 error)
Edge with no endpoints at all. **Fix:** connect it or remove it.

### STRUC-003 · orphan node (⚠️ warning / ℹ️ note)
Node with no connections. Sometimes intentional (a legend, a parked component, a title) —
notes and labels are exempt. **Fix:** connect it, or move it to a "parking" area with a note saying why.

## Severity quick reference

| Severity | Meaning |
|---|---|
| 🚨 error | Misleads the reader; fix before sharing |
| ⚠️ warning | Reader will stumble; fix soon |
| ℹ️ note | Polish; fix when convenient |
