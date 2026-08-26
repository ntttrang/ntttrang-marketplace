# Convention Lint Review — `messy_architecture.drawio`

Reviewed file: `fixtures/messy_architecture.drawio` (1 page, 1 layer, 10 nodes, 5 edges)
Scope: metadata, naming, line labels, legend, abstraction levels, edges, layout/structure.

**Verdict: Not ready to share.** 4 blockers (broken/dangling edges, placeholder node, level mixing) should be fixed first; the rest are consistency issues that will generate questions from readers.

Severity scale: **BLOCKER** (wrong or misleading), **MAJOR** (will confuse readers), **MINOR** (polish).

---

## 1. Blockers

| # | Severity | Location | Issue | Fix |
|---|----------|----------|-------|-----|
| B1 | BLOCKER | edge `e3` (`n-auth` → `n-deleted-long-ago`) | Edge targets a node that does not exist anywhere in the file (`n-deleted-long-ago`). This is a dangling reference to a deleted element — the edge will not render or attach, and the export may drop it silently. | Delete `e3`, or re-point it at the intended current node. |
| B2 | BLOCKER | edge `e4` | Edge with neither `source` nor `target` — a floating, unconnected edge. Pure leftover noise; conveys nothing. | Delete `e4`. |
| B3 | BLOCKER | node `n-placeholder` ("New Shape") | Untouched default placeholder label shipped in the diagram. Readers cannot tell whether it is a real component, a TODO, or an accident. | Rename to the actual component, or delete it. |
| B4 | BLOCKER | abstraction levels, whole canvas | Three abstraction levels are mixed on one page: a **person/actor** (context level: `Customer`), **containers** (`API Gateway`, `auth-service`, `Main DB`, `Redis Cache`), and **components inside a container** (`Request Router`, `token validator`). One page should sit at a single abstraction level (per C4 or similar convention): either a container-level diagram, or a component diagram of one container — not both. | Split into two pages: a container diagram (Customer → API Gateway / auth-service / DB / Cache) and a component diagram of the API Gateway (Router, Validator). |
| B5 | BLOCKER | edge `e5` (`c-router` → `n-validator`) | An edge from a **container to a node nested inside that same container**. A whole→part connection is meaningless as a data/control flow, and even if intended (e.g. "exposes"), it is drawn as an ordinary edge. This is also a level-skipping edge (container → component) while other edges connect container→container. | Delete `e5`. If the intent is "API Gateway contains the validator", containment already shows that. |

## 2. Metadata

| # | Severity | Location | Issue | Fix |
|---|----------|----------|-------|-----|
| M1 | MAJOR | `n-api` vs `n-auth` | Metadata **key drift**: `n-api` uses `technology="Node.js"` and adds `owner="team-a"`; `n-auth` uses `tech="Go"` and has no owner. Same concept, two key names (`technology` / `tech`), and inconsistent coverage (1 of 10 nodes has an owner). | Pick one schema per key name (`technology`, `owner`) and apply it to every node — or to none, if you don't want metadata at all. |
| M2 | MAJOR | `n-api` label "API Gateway [Node.js]" | Technology is duplicated: embedded in the label `[Node.js]` AND present as a `technology` attribute. When they drift apart (this is how drift starts) readers won't know which is current. | Keep technology in metadata only, or in the label only — consistently, for all nodes. |
| M3 | MINOR | `<diagram name="Page-1">` | Default page name. In a shared document this says nothing about content. | Rename to the diagram's purpose, e.g. `System context` / `Container view`. |
| M4 | MINOR | layer `layer-1` ("Layer 1") | Default-named layer, and the only layer — so the layer is not doing any organizational work. | Either remove the custom layer or give it a meaningful name (e.g. `Runtime`). |
| M5 | MINOR | whole file | No title or description element for the diagram itself; the reader learns nothing about what view this is (context / deployment / runtime?). | Add a title shape ("X — Container Diagram, v?, date") or at least set the page name (M3). |

## 3. Naming

| # | Severity | Location | Issue | Fix |
|---|----------|----------|-------|-----|
| N1 | MAJOR | `n-api` ("API Gateway") vs `c-router` ("API Gateway") | Two different elements with the **identical label** — and one is a container that visually contains the other level's components. Readers will reasonably conclude the container *is* the gateway, making the standalone `n-api` node a duplicate. | Disambiguate: keep "API Gateway" for one of them; the container should be labeled as what it is (e.g. "API Gateway (components)" — or just resolved by B4's split). |
| N2 | MAJOR | `n-cache1`, `n-cache2` | Two nodes both labeled "Redis Cache". Either an accidental duplicate, or two real instances — but nothing distinguishes them (no suffix, no metadata, different positions only). | If duplicate: delete one. If two instances: name them by role, e.g. "Redis Cache (sessions)" / "Redis Cache (jobs)", or one node + a note. |
| N3 | MAJOR | all node labels | **Casing convention drift** across four different styles: `API Gateway` / `Main DB` (Title + acronym), `auth-service` (kebab-case), `token validator` / `request router` style lowercase, `Request Router` (Title Case), `Customer` (Title). | Pick one label style (e.g. Title Case for display names) and apply everywhere: `Auth Service`, `Token Validator`. |
| N4 | MINOR | `n-db` ("Main DB") | Abbreviation "DB" while other labels are spelled out; "Main" is vague (main what?). | "Primary Database" or name it by engine/role, e.g. "PostgreSQL (primary)". |
| N5 | MINOR | node IDs | IDs mix conventions (`n-api`, `c-router`, `n-cache1`, `e1`). Minor since IDs are invisible to readers, but the `n-`/`c-` prefix is applied inconsistently (`c-router` is a container holding nodes — fine — but `n-router` also exists, easy to confuse). | Optional: keep the `n-`/`c-`/`e-` prefixes but make them unambiguous. |

