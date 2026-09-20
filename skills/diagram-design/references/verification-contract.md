# Verification and delivery contract

Load this reference after the visual type is selected and before writing the final output. The purpose is to keep three different claims separate:

| Claim | Evidence | It does not prove |
|---|---|---|
| Artifact validation | `artifact_gate.py validate` or `deliver` receipt | Browser layout or visual polish |
| Browser evidence | Measurements and screenshots from the exact delivered HTML | Editorial quality |
| Perceptual review | Inspection of rendered screenshots or the live artifact | Deterministic file identity |

Never collapse these into one “verified” label.

## Candidate-first workflow

1. Write `<name>.candidate.html` beside the requested output. Do not overwrite the last known good `<name>.html` while authoring.
2. Run the deterministic gate after each meaningful candidate edit:

   ```bash
   python3 scripts/artifact_gate.py validate <name>.candidate.html --json
   ```

3. Read each `diagnostics[]` item by `code`, `subject`, `evidence`, and `supported_fixes`. Change only the named subject where practical, then validate again.
4. If two focused corrections fail to reduce the diagnostic count, stop local geometry guessing and inspect the execution path, invariants, environment, and logs or rendered evidence.
5. A passing validation freezes the candidate. Do not edit it afterward.
6. Commit the exact bytes atomically:

   ```bash
   python3 scripts/artifact_gate.py deliver <name>.candidate.html <name>.html --json
   ```

The output must end in `.html`. `deliver` writes a same-directory temporary file, flushes it, and replaces the target only after validation passes. A failed validation or replacement leaves the previous target untouched. The receipt binds the candidate and delivered artifact with SHA-256 and byte counts.

## Current executable checks

`artifact_gate.py` combines:

- `self_check.py`: accessible SVG naming, fragment integrity, single-file safety, and the bounded motion contract.
- `verify-geometry.py`: diagonal marker-bearing `<line>` elements and explicit diagonal `L` path segments.

The geometry checker is deliberately a baseline. It does not prove node clearance, label-mask clearance, connector overlap, bridge correctness, or visual balance. Those remain browser and perceptual checks. Loop radial spokes are the only installed exemption and must carry `data-geometry-exempt="radial"`; unknown exemption values fail closed.

Good:

```html
<path d="M120 80 H192 Q200 80 200 88 V144" marker-end="url(#arrow)"/>
```

Bad:

```html
<line x1="120" y1="80" x2="200" y2="144" marker-end="url(#arrow)"/>
```

## Browser evidence

After successful delivery, open the exact delivered `<name>.html`; do not rerender another source. At the requested final size and 100% zoom, record:

- viewport size and theme;
- horizontal or vertical page overflow;
- clipped text or elements outside the SVG `viewBox`;
- hidden arrowheads, connector collisions, and label-mask collisions;
- readability of the smallest required label;
- for motion, the complete static/no-JS frame and reduced-motion behavior.

When both light and dark variants are delivered, inspect both. Record browser evidence as `passed`, `failed`, or `not_run (<reason>)` without changing the artifact-validation claim.

## Perceptual review

Inspect the rendered result with a human or image-capable reviewer. Judge hierarchy, density, focal emphasis, whitespace, and whether the chosen visual type communicates better than a table or paragraph. Record `passed`, `failed (<visible defect>)`, or `not_run (<reason>)`.

## Handoff receipt

Return these fields:

```text
output: <absolute path>
artifact_validation: passed|failed
candidate_sha256: <receipt value>
artifact_sha256: <receipt value or absent on failure>
browser_evidence: passed|failed|not_run (<reason>)
visual_review: passed|failed|not_run (<reason>)
correction_rounds: <number>
```

## Fallbacks

| Situation | Next action |
|---|---|
| Python is unavailable | Run the §9 checklist manually and deliver to a new filename; do not overwrite the last known good output |
| Browser or image reader is unavailable | Keep artifact validation separate and report browser evidence and visual review as `not_run` |
| Candidate validation fails | Preserve the existing output and return the structured diagnostics |
| Output replacement fails | Preserve or inspect the existing output, repair directory permissions, and rerun `deliver` |

## Typed source boundary

HTML remains the source of truth for the current 40-type skill. Do not invent a universal JSON field or claim deterministic spec-to-render compilation until a renderer and round-trip tests exist for that type. Introduce typed intermediate representation incrementally for architecture, process/data-flow, sequence, and state only after the shared validation gate is stable.

## Gotchas

- A passing artifact receipt is not a screenshot and is not visual approval.
- Running browser checks after a failed delivery may inspect a stale last-known-good output. Repair and deliver first.
- Hash the file bytes, not text re-encoded by the caller; newline translation changes byte identity on Windows.
