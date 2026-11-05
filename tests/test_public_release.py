from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_public_release import materials_check, release_check, REQUIRED_NOTICE_FILES


class StandardDistributionPackagingTests(unittest.TestCase):
    def test_included_license_texts_and_gemma_notice(self):
        self.assertEqual(materials_check(), [])

    def test_dummy_fixture_scope_is_acceptable(self):
        self.assertEqual(release_check(mode="fixture"), [])

    def test_full_public_checks_common_legal_notice_packaging(self):
        self.assertEqual(release_check(mode="full-public"), [])

    def test_notice_and_readme_are_required(self):
        self.assertIn("NOTICE-THIRD-PARTY.md", REQUIRED_NOTICE_FILES)
        self.assertIn("README.md", REQUIRED_NOTICE_FILES)


if __name__ == "__main__":
    unittest.main()
