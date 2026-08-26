# Convention Lint — onboarding_flow.drawio

File reviewed: `fixtures/onboarding_flow.drawio` (1 page, 5 nodes, 4 edges)

## Summary

The diagram's layout is clean (aligned rows, consistent heights, sensible left-to-right flow), but it breaks several flowchart conventions. The most important problems are a missing decision shape at the branch point, inconsistent label casing, an unsemantic color palette, and a dangling failure path with no end node.

## Findings

### High — semantic / structural issues

1. **Branch point is not a decision shape.** `n-verify` ("Email Verifier") has two labeled outgoing edges ("verified" / "on failure"), but it is a plain rectangle. A node with mutually exclusive conditional branches must be a diamond (`rhombus;whiteSpace=wrap;html=1`). As drawn, readers cannot tell the edges are alternatives.
2. **No end/terminator node.** The flow dead-ends at `n-provision` and `n-notify` with no terminator. Every path in a flowchart should reach an explicit end node (typically a rounded rectangle or ellipse matching the start terminator). `n-notify` in particular is a dangling node with no outgoing edge — it looks unfinished.
3. **Unsemantic color palette.** Five nodes use five unrelated fill colors (`#d5e8d4`, `#dae8fc`, `#ffe6cc`, `#e1d5e7`, `#f8cecc`) from different palette families, with no legend and no meaning. Either use one consistent palette where color encodes something (e.g., green = start, red = failure path, blue = process steps), or drop fills entirely. Right now the colors imply distinctions the diagram doesn't define.

### Medium — naming and label conventions

4. **Inconsistent label casing.** Labels mix four styles: `"Start Here"` (Title Case), `"signup form"` (lowercase), `"Email Verifier"` / `"Account Provisioner"` (Title Case), `"NOTIFY TEAM"` (ALL CAPS). Pick one convention — Title Case ("Sign-Up Form", "Notify Team") is the usual choice. All-caps also reads as shouting.
5. **Edge labels are inconsistent.** `e2` (form → verify) is unlabeled while its siblings carry labels, and `e1`'s label "fills in" describes an actor action rather than the flow (the *user* fills in the form; the edge from Start should be unlabeled or read "submits form"). Branch edges ("verified", "on failure") are good practice — keep those, label the rest deliberately, and make branch conditions exhaustive and parallel in phrasing (e.g., "verified" / "failed", not "verified" / "on failure").
6. **Generic page name.** The diagram page is named `Page-2`, which suggests a leftover scratch page and gives no hint of content. Rename it to something descriptive, e.g., `Onboarding Flow`.

### Low — style polish

7. **Inconsistent node widths.** Widths run 100 / 130 / 140 / 140 / 160 px. Heights are uniformly 50 px (good). Standardize widths (140 px works for all labels) or align them to a grid so the main row reads as a rhythm.
8. **Edge naming convention.** Nodes follow a `n-<name>` convention (`n-start`, `n-form`, …) but edges are bare `e1`–`e4`. For consistency and greppability, name edges after their endpoints, e.g., `e-form-verify`, `e-verify-failure`.
9. **Failure edge styling.** The "on failure" edge (`e4`) is visually identical to the happy path. Consider `dashed=1` (or stroke color matching the failure node) to distinguish error paths from the normal flow.
10. **No explicit arrow style.** Edges rely on the default arrowhead. That's acceptable, but if your team's convention specifies `endArrow=block;rounded=0` (or similar), declare it on every edge so the file is robust against default changes.

## Suggested fixes, in order

1. Change `n-verify` to a decision diamond and keep the two labeled branches.
2. Add end terminators after "Account Provisioner" and "Notify Team" (or a single shared "End").
3. Normalize all labels to Title Case: "Sign-Up Form", "Email Verifier", "Account Provisioner", "Notify Team".
4. Adopt a meaningful color scheme (e.g., blue process rectangles, green start, red/dashed failure branch) and remove the purple/orange one-offs.
5. Rename the page from `Page-2` to `Onboarding Flow`.
6. Equalize node widths, relabel or drop the "fills in" edge label, and rename edges to the `e-<from>-<to>` pattern.
