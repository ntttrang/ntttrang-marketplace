# Diagram review: onboarding_flow.drawio — Page-2

## Verdict
Not publishable yet. Nothing here is actively misleading (no dangling edges, no placeholders), but the page still looks like a draft: it carries a default page name, three different label casings, five unexplained fill colors, and one of the four edges has no label. All four issues are five-minute fixes.
Counts: 🚨 0 errors · ⚠️ 4 warnings · ℹ️ 0 notes

## Metadata
- The page is named `Page-2` (default name). Rename it to what it shows, e.g. "Onboarding Flow".

## Naming
Label casing drifts across three styles within five nodes:

- Title case: `Start Here`, `Email Verifier`, `Account Provisioner`
- lower case: `signup form` (`n-form`)
- ALL CAPS: `NOTIFY TEAM` (`n-notify`)

Pick one convention (Title case or sentence case is typical for flow steps) and apply it to all five. The ALL-CAPS `NOTIFY TEAM` in particular reads like a leftover emphasis hack — if that step is meant to stand out, encode that in the shape or the legend, not the casing.

## Line labels
Three of the four edges are labeled (`fills in`, `verified`, `on failure`); one carries no label:

- `signup form → Email Verifier` (edge `e2`) — what actually happens here? Does the user submit the form and the system sends a verification email, or does the form hand off to the verifier directly? Something like "sends verification email" or "submits for verification" closes the gap.

With 1 of 4 edges unlabeled (25%), this is a warning, not a note — the one silent edge is the central handoff of the flow.

## Legend
The diagram uses five distinct fill colors — every node a different one (`#d5e8d4`, `#dae8fc`, `#ffe6cc`, `#e1d5e7`, `#f8cecc`) — and there is no legend. If each color means something (e.g. user action vs. system step vs. error path — the red `NOTIFY TEAM` and the green `Start Here` suggest it might), readers can't know that; if it doesn't, the rainbow palette invites them to guess. Either:

1. Add a small legend box stating what each color encodes, or
2. Collapse to a neutral palette with color reserved for the one distinction that matters (e.g. red for the failure path).

## Abstraction levels
Clean — all five nodes sit at the same step-level abstraction; no C4-style level mixing.

## Structure
Clean — no orphan nodes or dangling edges; every node is connected.

## Fix list
1. Rename the page from `Page-2` to something meaningful ("Onboarding Flow").
2. Normalize the five node labels to one casing — change `signup form` → `Signup Form` and `NOTIFY TEAM` → `Notify Team` (IDs `n-form`, `n-notify`).
3. Label edge `e2` (`signup form → Email Verifier`) with what the handoff is, e.g. "sends verification email".
4. Resolve the color question: add a legend explaining the five fills, or simplify the palette so color only marks the failure path (`Email Verifier → NOTIFY TEAM`).
