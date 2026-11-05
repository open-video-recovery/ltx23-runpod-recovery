"""CPU-only full OCI model staging tests; no network, Docker or real weights."""
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "runtime"))
from prepare_embedded_bundle import prepare
from restore_model_bundle import restore


class BundledModelStages(unittest.TestCase):
    def fixture(self, base: Path):
        models = base / "models"
        entries = []
        for key, dest, data in [
            ("checkpoint", "checkpoints/fake-model.safetensors", b"model-fake" * 412),
            ("gemma", "text_encoders/fake-encoder.safetensors", b"gemma-fake" * 119),
        ]:
            source = models / dest
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(data)
            entries.append({"key": key, "target": dest, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)})
        lock = base / "models.lock.json"
        lock.write_text(json.dumps({"models": entries}))
        return lock, models

    def test_prepare_and_restore_offline(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            lock, models = self.fixture(base)
            out = base / "context"
            result = prepare(lock, models, out, chunk_bytes=151)
            self.assertEqual(result["schema"], "full-model-embedded-oci-staging-v1")
            self.assertEqual(len(result["models"]), 2)
            self.assertGreater(len(list(out.rglob("part-*.bin"))), 3)
            restored = base / "restored"
            self.assertEqual(len(restore(out, restored)), 2)
            for entry in result["models"]:
                self.assertEqual((restored / entry["target"]).read_bytes(),
                                 (models / entry["target"]).read_bytes())
            self.assertEqual(len(restore(out, restored)), 2)

    def test_mismatched_input_fails_before_emitting_parts(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            lock, models = self.fixture(base)
            (models / "checkpoints/fake-model.safetensors").write_bytes(b"tampered")
            out = base / "context"
            with self.assertRaises(ValueError):
                prepare(lock, models, out, chunk_bytes=128)
            self.assertFalse(out.exists())

    def test_missing_chunk_fails_restore(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            lock, models = self.fixture(base)
            out = base / "context"
            prepare(lock, models, out, chunk_bytes=200)
            (out / "model_chunks" / "gemma" / "part-0000.bin").unlink()
            with self.assertRaisesRegex(ValueError, "CHUNK_MISSING"):
                restore(out, base / "restored")


if __name__ == "__main__":
    unittest.main()
