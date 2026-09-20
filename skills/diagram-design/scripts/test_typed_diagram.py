from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("typed_diagram.py")
EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "typed"


def graph_spec(diagram_type: str = "architecture") -> dict[str, object]:
    return {
        "schema_version": 1,
        "diagram_type": diagram_type,
        "meta": {"title": "Order path", "description": "A compact structural example."},
        "nodes": [
            {"id": "client", "label": "Client", "kind": "frontend", "col": 0, "row": 0},
            {"id": "api", "label": "API", "kind": "backend", "col": 1, "row": 0},
            {"id": "store", "label": "Store", "kind": "database", "col": 1, "row": 1},
        ],
        "edges": [
            {"id": "request", "from": "client", "to": "api", "label": "HTTPS", "style": "accent"},
            {"id": "write", "from": "api", "to": "store", "label": "WRITE", "style": "default"},
        ],
    }


def sequence_spec() -> dict[str, object]:
    return {
        "schema_version": 1,
        "diagram_type": "sequence",
        "meta": {"title": "Login", "description": "Request and response."},
        "participants": [
            {"id": "browser", "label": "Browser"},
            {"id": "api", "label": "API"},
        ],
        "messages": [
            {"id": "login", "from": "browser", "to": "api", "label": "POST /login", "kind": "default"},
            {"id": "ok", "from": "api", "to": "browser", "label": "200 OK", "kind": "return"},
        ],
    }


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class TypedDiagramCliTests(unittest.TestCase):
    def write_spec(self, root: Path, value: dict[str, object]) -> Path:
        path = root / "spec.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_unknown_field_is_a_structured_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = graph_spec()
            value["surprise"] = True
            spec = self.write_spec(root, value)

            result = run_cli("validate", str(spec), "--json")

            self.assertEqual(result.returncode, 1, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt["diagnostics"][0]["code"], "schema/unknown-field")
            self.assertEqual(receipt["diagnostics"][0]["subject"], "$.surprise")

    def test_missing_edge_endpoint_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = graph_spec()
            value["edges"][0]["to"] = "missing"  # type: ignore[index]
            spec = self.write_spec(root, value)

            result = run_cli("validate", str(spec), "--json")

            self.assertEqual(result.returncode, 1, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertIn("graph/missing-endpoint", {item["code"] for item in receipt["diagnostics"]})

    def test_all_five_types_render_deterministically_and_pass_artifact_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            examples = sorted(EXAMPLES.glob("*.json"))
            self.assertEqual({path.stem for path in examples}, {"architecture", "process", "data-flow", "sequence", "state"})
            for index, spec in enumerate(examples):
                value = json.loads(spec.read_text(encoding="utf-8"))
                with self.subTest(diagram_type=value["diagram_type"]):
                    first = root / f"first-{index}.html"
                    second = root / f"second-{index}.html"
                    one = run_cli("render", str(spec), str(first), "--json")
                    two = run_cli("render", str(spec), str(second), "--json")
                    self.assertEqual(one.returncode, 0, one.stderr)
                    self.assertEqual(two.returncode, 0, two.stderr)
                    self.assertEqual(first.read_bytes(), second.read_bytes())
                    receipt = json.loads(one.stdout)
                    self.assertEqual(receipt["artifact_validation"], "passed")
                    self.assertEqual(receipt["spec"]["sha256"], hashlib.sha256(spec.read_bytes()).hexdigest())

    def test_delivery_preserves_last_good_output_when_spec_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = graph_spec()
            value["nodes"].append(value["nodes"][0].copy())  # type: ignore[union-attr,index]
            spec = self.write_spec(root, value)
            output = root / "diagram.html"
            output.write_text("trusted", encoding="utf-8")

            result = run_cli("deliver", str(spec), str(output), "--json")

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "trusted")
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt["diagnostics"][0]["code"], "graph/duplicate-id")


if __name__ == "__main__":
    unittest.main()
