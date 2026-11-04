import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_legal_snapshot import verify, EXPECTED_FILES


class LegalSnapshotTests(unittest.TestCase):
    def make_bundle(self, root: Path):
        docs = []
        for name in sorted(EXPECTED_FILES):
            payload = (b"%PDF-1.7" if name.endswith(".pdf") else b"<html><body>official text</body></html>") + b" legal" * 120
            (root / name).write_bytes(payload)
            docs.append({"file": name, "sha256": hashlib.sha256(payload).hexdigest(), "size_bytes": len(payload)})
        (root / "policy-snapshot.json").write_text(json.dumps({"documents": docs}))

    def test_full_bundle_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_bundle(root)
            self.assertEqual(verify(root), [])

    def test_modified_policy_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_bundle(root)
            (root / "Gemma-Terms-Official.html").write_bytes(b"<html>modified</html>")
            issues = verify(root)
            self.assertTrue(any("MISMATCH" in x for x in issues))

    def test_missing_bundle_fails(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("LEGAL_SNAPSHOT_MANIFEST_UNREADABLE", verify(Path(d)))


if __name__ == "__main__":
    unittest.main()
