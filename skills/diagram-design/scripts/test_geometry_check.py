from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import geometry_check


SCRIPT = Path(__file__).with_name("verify-geometry.py")


def diagram_with(connector: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Geometry test</title></head>
<body><svg role="img" aria-labelledby="g-title g-desc" viewBox="0 0 100 100">
<title id="g-title">Geometry test</title><desc id="g-desc">Geometry test fixture.</desc>
<defs><marker id="arrow"><path d="M0 0 L8 3 L0 6 Z"/></marker></defs>
{connector}
</svg></body></html>"""


class GeometryCliTests(unittest.TestCase):
    def run_check(self, source: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "diagram.html"
            path.write_text(source, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--json", str(path)],
                text=True,
                capture_output=True,
                check=False,
            )

    def test_rejects_diagonal_connector_line_with_stable_diagnostic(self) -> None:
        result = self.run_check(
            diagram_with(
                '<line id="bad-edge" x1="10" y1="10" x2="90" y2="70" '
                'marker-end="url(#arrow)"/>'
            )
        )

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("geometry/diagonal-connector", result.stdout)
        receipt = json.loads(result.stdout)
        diagnostic = receipt["diagnostics"][0]
        self.assertEqual(diagnostic["subject"], "#bad-edge")
        self.assertIn("x1", diagnostic["evidence"])
        self.assertTrue(diagnostic["supported_fixes"])

    def test_accepts_axis_aligned_connector_line(self) -> None:
        result = self.run_check(
            diagram_with(
                '<line id="good-edge" x1="10" y1="40" x2="90" y2="40" '
                'marker-end="url(#arrow)"/>'
            )
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["diagnostics"], [])

    def test_rejects_explicit_diagonal_path_segment(self) -> None:
        result = self.run_check(
            diagram_with(
                '<path id="bad-path" d="M 10 10 L 90 70" fill="none" '
                'marker-end="url(#arrow)"/>'
            )
        )

        self.assertEqual(result.returncode, 1, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["diagnostics"][0]["code"], "geometry/diagonal-segment")
        self.assertEqual(receipt["diagnostics"][0]["subject"], "#bad-path")

    def test_shipped_examples_have_no_unacknowledged_diagonal_connectors(self) -> None:
        assets = Path(__file__).resolve().parent.parent / "assets"
        failures = {
            path.name: geometry_check.verify(path)
            for path in assets.glob("example-*.html")
            if geometry_check.verify(path)
        }

        self.assertEqual(failures, {})


if __name__ == "__main__":
    unittest.main()
