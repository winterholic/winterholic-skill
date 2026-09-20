from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("artifact_gate.py")


def html(connector: str = "") -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Gate test</title></head>
<body><svg role="img" aria-labelledby="gate-title gate-desc" viewBox="0 0 100 100">
<title id="gate-title">Gate test</title><desc id="gate-desc">Artifact gate fixture.</desc>
<defs><marker id="arrow"><path d="M0 0 L8 3 L0 6 Z"/></marker></defs>
{connector}
</svg></body></html>"""


class ArtifactGateCliTests(unittest.TestCase):
    def test_missing_candidate_marks_checks_not_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.html"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "validate", str(missing), "--json"],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt["diagnostics"][0]["code"], "input/read-failed")
            self.assertEqual(receipt["checks"]["self_check"], "not_run")
            self.assertEqual(receipt["checks"]["geometry"], "not_run")

    def test_failed_delivery_preserves_last_good_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.html"
            output = root / "diagram.html"
            candidate.write_text(
                html('<line id="bad" x1="10" y1="10" x2="90" y2="70" marker-end="url(#arrow)"/>'),
                encoding="utf-8",
            )
            output.write_text("trusted-output", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "deliver", str(candidate), str(output), "--json"],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "trusted-output")
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt["status"], "fail")
            self.assertEqual(receipt["artifact_validation"], "failed")
            self.assertEqual(receipt["browser_evidence"], "not_run")
            self.assertEqual(receipt["visual_review"], "not_run")
            self.assertEqual(receipt["diagnostics"][0]["code"], "geometry/diagonal-connector")

    def test_reports_self_check_and_geometry_failures_independently(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.html"
            source = html(
                '<line id="bad" x1="10" y1="10" x2="90" y2="70" marker-end="url(#arrow)"/>'
            ).replace('role="img"', 'role="presentation"')
            candidate.write_text(source, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "validate", str(candidate), "--json"],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt["checks"]["self_check"], "fail")
            self.assertEqual(receipt["checks"]["geometry"], "fail")

    def test_successful_delivery_reports_exact_artifact_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.html"
            output = root / "diagram.html"
            source = html(
                '<line id="good" x1="10" y1="40" x2="90" y2="40" marker-end="url(#arrow)"/>'
            )
            candidate.write_text(source, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "deliver", str(candidate), str(output), "--json"],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), source)
            receipt = json.loads(result.stdout)
            expected_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
            self.assertEqual(receipt["candidate"]["sha256"], expected_hash)
            self.assertEqual(receipt["artifact"]["sha256"], expected_hash)
            self.assertEqual(receipt["artifact_validation"], "passed")
            self.assertEqual(receipt["browser_evidence"], "not_run")
            self.assertEqual(receipt["visual_review"], "not_run")


if __name__ == "__main__":
    unittest.main()
