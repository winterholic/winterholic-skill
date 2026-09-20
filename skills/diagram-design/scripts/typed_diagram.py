#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import artifact_gate


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


GRAPH_TYPES = {"architecture", "process", "data-flow", "state"}
ALL_TYPES = GRAPH_TYPES | {"sequence"}
NODE_KINDS = {"frontend", "backend", "database", "cloud", "security", "messagebus", "external", "step", "state"}
NODE_VARIANTS = {"default", "emphasis", "security", "dashed"}
EDGE_STYLES = {"default", "accent", "link", "dashed"}
MESSAGE_KINDS = {"default", "return", "async"}
ID_RE = re.compile(r"^[a-z][a-z0-9-]{0,47}$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def diagnostic(code: str, subject: str, message: str, evidence: dict[str, Any], fixes: list[str]) -> dict[str, Any]:
    return {"code": code, "subject": subject, "message": message, "evidence": evidence, "supported_fixes": fixes}


def unknown_fields(value: object, allowed: set[str], subject: str) -> list[dict[str, Any]]:
    if not isinstance(value, dict):
        return []
    return [
        diagnostic("schema/unknown-field", f"{subject}.{key}", f"Unknown field: {key}", {"field": key}, ["remove the field or use a documented v1 field"])
        for key in sorted(set(value) - allowed)
    ]


def require_object(value: object, subject: str, findings: list[dict[str, Any]]) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    findings.append(diagnostic("schema/type", subject, "Expected an object.", {"actual": type(value).__name__}, ["replace the value with a JSON object"]))
    return None


def require_list(value: object, subject: str, findings: list[dict[str, Any]]) -> list[Any] | None:
    if isinstance(value, list):
        return value
    findings.append(diagnostic("schema/type", subject, "Expected an array.", {"actual": type(value).__name__}, ["replace the value with a JSON array"]))
    return None


def required_text(item: dict[str, Any], key: str, subject: str, findings: list[dict[str, Any]], limit: int = 80) -> None:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        findings.append(diagnostic("schema/text", f"{subject}.{key}", f"Expected non-empty text up to {limit} characters.", {"value": value}, [f"provide concise {key} text"]))


def validate_id(item: dict[str, Any], subject: str, findings: list[dict[str, Any]]) -> None:
    value = item.get("id")
    if not isinstance(value, str) or ID_RE.fullmatch(value) is None:
        findings.append(diagnostic("schema/id", f"{subject}.id", "IDs must use lowercase kebab-case and start with a letter.", {"value": value}, ["use an ID such as order-api"]))


def validate_meta(value: object, findings: list[dict[str, Any]]) -> None:
    meta = require_object(value, "$.meta", findings)
    if meta is None:
        return
    findings.extend(unknown_fields(meta, {"title", "description"}, "$.meta"))
    required_text(meta, "title", "$.meta", findings, 100)
    required_text(meta, "description", "$.meta", findings, 240)


def validate_graph(spec: dict[str, Any], findings: list[dict[str, Any]]) -> None:
    findings.extend(unknown_fields(spec, {"schema_version", "diagram_type", "meta", "nodes", "edges"}, "$"))
    nodes = require_list(spec.get("nodes"), "$.nodes", findings)
    edges = require_list(spec.get("edges"), "$.edges", findings)
    if nodes is None or edges is None:
        return
    if not 1 <= len(nodes) <= 12:
        findings.append(diagnostic("budget/nodes", "$.nodes", "Graph diagrams require 1..12 nodes.", {"count": len(nodes)}, ["split overview and detail diagrams"]))
    if len(edges) > 16:
        findings.append(diagnostic("budget/edges", "$.edges", "Graph diagrams allow at most 16 edges.", {"count": len(edges)}, ["remove redundant relationships or split the diagram"]))
    node_ids: list[str] = []
    cells: list[tuple[int, int]] = []
    for index, raw in enumerate(nodes):
        subject = f"$.nodes[{index}]"
        item = require_object(raw, subject, findings)
        if item is None:
            continue
        findings.extend(unknown_fields(item, {"id", "label", "kind", "col", "row", "note", "variant"}, subject))
        validate_id(item, subject, findings)
        required_text(item, "label", subject, findings, 36)
        if "note" in item and (not isinstance(item["note"], str) or len(item["note"]) > 56):
            findings.append(diagnostic("schema/text", f"{subject}.note", "Note must be text up to 56 characters.", {"value": item["note"]}, ["shorten or remove the note"]))
        if item.get("kind") not in NODE_KINDS:
            findings.append(diagnostic("schema/enum", f"{subject}.kind", "Unsupported node kind.", {"value": item.get("kind")}, [f"choose one of {sorted(NODE_KINDS)}"]))
        if item.get("variant", "default") not in NODE_VARIANTS:
            findings.append(diagnostic("schema/enum", f"{subject}.variant", "Unsupported node variant.", {"value": item.get("variant")}, [f"choose one of {sorted(NODE_VARIANTS)}"]))
        coordinates: list[int] = []
        for key in ("col", "row"):
            value = item.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 7:
                findings.append(diagnostic("schema/grid-coordinate", f"{subject}.{key}", "Grid coordinates must be integers from 0 to 7.", {"value": value}, ["choose a grid coordinate from 0 to 7"]))
            else:
                coordinates.append(value)
        if isinstance(item.get("id"), str):
            node_ids.append(item["id"])
        if len(coordinates) == 2:
            cells.append((coordinates[0], coordinates[1]))
    for repeated in sorted({value for value in node_ids if node_ids.count(value) > 1}):
        findings.append(diagnostic("graph/duplicate-id", f"#${repeated}".replace("#$", "#"), "Node IDs must be unique.", {"id": repeated}, ["rename one node and update its edges"]))
    for cell in sorted({value for value in cells if cells.count(value) > 1}):
        findings.append(diagnostic("graph/duplicate-cell", "$.nodes", "Only one node may occupy a grid cell.", {"col": cell[0], "row": cell[1]}, ["move one node to a free grid cell"]))
    known = set(node_ids)
    edge_ids: list[str] = []
    for index, raw in enumerate(edges):
        subject = f"$.edges[{index}]"
        item = require_object(raw, subject, findings)
        if item is None:
            continue
        findings.extend(unknown_fields(item, {"id", "from", "to", "label", "style"}, subject))
        validate_id(item, subject, findings)
        required_text(item, "label", subject, findings, 24)
        if item.get("style", "default") not in EDGE_STYLES:
            findings.append(diagnostic("schema/enum", f"{subject}.style", "Unsupported edge style.", {"value": item.get("style")}, [f"choose one of {sorted(EDGE_STYLES)}"]))
        for key in ("from", "to"):
            endpoint = item.get(key)
            if endpoint not in known:
                findings.append(diagnostic("graph/missing-endpoint", f"{subject}.{key}", "Edge endpoint does not name a node.", {"value": endpoint}, ["use an existing node ID"]))
        if isinstance(item.get("id"), str):
            edge_ids.append(item["id"])
    for repeated in sorted({value for value in edge_ids if edge_ids.count(value) > 1}):
        findings.append(diagnostic("graph/duplicate-id", f"#{repeated}", "Edge IDs must be unique.", {"id": repeated}, ["rename one edge"]))


def validate_sequence(spec: dict[str, Any], findings: list[dict[str, Any]]) -> None:
    findings.extend(unknown_fields(spec, {"schema_version", "diagram_type", "meta", "participants", "messages"}, "$"))
    participants = require_list(spec.get("participants"), "$.participants", findings)
    messages = require_list(spec.get("messages"), "$.messages", findings)
    if participants is None or messages is None:
        return
    if not 2 <= len(participants) <= 5:
        findings.append(diagnostic("budget/participants", "$.participants", "Sequence diagrams require 2..5 participants.", {"count": len(participants)}, ["add a participant or split the interaction"]))
    if not 1 <= len(messages) <= 12:
        findings.append(diagnostic("budget/messages", "$.messages", "Sequence diagrams require 1..12 messages.", {"count": len(messages)}, ["split long interactions"]))
    ids: list[str] = []
    for index, raw in enumerate(participants):
        subject = f"$.participants[{index}]"
        item = require_object(raw, subject, findings)
        if item is None:
            continue
        findings.extend(unknown_fields(item, {"id", "label"}, subject))
        validate_id(item, subject, findings)
        required_text(item, "label", subject, findings, 32)
        if isinstance(item.get("id"), str):
            ids.append(item["id"])
    for repeated in sorted({value for value in ids if ids.count(value) > 1}):
        findings.append(diagnostic("graph/duplicate-id", f"#{repeated}", "Participant IDs must be unique.", {"id": repeated}, ["rename one participant"]))
    known = set(ids)
    message_ids: list[str] = []
    for index, raw in enumerate(messages):
        subject = f"$.messages[{index}]"
        item = require_object(raw, subject, findings)
        if item is None:
            continue
        findings.extend(unknown_fields(item, {"id", "from", "to", "label", "kind"}, subject))
        validate_id(item, subject, findings)
        required_text(item, "label", subject, findings, 36)
        if item.get("kind", "default") not in MESSAGE_KINDS:
            findings.append(diagnostic("schema/enum", f"{subject}.kind", "Unsupported message kind.", {"value": item.get("kind")}, [f"choose one of {sorted(MESSAGE_KINDS)}"]))
        for key in ("from", "to"):
            if item.get(key) not in known:
                findings.append(diagnostic("graph/missing-endpoint", f"{subject}.{key}", "Message endpoint does not name a participant.", {"value": item.get(key)}, ["use an existing participant ID"]))
        if isinstance(item.get("id"), str):
            message_ids.append(item["id"])
    for repeated in sorted({value for value in message_ids if message_ids.count(value) > 1}):
        findings.append(diagnostic("graph/duplicate-id", f"#{repeated}", "Message IDs must be unique.", {"id": repeated}, ["rename one message"]))


def validate_spec(spec: object) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    root = require_object(spec, "$", findings)
    if root is None:
        return findings
    if root.get("schema_version") != 1:
        findings.append(diagnostic("schema/version", "$.schema_version", "Only schema_version 1 is supported.", {"value": root.get("schema_version")}, ["set schema_version to 1"]))
    diagram_type = root.get("diagram_type")
    if diagram_type not in ALL_TYPES:
        findings.append(diagnostic("schema/diagram-type", "$.diagram_type", "Unsupported typed diagram.", {"value": diagram_type}, [f"choose one of {sorted(ALL_TYPES)}", "use the manual HTML path for other types"]))
        findings.extend(unknown_fields(root, {"schema_version", "diagram_type", "meta"}, "$"))
    elif diagram_type == "sequence":
        validate_sequence(root, findings)
    else:
        validate_graph(root, findings)
    validate_meta(root.get("meta"), findings)
    return findings


def load_spec(path: Path) -> tuple[object | None, bytes, list[dict[str, Any]]]:
    try:
        data = path.read_bytes()
        return json.loads(data.decode("utf-8")), data, []
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, b"", [diagnostic("input/read-failed", str(path), str(exc), {}, ["provide a readable UTF-8 JSON file"])]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def graph_svg(spec: dict[str, Any]) -> tuple[str, int, int]:
    nodes = spec["nodes"]
    edges = spec["edges"]
    width = max(520, 120 + (max(node["col"] for node in nodes) + 1) * 220)
    height = max(330, 170 + (max(node["row"] for node in nodes) + 1) * 130)
    positions = {node["id"]: (60 + node["col"] * 220, 100 + node["row"] * 130) for node in nodes}
    lines: list[str] = []
    for edge in edges:
        sx, sy = positions[edge["from"]]
        tx, ty = positions[edge["to"]]
        scx, scy, tcx, tcy = sx + 80, sy + 32, tx + 80, ty + 32
        if sy == ty:
            start_x, end_x = (sx + 160, tx) if sx < tx else (sx, tx + 160)
            path = f"M {start_x} {scy} H {end_x}"
            lx, ly = (start_x + end_x) / 2, scy - 12
        elif sx == tx:
            start_y, end_y = (sy + 64, ty) if sy < ty else (sy, ty + 64)
            path = f"M {scx} {start_y} V {end_y}"
            lx, ly = scx + 28, (start_y + end_y) / 2 - 8
        else:
            start_x = sx + 160 if sx < tx else sx
            end_x = tx if sx < tx else tx + 160
            mid_x = (start_x + end_x) / 2
            path = f"M {start_x} {scy} H {mid_x} V {tcy} H {end_x}"
            lx, ly = mid_x, min(scy, tcy) - 12
        style = edge.get("style", "default")
        stroke = {"accent": "#1A76B4", "link": "#0A5E93"}.get(style, "#535A63")
        dash = ' stroke-dasharray="6 5"' if style == "dashed" else ""
        label = esc(edge["label"])
        mask_w = max(44, len(str(edge["label"])) * 7 + 12)
        lines.append(f'<path id="edge-{esc(edge["id"])}" data-diagram-connector d="{path}" fill="none" stroke="{stroke}" stroke-width="1.5" marker-end="url(#typed-arrow)"{dash}/>')
        lines.append(f'<rect x="{lx-mask_w/2:.1f}" y="{ly-10:.1f}" width="{mask_w}" height="14" rx="2" fill="#F7F9F9"/><text x="{lx:.1f}" y="{ly:.1f}" class="edge-label">{label}</text>')
    for node in nodes:
        x, y = positions[node["id"]]
        variant = node.get("variant", "default")
        kind = node["kind"]
        fill = "#E7F3FA" if variant == "emphasis" else ("#F2F8F4" if variant == "security" else "#FFFFFF")
        stroke = "#1A76B4" if variant == "emphasis" else ("#4F7D61" if variant == "security" else "#89919B")
        dash = ' stroke-dasharray="5 4"' if variant == "dashed" else ""
        lines.append(f'<g id="node-{esc(node["id"])}" data-node-kind="{esc(kind)}"><rect x="{x}" y="{y}" width="160" height="64" rx="6" fill="#F7F9F9"/><rect x="{x}" y="{y}" width="160" height="64" rx="6" fill="{fill}" stroke="{stroke}"{dash}/><text x="{x+12}" y="{y+18}" class="kind">{esc(kind.upper())}</text><text x="{x+80}" y="{y+39}" class="node-label">{esc(node["label"])}</text>')
        if node.get("note"):
            lines.append(f'<text x="{x+80}" y="{y+54}" class="note">{esc(node["note"])}</text>')
        lines.append("</g>")
    return "\n".join(lines), width, height


def sequence_svg(spec: dict[str, Any]) -> tuple[str, int, int]:
    participants = spec["participants"]
    messages = spec["messages"]
    width = max(360, 160 + (len(participants) - 1) * 190)
    height = 190 + len(messages) * 72
    xs = {item["id"]: 80 + index * 190 for index, item in enumerate(participants)}
    lines: list[str] = []
    for item in participants:
        x = xs[item["id"]]
        lines.append(f'<line id="lifeline-{esc(item["id"])}" data-diagram-connector x1="{x}" y1="94" x2="{x}" y2="{height-42}" stroke="#9AA1AA" stroke-dasharray="4 5"/>')
    for index, message in enumerate(messages):
        y = 138 + index * 72
        x1, x2 = xs[message["from"]], xs[message["to"]]
        kind = message.get("kind", "default")
        dash = ' stroke-dasharray="6 5"' if kind in {"return", "async"} else ""
        lines.append(f'<line id="message-{esc(message["id"])}" data-diagram-connector x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#535A63" stroke-width="1.5" marker-end="url(#typed-arrow)"{dash}/><rect x="{(x1+x2)/2-54:.1f}" y="{y-25}" width="108" height="16" rx="2" fill="#F7F9F9"/><text x="{(x1+x2)/2:.1f}" y="{y-14}" class="edge-label">{esc(message["label"])}</text>')
    for item in participants:
        x = xs[item["id"]]
        lines.append(f'<g id="participant-{esc(item["id"])}"><rect x="{x-66}" y="52" width="132" height="42" rx="6" fill="#FFFFFF" stroke="#89919B"/><text x="{x}" y="78" class="node-label">{esc(item["label"])}</text></g>')
    return "\n".join(lines), width, height


def render_html(spec: dict[str, Any]) -> str:
    body, width, height = sequence_svg(spec) if spec["diagram_type"] == "sequence" else graph_svg(spec)
    title = esc(spec["meta"]["title"])
    description = esc(spec["meta"]["description"])
    diagram_type = esc(spec["diagram_type"])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>html,body{{margin:0;background:#F7F9F9;color:#2B3139;font-family:Inter,Segoe UI,sans-serif}}main{{max-width:{width}px;margin:0 auto;padding:28px}}h1{{font-size:22px;margin:0 0 5px}}p{{color:#64707D;margin:0 0 18px;font-size:13px}}svg{{width:100%;height:auto;display:block}}.node-label{{font-size:13px;font-weight:650;text-anchor:middle;fill:#2B3139}}.kind{{font:7px ui-monospace,Consolas,monospace;letter-spacing:.1em;fill:#64707D}}.note,.edge-label{{font:9px ui-monospace,Consolas,monospace;text-anchor:middle;fill:#535A63}}</style></head>
<body><main data-typed-diagram="1" data-diagram-type="{diagram_type}"><h1>{title}</h1><p>{description}</p><svg role="img" aria-labelledby="typed-title typed-desc" viewBox="0 0 {width} {height}"><title id="typed-title">{title}</title><desc id="typed-desc">{description}</desc><defs><marker id="typed-arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#535A63"/></marker></defs><rect width="100%" height="100%" fill="#F7F9F9"/>{body}</svg></main></body></html>
'''


def base_receipt(path: Path, data: bytes, findings: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "fail" if findings else "pass",
        "artifact_validation": "not_run",
        "browser_evidence": "not_run",
        "visual_review": "not_run",
        "spec": {"path": str(path.resolve()), "sha256": sha256(data), "bytes": len(data)},
        "diagnostics": findings,
    }


def process(command: str, spec_path: Path, output: Path | None) -> dict[str, Any]:
    raw, data, findings = load_spec(spec_path)
    if not findings:
        findings = validate_spec(raw)
    receipt = base_receipt(spec_path, data, findings)
    if findings or command == "validate":
        return receipt
    assert isinstance(raw, dict) and output is not None
    with tempfile.TemporaryDirectory() as directory:
        candidate = Path(directory) / "typed-candidate.html"
        candidate.write_text(render_html(raw), encoding="utf-8", newline="\n")
        gate = artifact_gate.deliver(candidate, output)
    gate["spec"] = receipt["spec"]
    gate["command"] = command
    return gate


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and deterministically render typed diagram v1 JSON.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("spec", type=Path)
    validate_parser.add_argument("--json", action="store_true", dest="as_json")
    for name in ("render", "deliver"):
        child = subparsers.add_parser(name)
        child.add_argument("spec", type=Path)
        child.add_argument("output", type=Path)
        child.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    receipt = process(args.command, args.spec, getattr(args, "output", None))
    if args.as_json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        print(("OK" if receipt["status"] == "pass" else "FAIL"), args.spec)
        for item in receipt["diagnostics"]:
            print(f"  - [{item['code']}] {item['subject']}: {item['message']}")
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
