#!/usr/bin/env python3
"""Lint a draw.io file against diagram conventions.

Mechanical checks (placeholders, unlabeled edges, default names, dangling edges...)
become `findings`. Context-dependent judgments (legend needed? C4 level mixing?
metadata drift? casing drift?) are left to the reviewer: the script only emits
`signals` — raw evidence — and `stats`.

Usage:
  python drawio_lint.py <file> [--page <name-or-index>] [--pretty]
  python drawio_lint.py <file> -o lint.json
"""

import argparse
import base64
import html
import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib


def decode_compressed(text: str) -> str:
    """Decode draw.io's compressed diagram payload: base64 -> raw inflate -> percent-decode."""
    try:
        raw = base64.b64decode(text.strip(), validate=False)
        xml_text = zlib.decompress(raw, -zlib.MAX_WBITS).decode("utf-8")
        return urllib.parse.unquote(xml_text)
    except Exception:
        return ""


def style_dict(style: str) -> dict:
    """Parse a style string like 'rounded=1;whiteSpace=wrap;swimlane;' into a dict.

    Bare keys (no '=') map to an empty-string value — e.g. 'swimlane' means shape=swimlane.
    """
    d = {}
    for part in (style or "").split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            d[k.strip()] = v.strip()
        else:
            d[part] = ""
    return d


def clean_label(value: str) -> str:
    """Turn a label (possibly containing HTML like <br>, <b>, &nbsp;) into plain text."""
    if not value:
        return ""
    text = html.unescape(value)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


SHAPE_KINDS = [
    (lambda s: "swimlane" in s, "swimlane"),
    (lambda s: "group" in s, "group"),
    (lambda s: s.get("shape", "").startswith("cylinder"), "database"),
    (lambda s: s.get("shape") == "rhombus" or "rhombus" in s, "decision"),
    (lambda s: s.get("shape") == "parallelogram" or "parallelogram" in s, "input-output"),
    (lambda s: s.get("shape") == "ellipse" or "ellipse" in s, "ellipse"),
    (lambda s: s.get("shape") in ("actor", "umlActor"), "actor"),
    (lambda s: s.get("shape") in ("note", "note2"), "note"),
    (lambda s: s.get("shape", "").startswith("mxgraph.flowchart.document2")
     or s.get("shape", "") == "document", "document"),
    (lambda s: s.get("shape", "").startswith("mxgraph."), "icon"),
    (lambda s: "text" in s, "label"),
    (lambda s: s.get("shape", "").startswith("umlLifeline"), "uml-lifeline"),
    (lambda s: True, "box"),
]


def classify_vertex(s: dict) -> str:
    for test, kind in SHAPE_KINDS:
        if test(s):
            return kind
    return "box"


def load_models(path: str):
    """Return a list of (page_name, mxGraphModel Element) from any supported file."""
    with open(path, "rb") as f:
        data = f.read()

    pages = []
    if path.lower().endswith(".svg") or b"<svg" in data[:2000]:
        m = re.search(rb'content="([^"]+)"', data)
        if not m:
            raise SystemExit("SVG file has no embedded draw.io content= attribute")
        decoded = decode_compressed(html.unescape(m.group(1).decode("utf-8", "replace")))
        if not decoded.strip().startswith("<"):
            raise SystemExit("Could not decode the SVG's embedded content attribute")
        pages.append(("svg-embedded", ET.fromstring(decoded)))
        return pages

    tree = ET.fromstring(data)
    tag = tree.tag if isinstance(tree.tag, str) else ""

    if tag == "mxGraphModel":
        pages.append(("page-1", tree))
    elif tag == "mxfile":
        for i, diag in enumerate(tree.findall("diagram")):
            name = diag.attrib.get("name", f"page-{i + 1}")
            inner = diag.find("mxGraphModel")
            if inner is not None:
                pages.append((name, inner))
            elif (diag.text or "").strip():
                decoded = decode_compressed(diag.text)
                if decoded.strip().startswith("<"):
                    pages.append((name, ET.fromstring(decoded)))
                else:
                    print(f"warning: could not decode page '{name}'", file=sys.stderr)
            else:
                print(f"warning: page '{name}' is empty", file=sys.stderr)
    else:
        raise SystemExit(f"Unrecognized root element <{tag}> — is this a draw.io file?")
    return pages


