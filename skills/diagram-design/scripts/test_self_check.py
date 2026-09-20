from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("self_check.py")
SPEC = importlib.util.spec_from_file_location("diagram_self_check", MODULE_PATH)
assert SPEC and SPEC.loader
SELF_CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SELF_CHECK)


def verify_html(svg_body: str) -> list[str]:
    source = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Test</title></head>
<body><svg role="img" aria-labelledby="test-title test-desc" viewBox="0 0 100 100">
<title id="test-title">Test diagram</title>
<desc id="test-desc">A test diagram.</desc>
{svg_body}
</svg></body></html>"""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "diagram.html"
        path.write_text(source, encoding="utf-8")
        return SELF_CHECK.verify(path)


class FragmentIntegrityTests(unittest.TestCase):
    def test_rejects_duplicate_ids(self) -> None:
        errors = verify_html('<rect id="node"/><circle id="node"/>')
        self.assertIn("duplicate id 'node'", errors)

    def test_rejects_unresolved_fragment_references(self) -> None:
        errors = verify_html('<path marker-end="url(#missing-arrow)"/>')
        self.assertIn("unresolved fragment reference #missing-arrow", errors)


if __name__ == "__main__":
    unittest.main()
