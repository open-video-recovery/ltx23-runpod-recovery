import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_embedded_bundle import prepare
from render_embedded_dockerfile import render


class DockerfileRenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        models = root / "models"
        sample = b"NOT A REAL MODEL" * 500
        filename = "checkpoints/example.safetensors"
        target = models / filename
        target.parent.mkdir(parents=True)
        target.write_bytes(sample)
        lock = root / "lock.json"
        lock.write_text(json.dumps({"models": [{
            "key": "example", "target": filename,
            "sha256": hashlib.sha256(sample).hexdigest(),
            "size": len(sample),
        }]}))
        self.context = root / "stage"
        prepare(lock, models, self.context, chunk_bytes=2048)

    def test_render_layered_dockerfile_is_explicitly_experimental(self):
        output = render(self.context, ROOT, test_only=True)
        content = output.read_text()
        self.assertGreaterEqual(content.count("COPY model_chunks/example/part-"), 3)
        self.assertIn("restore_model_bundle.py", content)
        self.assertNotIn("rirukachan/nend-ltx23", content)
        self.assertIn("NOT GPU validated", content)
        self.assertTrue((self.context / "NOTICE-THIRD-PARTY.md").is_file())
        self.assertTrue((self.context / "runtime" / "restore_model_bundle.py").is_file())

    def test_actual_release_requires_workflow(self):
        if (ROOT / "workflows" / "i2v.json").exists():
            self.skipTest("An audited workflow has been added in a later phase")
        with self.assertRaisesRegex(ValueError, "AUDITED_I2V_WORKFLOW_REQUIRED"):
            render(self.context, ROOT, test_only=False)


if __name__ == "__main__":
    unittest.main()