def parse_cells(model: ET.Element):
    """Walk one mxGraphModel's <root> and return nodes, edges, containers, layers."""
    root = model.find("root")
    if root is None:
        return [], [], [], {}

    cells = {}
    order = []
    for el in root:
        obj = {}
        cell_el = el
        if el.tag in ("object", "UserObject"):
            obj["metadata"] = {k: v for k, v in el.attrib.items() if k not in ("label", "id")}
            cell_el = el.find("mxCell")
            if cell_el is None:
                continue
            obj["label_attr"] = el.attrib.get("label", "")
        # draw.io puts the id on the <mxCell>, but hand-written files sometimes
        # put it on the <object> wrapper instead — accept either
        cid = cell_el.attrib.get("id") or el.attrib.get("id")
        if cid is None:
            continue
        obj["id"] = cid
        obj["element"] = cell_el
        cells[cid] = obj
        order.append(cid)

    nodes, edges, containers, layers = [], [], [], []
    for cid in order:
        el = cells[cid]["element"]
        attrs = el.attrib
        style = style_dict(attrs.get("style", ""))
        label = clean_label(attrs.get("value", "") or cells[cid].get("label_attr", ""))
        parent_id = attrs.get("parent")

        if attrs.get("vertex") == "1":
            entry = {
                "id": cid, "label": label, "kind": classify_vertex(style),
                "parent": parent_id, "style": style,
                "metadata": cells[cid].get("metadata", {}),
            }
            if entry["kind"] in ("swimlane", "group") or style.get("container") == "1":
                entry["container_kind"] = entry["kind"]
                containers.append(entry)
            else:
                nodes.append(entry)
        elif attrs.get("edge") == "1":
            edges.append({
                "id": cid, "label": label,
                "source": attrs.get("source"), "target": attrs.get("target"),
                "parent": parent_id, "style": style,
            })
        elif parent_id == "0":
            layers.append({"id": cid,
                           "label": clean_label(attrs.get("value", "")) or "",
                           "visible": attrs.get("visible", "1") != "0"})
    return nodes, edges, containers, layers, cells


PLACEHOLDER_RE = re.compile(
    r"^(new (shape|rectangle|ellipse|box|arrow|text)( \d+)?|untitled( \d+)?|"
    r"copy of .*|rectangle|ellipse|shape|text|todo.*|tbd.*|fixme.*|xxx.*)$", re.I)


def label_casing(label: str) -> str:
    """Coarse casing bucket for a label, ignoring [tech] annotations and trailing digits."""
    core = re.sub(r"\[[^\]]*\]", "", label).strip()
    core = re.sub(r"\b(v?\d+([.\d]*)*)\b", "", core).strip(" -_")
    if not core or not any(c.isalpha() for c in core):
        return ""
    letters = [c for c in core if c.isalpha()]
    if all(c.isupper() for c in letters):
        return "UPPER"
    if letters[0].islower():
        return "lower"
    if "-" in core and not core.startswith("-"):
        return "kebab"
    if "_" in core:
        return "snake"
    return "Title"


