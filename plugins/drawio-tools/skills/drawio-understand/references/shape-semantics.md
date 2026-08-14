# Shape & style semantics — what draw.io elements mean

Use this to translate draw.io shapes, arrows, and styles into plain English.
When a diagram has a legend or labeled styles, the legend overrides these defaults.

## Vertex shapes

| draw.io style / shape | Friendly name | Usually means |
|---|---|---|
| (default, no shape=) | Rectangle / box | A process, step, or generic component |
| `rounded=1` | Rounded box | A service or soft process (flowcharts: start/end sometimes) |
| `shape=process` | Process box | A processing step with explicit input/output sides |
| `rhombus` | Diamond / decision | A decision point: yes/no branch |
| `ellipse` | Oval / terminator | Flowchart start/end; or a generic node |
| `shape=cylinder`, `cylinder3` | Cylinder | A database or data store |
| `shape=actor`, `umlActor` | Stick figure | A person / user role (not software) |
| `shape=cloud` | Cloud | The internet or an external network |
| `shape=document`, `document2` | Document | A document, report, or file output |
| `shape=note`, `note2` | Note | An annotation, not part of the flow |
| `shape=parallelogram` | Parallelogram | Input or output data (classic flowcharting) |
| `shape=hexagon` | Hexagon | A preparation step or a state |
| `text` (no border) | Text label | Commentary; not a real node |
| `shape=cross` | Cross / X | An end/error terminator |
| `shape=doubleEllipse` | Double circle | A final/accepting state (state machines) |
| `shape=doubleCircle` | Double circle | Final state or emphasized endpoint |

### UML shapes

| Style | Friendly name | Means |
|---|---|---|
| `shape=umlLifeline` | Sequence lifeline | One participant over time in a sequence diagram |
| `shape=umlActor` | Actor | External user or system |
| `shape=class` / `swimlane` w/ `uml...` | Class box | Class with attributes/methods |
| `ellipse` in UML use-case | Use case | A capability the system provides |

### ERD (entity-relationship) shapes

| Style | Means |
|---|---|
| `shape=er...` (`entity`, `rnToOne`...) | Entities and relationship crow's-feet |
| Box with header row | Entity (table); rows are attributes |

### Icon libraries (style starts with `mxgraph.`)

`shape=mxgraph.<library>.<icon>` is a stencil from a shape library. Read the library name as the domain and the icon as the thing:

| Library prefix | Domain |
|---|---|
| `mxgraph.aws4` / `aws3` | Amazon Web Services |
| `mxgraph.azure` | Microsoft Azure |
| `mxgraph.gcp2` / `gcp` | Google Cloud |
| `mxgraph.cisco` (routers, firewalls...) | Network equipment |
| `mxgraph.kubernetes` | K8s pods, services, deployments |
| `mxgraph.lean_mapping`, `mxgraph.electrical`, `mxgraph.networks`, `mxgraph.uml`, `mxgraph.bpmn`, `mxgraph.flowchart` | Self-describing |
| `mxgraph.office.concepts.*` | Neutral concept icons (users, servers, documents) |

The icon half usually names the thing directly (`mxgraph.aws4.lambda_function` → "AWS Lambda function"), so say that; don't force it into a generic category.

## Boundaries / containers

| Style | Friendly name | Usually means |
|---|---|---|
| `swimlane` | Swimlane | One actor's or team's responsibilities (BPMN), or a phase column |
| `swimlane;horizontal=0` | Vertical lane | Same, laid out vertically |
| `shape=pool` / nested swimlanes | Pool | An organization/participant containing lanes |
| `group` (or style containing `group`) | Group | Things selected & grouped together — may be purely visual |
| `container=1` | Container | Custom boundary: VPC, cluster, trust zone, environment |
| `rounded=1;dashed=1` large box | Dashed boundary | A logical/system boundary (common in UML & C4) |
| layer (cell with `parent="0"`, no vertex/edge) | Layer | A toggleable view (e.g. "physical vs logical"); check `visible` |

## Edge (connector) styles

| Style keys | Look | Usually means |
|---|---|---|
| (default, `endArrow=classic`) | Solid arrow → | Direction of flow / request / dependency |
| `dashed=1` | Dashed arrow | Optional, indirect, async, or "planned"; ERD: a non-identifying relation |
| `endArrow=none` | Plain line | Association without direction; UML "uses/knows" |
| `startArrow` + default end | Two-headed | Bidirectional interaction |
| `endArrow=block;endFill=0` | Open triangle | UML dependency / implements (dashed+open = dependency) |
| `endArrow=block` filled + `startArrow=diamondThin` | UML line | Aggregation (empty diamond at the *whole* side) |
| `endArrow=diamond` filled | Filled diamond | Composition (strong ownership) |
| `endArrow=oval` | Hollow circle | UML generalization arrowhead variant / "extends" in use cases |
| `endArrow=open` | Open arrow | Info/query flow (often read-only) |
| `edgeStyle=orthogonalEdgeStyle` | Right angles | Flowchart/architecture routing (visual only — not semantic) |
| `curved=1` | Curved | Visual style only (mind maps) |
| `startFill=0;endFill=0` with `oval` ends | Line with circles | REST/association in some notations — check labels |

**Don't over-interpret routing style** (`edgeStyle`, `curved`, waypoints): those change how a line *looks*, not what it means. Semantics live in arrowheads, dash pattern, color, and the label.

## Color conventions (informal, common)

| Color pattern | Common intent (verify with legend) |
|---|---|
| Green fill | Healthy / success / production-ready |
| Red/orange fill | Failure path, risk, alerting component |
| Blue fill | Default neutral (draw.io default palette) |
| Yellow fill | Warning / external / untrusted |
| Per-lane pastel fills | Differentiating lanes only |
| `fillColor=none` | Abstract/logical grouping (no deployment meaning) |

## Common diagram types & what to emphasize in the walkthrough

| Type | Telltale signs | Walkthrough emphasis |
|---|---|---|
| Flowchart | decisions (`rhombus`), terminators | Follow the main path first, then exception branches |
| Architecture | services + data stores + boundaries | Request journey: client → edge → services → data |
| BPMN process | pools/swimlanes, events (circles) | Who does what, in order, across lanes |
| Sequence | lifelines + horizontal messages | Chronological messages top → bottom |
| ERD | entities + crow's-foot lines | Entities and cardinality (one-to-many...) |
| UML class | class boxes, inheritance arrows | Inheritance vs composition vs dependency |
| Network | `mxgraph.cisco` icons | Traffic path and trust boundaries |
| State machine | rounded states + transitions | Start state, events that move between states, final state |
