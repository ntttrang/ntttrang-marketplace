# Diagram review: messy_architecture.drawio — Page-1

## Verdict

Not ready to share. The page mixes context, container, and component abstractions on one canvas, has a dangling edge pointing at a deleted node, a floating edge with no endpoints, and 5/5 edges carry no label — a teammate reading this cannot tell what talks to what, or how. Fix the structural errors and the level split first; the rest is cleanup.

Counts: 🚨 4 errors · ⚠️ 6 warnings · ℹ️ 4 notes

## Metadata

- ⚠️ **Page name** — the page is still called `Page-1`. Rename it to what it shows (e.g. "Checkout — container view").
- ℹ️ **Layer name** — the single layer is `layer-1` with the label "Layer 1". With only one layer this is cosmetic, but name it after the view it toggles if you keep it.
- ⚠️ **Metadata key drift** — 2 of 10 nodes carry metadata, and they don't agree on keys: `n-api` uses `owner="team-a"` + `technology="Node.js"`, while `n-auth` uses `tech="Go"` (and no owner). Pick one schema (`tech` or `technology`, plus owner) and apply it to all services or none — right now it reads as "team-a documents their stuff, everyone else doesn't."

## Naming

- 🚨 **Placeholder label shipped** — node `n-placeholder` (id `n-placeholder`) still says "New Shape", styled in the same red as `Main DB`. Either name it or delete it; a placeholder in a shared diagram reads as unfinished work.
- ⚠️ **Two different elements named "API Gateway"** — the container-level node `n-api` is labeled `API Gateway [Node.js]` while the dashed container `c-router` around `Request Router` / `token validator` is labeled `API Gateway`. A reader can't tell whether these are the same thing shown twice or two different gateways. Name the container distinctly (e.g. "API Gateway — internal components") or, better, see the abstraction-level fix below.
- ⚠️ **Casing drift** — 7 labels are Title Case (`Customer`, `Main DB`, `Request Router`) but 2 are lower case: `auth-service` (kebab-case) and `token validator`. Pick one convention for service names — `Auth Service` / `Token Validator` if you keep Title Case, or `auth-service` / `request-router` if kebab-case is your standard.
- ℹ️ **Duplicate labels without a container** — `n-cache1` and `n-cache2` are both labeled `Redis Cache` at the same nesting level. If they're genuinely two caches, disambiguate (`Session Cache` / `Rate-limit Cache`); if not, delete one.

## Line labels

- ⚠️ **All 5 edges are unlabeled (5/5, 100%)** — every relationship on the page is a bare line:

  - `Customer → API Gateway [Node.js]` — what does the customer do? `HTTP requests` / `uses`?
  - `API Gateway [Node.js] → auth-service` — sync call or async event? `validates token via`?
  - `API Gateway → token validator` (edge `e5`, see Structure) — what flows between them?

  Minimum viable fix: label each edge with the interaction — verb + protocol (`HTTPS`, `gRPC`, `publishes to Kafka`). A reader six months from now should never have to guess sync vs async.

## Legend

- ⚠️ **4 fill colors, no legend** — the page uses `#ffe6cc` (Customer), `#dae8fc` (API Gateway, Request Router, token validator), `#d5e8d4` (auth-service), `#f8cecc` (New Shape, Main DB) with no key. The colors *appear* to mean: orange = actor/person, blue = gateway + its components, green = backend service, red = …placeholder and database? That's the problem — red groups a placeholder with a data store, and green vs blue is unclear (is `auth-service` not part of the gateway tier?). Add a legend box stating what each color means, or stop color-coding. Once `New Shape` is deleted, decide whether the remaining three colors earn their keep.

## Abstraction levels

- 🚨 **Three C4 levels on one canvas**:
  - **Context level:** `Customer` (`n-actor`, actor shape)
  - **Container level:** `API Gateway [Node.js]` (`n-api`), `auth-service` (`n-auth`), `Main DB` (`n-db`), the two `Redis Cache` nodes
  - **Component level:** `Request Router` (`n-router`) and `token validator` (`n-validator`) inside the dashed `API Gateway` container (`c-router`)

  The diagram shows the API Gateway twice — once as a peer of auth-service and once exploded into its internal components — so a reader can't tell whether `Request Router` is a deployable thing or a module inside the gateway. **Split into two pages:** page 1 = container view (Customer → API Gateway → auth-service → Main DB / Redis Cache), page 2 = "API Gateway — component detail" containing Request Router and token validator. The tech annotation `[Node.js]` on the container-level node confirms page 1 is meant to be container level.

## Structure

- 🚨 **Dangling edge `e3`** — `auth-service → n-deleted-long-ago`. The target node no longer exists, so the edge renders as a line into nothing and silently implies auth-service talks to *something*. Delete the edge or restore the node.
- 🚨 **Floating edge `e4`** — no source, no target. It's a stray line on the canvas; delete it.
- ℹ️ **Five unconnected nodes** — `n-placeholder` (New Shape), `n-db` (Main DB), `n-router` (Request Router), `n-cache1` and `n-cache2` (Redis Cache) have no edges. A Main DB and two caches nothing reads from will raise eyebrows in review — either the edges are missing or the nodes are stale.
- ℹ️ **Edge `e5` connects a container to its own child** — `c-router` (the "API Gateway" container) → `n-validator` (token validator, *inside* `c-router`). An edge from a boundary to its own contents is degenerate; it should connect `Request Router → token validator` (or whatever the real relationship is). This disappears with the level split above.

## Fix list

1. Delete or reconnect the broken edges: `e3` (dangling, target `n-deleted-long-ago`) and `e4` (floating).
2. Delete the placeholder node `n-placeholder` ("New Shape") or give it a real name.
3. Split levels into two pages: container view on page 1, "API Gateway — component detail" (`Request Router`, `token validator`) on page 2. Remove the duplicate `API Gateway` container/name conflict.
4. Label all remaining edges — start with `Customer → API Gateway` ("HTTPS requests") and `API Gateway → auth-service` (sync/async?).
5. Add the missing data-store edges: `auth-service → Main DB`, and connect whichever `Redis Cache` is real (and delete the duplicate).
6. Add a legend box defining the fill colors — or drop color-coding that doesn't carry meaning.
7. Unify metadata: pick `tech` or `technology` (and add `owner`) and apply the same schema to all service nodes.
8. Normalize casing across labels (`auth-service`, `token validator` vs. everything else).
9. Rename the page from `Page-1` to something descriptive, and name the layer if you keep it.