## 4. Line (edge) labels

| # | Severity | Location | Issue | Fix |
|---|----------|----------|-------|-----|
| L1 | MAJOR | `e1`, `e2` (and the dangling `e3`) | **No edge in the entire diagram has a label.** `e3` even carries an explicit empty `value=""`. Readers can't tell what flows: "Customer → API Gateway" is it HTTP? a request? "API Gateway → auth-service" — calls, validates tokens, forwards? | Label every edge with the interaction, ideally "verb / protocol", e.g. `e1`: "HTTPS requests", `e2`: "validates tokens via gRPC". |
| L2 | MINOR | all edges | All edges use identical default arrows — no visual distinction between synchronous calls, async messages, or reads/writes. Not required, but with a legend this adds a lot of meaning cheaply. | Consider line styles (solid = sync, dashed = async) **and then document them in the legend** (see G1). |

## 5. Legend & visual language

| # | Severity | Location | Issue | Fix |
|---|----------|----------|-------|-----|
| G1 | MAJOR | whole canvas | **No legend exists.** The diagram uses at least 4 fill colors, 2 shapes, and a dashed style with no key anywhere. | Add a small legend box mapping color/shape/style → meaning (see G2/G3 for what it must explain). |
| G2 | MAJOR | fill colors | Colors carry no consistent meaning: `#dae8fc` (blue) is used for a top-level container (`n-api`) *and* for nested components (`n-router`, `n-validator`) — the same color at two abstraction levels; `#f8cecc` (draw.io's "problem" red) is used for both the placeholder node *and* the database; `#d5e8d4` (green) appears once; the two Redis caches have no fill at all (default). | Define one color per concept/level (e.g. blue = gateway tier, green = services, purple = data stores) and apply uniformly; reserve red for warnings only. |
| G3 | MINOR | `c-router` style | `dashed=1` on the container is unexplained — does dashed mean "logical boundary"? "planned"? Readers will guess. | Either remove the dash or explain it in the legend. |
| G4 | MINOR | shapes | Actor, rounded rectangles, and cylinders are used — good instinct (cylinder = datastore), but nothing states it. | One line in the legend: cylinder = data store, actor = person, rectangle = software. |

## 6. Structure / layout

| # | Severity | Location | Issue | Fix |
|---|----------|----------|-------|-----|
| S1 | MAJOR | `n-router`, `n-validator` geometry | These nodes are parented to container `c-router` (at x=640, y=40) but carry what look like **absolute canvas coordinates** (x=660, y=160). Child geometry in draw.io is relative to the parent, so they will actually render around (1300, 100)–(1300, 180) — far outside their container (which spans 640–940). The "components inside the gateway" will not appear inside it at all. | Re-parent with relative coordinates (e.g. x=20, y=40 within the container), or drop the parenting and position them manually. |
| S2 | MINOR | `e1` style | Only `e1` sets `edgeStyle=orthogonalEdgeStyle`; the other edges use default (straight) routing. Mixed edge routing looks accidental. | Pick one routing style for the whole diagram. |

---

## Summary

| Category | Blocker | Major | Minor |
|---|---|---|---|
| Edges (dangling/floating/labels) | 3 (B1, B2, B5) | 1 (L1) | 2 (L2, S2) |
| Abstraction levels | 1 (B4) | — | — |
| Metadata | — | 2 (M1, M2) | 3 (M3, M4, M5) |
| Naming | — | 3 (N1, N2, N3) | 2 (N4, N5) |
| Legend / visual language | — | 2 (G1, G2) | 2 (G3, G4) |
| Layout / structure | — | 1 (S1) | — |
| **Total** | **4** | **9** | **9** |

### Suggested fix order
1. Delete/repair broken edges: `e3` (dangling), `e4` (floating), `e5` (container → own child). (B1, B2, B5)
2. Resolve or delete the "New Shape" placeholder. (B3)
3. Decide the abstraction level and split pages if needed. (B4, N1)
4. Fix container-child coordinates so components render inside the gateway container. (S1)
5. Resolve the duplicate "Redis Cache" nodes. (N2)
6. Normalize metadata keys and casing; unify where technology lives. (M1, M2, N3)
7. Label all remaining edges. (L1)
8. Add a legend and align the color scheme. (G1, G2)
9. Rename page/layer, add a title. (M3, M4, M5)
