# Convention Review: checkout_flow_clean.drawio

**Diagram:** Checkout Flow (`fixtures/checkout_flow_clean.drawio`)
**Scope:** 6 nodes (Customer, Cart Service, Payment Service, Orders DB, Fraud Check, Legend), 4 edges.
**Overall verdict:** Clean — no blocking convention violations. The diagram is internally consistent with its own legend, and naming/labeling conventions are applied uniformly. Two minor observations below, neither of which requires a fix to call this diagram conformant.

## Checks performed

| # | Check | Result |
|---|-------|--------|
| 1 | Node ID naming (`n-` prefix, semantic names: `n-start`, `n-cart`, `n-pay`, `n-db`, `n-fraud`, `n-legend`) | Pass — consistent |
| 2 | Every edge has both `source` and `target`, no dangling refs | Pass — all 4 edges resolve to existing nodes |
| 3 | Every edge is labeled (`adds items`, `submits order`, `writes order`, `validates`) | Pass — no unlabeled connections |
| 4 | Fill colors match the legend's declared scheme (blue = service, green = data store, yellow = decision) | Pass — `#dae8fc` services, `#d5e8d4` data store, `#fff2cc` decision; legend `#f5f5f5` note is neutral |
| 5 | Shape semantics match node roles (actor for Customer, cylinder for DB, rhombus for decision, rounded rect for services, note for legend) | Pass |
| 6 | Overlapping nodes or intersecting bounding boxes | Pass — no overlaps; legend does not collide with the Fraud Check diamond (x 640 vs. diamond ending at x 530) |
| 7 | Grid alignment (coordinates on 10px grid) | Pass — all geometry values are multiples of 10 |
| 8 | Orphan nodes | Pass — every shape is connected, except the Legend which is decorative by design |

## Minor observations (non-blocking)

1. **Decision node has no outgoing branches.** `n-fraud` ("Fraud Check", the yellow decision per the legend) only receives edge `e4` ("validates") and emits no edges. Flowchart convention expects a decision to branch with labeled outcomes (e.g., `pass` / `flag for review`). If this diagram is meant to be complete, add at least one labeled outgoing edge from the diamond; if the fraud outcome is intentionally out of scope, this is fine as is.
2. **Slightly uneven horizontal rhythm.** Gaps between the main-row shapes are 100px (Customer → Cart Service) then 80px (Cart Service → Payment Service, Payment Service → Orders DB). Harmonizing to a single gap would tighten the layout, but this is cosmetic.

## Notes

- `n-db` (Orders DB) sits at y=110 with height 70, so its vertical center (145) is 5px above the row center of the other nodes (150). This is the usual visual correction for cylinder shapes and is not counted as an issue.
- Edge IDs use a bare numeric scheme (`e1`–`e4`) while node IDs are semantic (`n-pay`). The two schemes coexist cleanly; renaming edges to semantic IDs would only matter if a stricter ID convention is adopted team-wide.

**Recommendation:** Accept as-is. Optionally address observation 1 if the fraud-check branch is meant to be modeled.
