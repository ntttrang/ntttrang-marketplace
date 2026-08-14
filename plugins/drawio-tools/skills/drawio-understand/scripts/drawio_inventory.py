#!/usr/bin/env python3
"""Extract a structured inventory (nodes, edges, containers, layers) from a draw.io file.

Handles:
  - .drawio / .xml files (uncompressed mxGraphModel, or <diagram> with
    base64 + raw-DEFLATE compressed content, the default for saved files)
  - .svg files exported from draw.io (diagram XML embedded in the content="..." attribute)

Usage:
  python drawio_inventory.py <file> [--page <name-or-index>] [--pretty]
  python drawio_inventory.py <file> -o inventory.json

Output: JSON with pages, layers, containers, nodes, edges, and warnings
(dangling edge endpoints, orphan nodes, unlabeled edges).
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


# style keys -> semantic kind, used to classify vertices.
# Order matters: first match wins. Most specific first.
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


def classify_edge(s: dict) -> dict:
    end = s.get("endArrow", "classic")  # draw.io default endArrow is classic
    start = s.get("startArrow", "none")
    if end == "none" and start == "none":
        direction = "undirected"
    elif end != "none" and start != "none":
        direction = "bidirectional"
    elif end == "none":
        direction = "reverse"  # arrow only on the start
    else:
        direction = "directed"
    kind = "association"
    if "dashed" in s and s["dashed"] not in ("0", "false"):
        kind = "dashed"
    if s.get("endFill") == "0":
        kind = "open-arrow"
    if start == "oval" or s.get("endArrow") in ("oval", "diamond") or s.get("startArrow") in ("oval", "diamond"):
        kind = "generalization-or-inheritance"
    if s.get("endArrow") == "diamondThin" or s.get("startArrow") == "diamondThin":
        kind = "aggregation-composition"
    return {
        "direction": direction,
        "style_kind": kind,
        "edge_style": s.get("edgeStyle", "straight"),
        "label_background": s.get("labelBackgroundColor", ""),
    }


def parse_cells(model: ET.Element, page_name: str):
    """Walk the <root> of one mxGraphModel and return inventory dicts."""
    cells = {}
    order = []
    root = model.find("root")
    if root is None:
        return {}, [], [], [], [], []

    def grab(cell_el):
        """Extract common fields from an mxCell (or its object wrapper)."""
        obj = {}
        parent_el = cell_el
        # <object> wrappers carry the label in an attribute and metadata as attributes
        if parent_el.tag in ("object", "UserObject"):
            obj["metadata"] = {k: v for k, v in parent_el.attrib.items()
                               if k not in ("label", "id")}
            cell_el = parent_el.find("mxCell")
            if cell_el is None:
                return None
            obj["label_attr"] = parent_el.attrib.get("label", "")
        cid = cell_el.attrib.get("id")
        if cid is None:
            return None
        obj["id"] = cid
        obj["element"] = cell_el
        return obj

    for el in root:
        got = grab(el)
        if got is None:
            continue
        cells[got["id"]] = got
        order.append(got["id"])

    nodes, edges, containers, layers = [], [], [], []

    for cid in order:
        got = cells[cid]
        el = got["element"]
        attrs = el.attrib
        style = style_dict(attrs.get("style", ""))
        label = clean_label(attrs.get("value", "") or got.get("label_attr", ""))
        parent_id = attrs.get("parent")

        if attrs.get("vertex") == "1":
            entry = {
                "id": cid,
                "label": label or "(unlabeled)",
                "kind": classify_vertex(style),
                "parent": parent_id,
                "style": style,
                "metadata": got.get("metadata", {}),
            }
            geom = el.find("mxGeometry")
            if geom is not None and geom.attrib.get("relative") != "1":
                entry["geometry"] = {k: float(v) for k, v in geom.attrib.items()
                                     if k in ("x", "y", "width", "height")}
            # containers swallow their children; keep them separate from plain nodes
            if entry["kind"] in ("swimlane", "group") or style.get("container") == "1":
                entry["container_kind"] = entry["kind"]
                containers.append(entry)
            else:
                nodes.append(entry)
        elif attrs.get("edge") == "1":
            info = classify_edge(style)
            edges.append({
                "id": cid,
                "label": label,
                "source": attrs.get("source"),
                "target": attrs.get("target"),
                "parent": parent_id,
                "style": style,
                **info,
            })
        else:
            # no vertex/edge attr -> layer (parent="0") or root cell
            if parent_id == "0":
                layers.append({"id": cid, "label": clean_label(attrs.get("value", "")) or cid,
                               "visible": attrs.get("visible", "1") != "0"})

    return cells, nodes, edges, containers, layers, order


def resolve_references(cells, nodes, edges, containers):
    """Attach human-readable names to parents and edge endpoints; collect warnings."""
    by_id = {}
    for n in nodes + containers:
        by_id[n["id"]] = n

    def name_of(cid):
        if cid is None:
            return None
        if cid == "0":
            return "(root)"
        if cid == "1":
            return "(default layer)"
        return (by_id.get(cid) or {}).get("label", f"(unknown id {cid})")

    container_ids = {c["id"] for c in containers}
    for n in nodes + containers:
        p = n.get("parent")
        n["parent_label"] = name_of(p)
        n["in_container"] = p in container_ids

    warnings = []
    connected = set()
    for e in edges:
        e["source_label"] = name_of(e["source"])
        e["target_label"] = name_of(e["target"])
        connected.add(e["source"])
        connected.add(e["target"])
        if (e["source"] and e["source"] not in by_id) or (e["target"] and e["target"] not in by_id):
            warnings.append(f"Edge '{e['label'] or e['id']}' points to a non-existent cell")
        if e["source"] is None and e["target"] is None:
            warnings.append(f"Edge '{e['label'] or e['id']}' is floating (no endpoints)")

    for n in nodes:
        if n["id"] not in connected:
            warnings.append(f"Node '{n['label']}' has no connections")
    for e in edges:
        if not e["label"]:
            e["label"] = ""

    return warnings


def load_models(path: str):
    """Return a list of (page_name, mxGraphModel Element) from any supported file."""
    with open(path, "rb") as f:
        data = f.read()

    pages = []
    # SVG export: diagram XML hides in content="..." (HTML-escaped, base64+deflate)
    if path.lower().endswith(".svg") or b"<svg" in data[:2000]:
        m = re.search(rb'content="([^"]+)"', data)
        if not m:
            raise SystemExit("SVG file has no embedded draw.io content= attribute "
                             "(likely exported without draw.io data — read it as an image instead)")
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
        sel = []
        for i, (name, model) in enumerate(pages, 1):
            if name == args.page or str(i) == args.page:
                sel.append((name, model))
        if not sel:
            names = ", ".join(n for n, _ in pages)
            raise SystemExit(f"Page '{args.page}' not found. Available: {names}")
        pages = sel

    result = {"file": args.file, "pages": []}
    for name, model in pages:
        cells, nodes, edges, containers, layers, order = parse_cells(model, name)
        warnings = resolve_references(cells, nodes, edges, containers)
        for n in nodes + containers + edges:
            n.pop("element", None)
        result["pages"].append({
            "name": name,
            "layers": layers,
            "containers": containers,
            "nodes": nodes,
            "edges": edges,
            "warnings": warnings,
            "counts": {"nodes": len(nodes), "edges": len(edges),
                       "containers": len(containers), "layers": len(layers)},
        })

    out = json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(out + "\n")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
