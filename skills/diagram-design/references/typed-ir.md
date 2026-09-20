# Typed Diagram IR v1

Use this optional source format when a structural diagram will be revised repeatedly, diffed, or regenerated. The pilot supports **architecture**, **process**, **data-flow**, **sequence**, and **state**. Keep the manual HTML/SVG workflow for the other 35 types, bespoke composition, semantic-pattern primitives, animation, imports, or geometry beyond this grid.

## Commands

```powershell
python scripts/typed_diagram.py validate spec.json --json
python scripts/typed_diagram.py render spec.json candidate.html --json
python scripts/typed_diagram.py deliver spec.json final.html --json
```

`render` and `deliver` both render deterministically, run the normal artifact gate, and atomically replace the target only after validation passes. Their names express intent; they share the same guarded write path. A successful receipt binds the source and artifact with SHA-256 hashes. Browser evidence and visual review remain `not_run` until performed separately.

## Shared contract

- UTF-8 JSON, `schema_version: 1`.
- Unknown fields fail closed with `schema/unknown-field`.
- IDs use lowercase kebab-case, start with a letter, and are stable across revisions.
- `meta.title` and `meta.description` are required and become the accessible SVG title and description.
- No automatic semantic inference: the author chooses type, labels, order, and grid cells.

## Grid graph types

Architecture, process, data-flow, and state use:

```json
{
  "schema_version": 1,
  "diagram_type": "architecture",
  "meta": {"title": "Order path", "description": "Client request to durable storage."},
  "nodes": [
    {"id": "client", "label": "Client", "kind": "frontend", "col": 0, "row": 0},
    {"id": "api", "label": "API", "kind": "backend", "col": 1, "row": 0, "variant": "emphasis"}
  ],
  "edges": [
    {"id": "request", "from": "client", "to": "api", "label": "HTTPS", "style": "accent"}
  ]
}
```

Node kinds: `frontend`, `backend`, `database`, `cloud`, `security`, `messagebus`, `external`, `step`, `state`. Optional variants: `default`, `emphasis`, `security`, `dashed`. Optional `note` is limited to 56 characters. Edge styles: `default`, `accent`, `link`, `dashed`.

Limits: 1–12 nodes, 0–16 edges, grid coordinates 0–7, and one node per cell. The renderer uses stable grid geometry and orthogonal H/V paths; it does not optimize layout.

## Sequence type

```json
{
  "schema_version": 1,
  "diagram_type": "sequence",
  "meta": {"title": "Login", "description": "Request and response."},
  "participants": [
    {"id": "browser", "label": "Browser"},
    {"id": "api", "label": "API"}
  ],
  "messages": [
    {"id": "login", "from": "browser", "to": "api", "label": "POST /login", "kind": "default"}
  ]
}
```

Participants appear in source order; messages appear top-to-bottom in source order. Message kinds are `default`, `return`, and `async`. Limits: 2–5 participants and 1–12 messages.

## Failure boundary

Schema, budget, duplicate-ID, duplicate-cell, and missing-endpoint diagnostics are structured. An invalid spec never changes the requested output. Machine validation covers structural contracts only; always inspect the rendered result at the target viewport before calling it visually approved.

