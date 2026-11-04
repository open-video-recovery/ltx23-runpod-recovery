"""CPU-only checks: no model downloads, Docker daemon or GPU required."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "runtime"))
from verify_models import verify_one
from inspect_workflow import inspect, REQUIRED, STAGE_1, STAGE_2
from worker import patch_workflow


class TestOffline(unittest.TestCase):
    def test_model_lock_metadata(self):
        lock = json.loads((ROOT / "models.lock.json").read_text())
        self.assertEqual(len(lock["models"]), 4)
        for entry in lock["models"]:
            self.assertEqual(len(entry["sha256"]), 64)
            self.assertEqual(len(entry["revision"]), 40)
            self.assertGreater(entry["size"], 1000000)

    def test_verify_hash_and_size(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / "checkpoints" / "fixture.safetensors"
            file.parent.mkdir()
            data = b"example asset only"
            file.write_bytes(data)
            entry = {
                "key": "fixture", "target": "checkpoints/fixture.safetensors",
                "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            }
            self.assertEqual(verify_one(entry, root)["status"], "PASS")
            file.write_bytes(b"corrupt")
            with self.assertRaises(ValueError):
                verify_one(entry, root)

    def test_workflow_node_and_sigma_check(self):
        graph = {key: {"class_type": value, "inputs": {}} for key, value in REQUIRED.items()}
        graph["306"] = {"class_type": "ManualSigmas", "inputs": {"sigmas": STAGE_1}}
        graph["281"] = {"class_type": "ManualSigmas", "inputs": {"sigmas": STAGE_2}}
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "graph.json"
            file.write_text(json.dumps(graph))
            result = inspect(file)
            self.assertEqual(result["structure"], "PASS")
            self.assertFalse(result["original_exact_match"])

    def test_patch_workflow(self):
        template = {
            "1": {"class_type": "LoadImage", "inputs": {"image": "__INPUT_IMAGE__"}},
            "2": {"class_type": "SomeEncode", "inputs": {"text": "__PROMPT__", "seed": "__SEED__"}},
            "3": {"class_type": "SaveVideo", "inputs": {"video": ["2", 0]}},
        }
        result = patch_workflow(template, "hello", "sample.jpg", 42)
        self.assertEqual(result["1"]["inputs"]["image"], "sample.jpg")
        self.assertEqual(result["2"]["inputs"]["seed"], 42)
        self.assertEqual(template["1"]["inputs"]["image"], "__INPUT_IMAGE__")

    def test_missing_placeholder_rejected(self):
        with self.assertRaises(ValueError):
            patch_workflow({"3": {"class_type": "SaveVideo", "inputs": {}}}, "x", "x.jpg", 2)


if __name__ == "__main__":
    unittest.main()