def lint_page(page_name: str, model: ET.Element):
    nodes, edges, containers, layers, cells = parse_cells(model)
    findings = []

    def add(rule, severity, message, elements=None):
        findings.append({"rule": rule, "severity": severity, "message": message,
                         "elements": elements or []})

    vertex_ids = {n["id"] for n in nodes} | {c["id"] for c in containers}

    # ---- Metadata: page name ----
    if re.fullmatch(r"page[- ]?\d+", page_name, re.I):
        add("META-001", "warning", f"Page uses a default name '{page_name}' — rename it "
            "to what the page shows", [page_name])

    # ---- Metadata: layer names ----
    real_layers = [l for l in layers if l["id"] not in ("0", "1")]
    unnamed = [l for l in real_layers
               if not l["label"] or re.fullmatch(r"layer[- ]?\d*", l["label"], re.I)]
    if real_layers and unnamed:
        sev = "warning" if len(unnamed) >= 2 else "note"
        add("META-002", sev, f"{len(unnamed)}/{len(real_layers)} layers unnamed "
            "(multi-layer files should name each layer after the view it toggles)",
            [l["id"] for l in unnamed])

    # ---- Naming: placeholders ----
    for n in nodes:
        if n["kind"] in ("label", "note"):
            continue
        if not n["label"]:
            add("NAME-001", "error", f"Node {n['id']} has no label at all", [n["id"]])
        elif PLACEHOLDER_RE.match(n["label"]):
            add("NAME-001", "error", f"Node '{n['label']}' ({n['id']}) still has a "
                "placeholder name", [n["id"]])
        elif n["label"] != n["label"].strip() or "  " in n["label"]:
            add("NAME-001", "note", f"Label '{n['label']}' has stray whitespace", [n["id"]])

    # ---- Naming: duplicates ----
    by_label = {}
    for n in nodes:
        if n["label"]:
            by_label.setdefault(n["label"], []).append(n)
    for label, group in sorted(by_label.items()):
        if len(group) > 1 and label.lower() not in ("legend",):
            parents = {g["parent"] for g in group}
            disambiguated = len(parents) == len(group) and None not in parents
            if not disambiguated:
                add("NAME-002", "note", f"{len(group)} nodes share the label '{label}' with "
                    "no container to disambiguate", [g["id"] for g in group])

    # ---- Line labels ----
    unlabeled = []
    for e in edges:
        if not e["label"]:
            unlabeled.append(e)
    for e in unlabeled:
        s = next((n["label"] for n in nodes + containers if n["id"] == e["source"]), "?")
        t = next((n["label"] for n in nodes + containers if n["id"] == e["target"]), "?")
        e["unlabeled_desc"] = f"{s or '(unlabeled)'} → {t or '(unlabeled)'}"

    # ---- Structure ----
    connected = set()
    for e in edges:
        connected.add(e["source"])
        connected.add(e["target"])
        if (e["source"] and e["source"] not in vertex_ids) or \
           (e["target"] and e["target"] not in vertex_ids):
            add("STRUC-001", "error", f"Edge '{e['label'] or e['id']}' points to a "
                "non-existent cell (deleted node?)", [e["id"]])
        if e["source"] is None and e["target"] is None:
            add("STRUC-002", "error", f"Edge '{e['label'] or e['id']}' is floating "
                "(no endpoints)", [e["id"]])
    for n in nodes:
        if n["kind"] in ("label", "note"):
            continue
        if n["id"] not in connected:
            add("STRUC-003", "note", f"Node '{n['label'] or n['id']}' has no connections", [n["id"]])

    # ===== Signals (evidence for judgment calls — NOT violations) =====

    # Legend presence
    has_legend = any("legend" in (n["label"] or "").lower() for n in nodes + containers)
    fills = {}
    for n in nodes:
        f = n["style"].get("fillColor", "")
        if f and f not in ("none", "#dae8fc;stroke=#6c8ebf", "#ffffff"):
            fills.setdefault(f, []).append(n["label"] or n["id"])
    dashed = sum(1 for e in edges if e["style"].get("dashed") not in (None, "0", "false"))

    # Casing distribution (labels with real words only)
    casings = {}
    for n in nodes:
        if n["kind"] in ("label", "note") or not n["label"]:
            continue
        bucket = label_casing(n["label"])
        if bucket:
            casings.setdefault(bucket, []).append(n["label"])

    # Metadata coverage & key drift
    with_meta = [n for n in nodes + containers if n["metadata"]]
    all_meta_keys = {}
    for n in with_meta:
        for k in n["metadata"]:
            all_meta_keys.setdefault(k, set()).add(n["id"])
    similar = []
    keys = list(all_meta_keys)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if a != b and (a in b or b in a or a.replace("-", "") == b.replace("-", "")):
                similar.append((a, b))

    # C4 level indicators
    def depth(node):
        d, p = 0, node.get("parent")
        seen = set()
        while p and p in vertex_ids and p not in seen:
            d += 1
            seen.add(p)
            p = next((c["parent"] for c in containers if c["id"] == p), None)
        return d

    tech_annotated = [n["label"] for n in nodes + containers
                      if n["label"] and re.search(r"\[[^\]]{2,}\]", n["label"])]
    actors = [n["label"] or n["id"] for n in nodes if n["kind"] == "actor"]
    datastores = [n["label"] or n["id"] for n in nodes if n["kind"] == "database"]
    container_ids = {c["id"] for c in containers}
    deep_nodes = [n["label"] or n["id"] for n in nodes if depth(n) >= 2]
    boundary_crossing = 0
    for e in edges:
        s_in = e["source"] in container_ids
        t_in = e["target"] in container_ids
        # container -> node nested inside another container = level skip
        if (s_in or t_in) and e["source"] in vertex_ids and e["target"] in vertex_ids:
            s_parent = next((n["parent"] for n in nodes + containers if n["id"] == e["source"]), None)
            t_parent = next((n["parent"] for n in nodes + containers if n["id"] == e["target"]), None)
            if (s_in and t_parent in container_ids and t_parent != e["source"]) or \
               (t_in and s_parent in container_ids and s_parent != e["target"]):
                boundary_crossing += 1

    signals = {
        "legend": {
            "present": has_legend,
            "distinct_fill_colors": len(fills),
            "fill_usage": {k: v[:5] for k, v in fills.items()},
            "dashed_edges": dashed,
            "solid_edges": len(edges) - dashed,
        },
        "naming": {
            "casing_distribution": {k: {"count": len(v), "examples": v[:4]} for k, v in casings.items()},
        },
        "metadata": {
            "nodes_total": len(nodes) + len(containers),
            "nodes_with_metadata": len(with_meta),
            "metadata_keys": {k: len(v) for k, v in all_meta_keys.items()},
            "suspected_key_drift": similar,
            "example_metadata": {n["id"]: n["metadata"] for n in with_meta[:3]},
        },
        "c4_levels": {
            "actors": actors,
            "data_stores": datastores,
            "tech_annotated_labels": tech_annotated,
            "containers": [c["label"] or c["id"] for c in containers],
            "nodes_nested_depth_ge_2": deep_nodes,
            "container_boundary_crossing_edges": boundary_crossing,
        },
        "line_labels": {
            "edges_total": len(edges),
            "unlabeled_edges": [e.get("unlabeled_desc") or e["id"] for e in unlabeled],
        },
    }

    stats = {
        "nodes": len(nodes), "edges": len(edges),
        "containers": len(containers), "layers": len(real_layers),
        "findings": len(findings),
        "by_severity": {},
        "unlabeled_edge_ratio": round(len(unlabeled) / len(edges), 2) if edges else 0.0,
    }
    for f in findings:
        stats["by_severity"][f["severity"]] = stats["by_severity"].get(f["severity"], 0) + 1

    # Promote unlabeled edges from stats to findings only when they dominate
    if edges and len(unlabeled) / len(edges) > 0.5:
        add("LINE-001", "warning",
            f"{len(unlabeled)}/{len(edges)} edges are unlabeled — the majority of relationships "
            "are unreadable", [e["id"] for e in unlabeled])

    return {"page": page_name, "findings": findings, "signals": signals, "stats": stats}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--page", help="page name or 1-based index (default: all pages)")
    ap.add_argument("-o", "--output")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    pages = load_models(args.file)
    if not pages:
        raise SystemExit("No diagram pages found")

    if args.page is not None:
        sel = [(n, m) for i, (n, m) in enumerate(pages, 1) if n == args.page or str(i) == args.page]
        if not sel:
            names = ", ".join(n for n, _ in pages)
            raise SystemExit(f"Page '{args.page}' not found. Available: {names}")
        pages = sel

    result = {"file": args.file, "pages": [lint_page(n, m) for n, m in pages]}

    out = json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(out + "\n")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
