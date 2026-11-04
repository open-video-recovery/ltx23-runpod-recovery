from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_public_release import materials_check, release_check, REQUIRED_GATE_NAMES


class PublicReleaseGateTests(unittest.TestCase):
    def test_included_license_texts_and_gemma_notice(self):
        self.assertEqual(materials_check(), [])

    def test_dummy_fixture_scope_is_acceptable(self):
        self.assertEqual(release_check(mode="fixture"), [])

    def test_actual_public_model_release_is_blocked(self):
        errors = release_check(mode="full-public")
        self.assertIn("PUBLIC_MODEL_RELEASE_BLOCKED", errors)
        self.assertIn("UNVERIFIED_RELEASE_GATE:binding_downstream_acceptance_mechanism", errors)
        self.assertIn("UNVERIFIED_RELEASE_GATE:restricted_recipient_export_compliance", errors)

    def test_release_requires_complete_evidence(self):
        self.assertGreaterEqual(len(REQUIRED_GATE_NAMES), 8)


if __name__ == "__main__":
    unittest.main()
