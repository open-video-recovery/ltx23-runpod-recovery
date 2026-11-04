"""Offline tests for the model-free GHCR diagnostic image."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from ghcr_smoke import handler


class TestGhcrSmoke(unittest.TestCase):
    def test_diagnostics(self):
        result = handler({"input": {"task": "diagnostics"}})
        self.assertEqual(result["status"], "OK")
        self.assertIs(result["ready_for_video"], False)
        self.assertIs(result["gpu_generated"], False)
        self.assertIs(result["has_ltx_models"], False)

    def test_generate_fail_closed(self):
        result = handler({"input": {"task": "i2v", "prompt": "x"}})
        self.assertEqual(result["error"], "DIAGNOSTICS_ONLY_NO_VIDEO_GENERATION")

    def test_missing_input(self):
        self.assertEqual(handler({})["error"], "INPUT_OBJECT_REQUIRED")


if __name__ == "__main__":
    unittest.main()
