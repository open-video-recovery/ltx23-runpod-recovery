import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from collect_official_policies import DOCUMENTS, verify_doc


class PolicyFetchValidationTests(unittest.TestCase):
    def test_valid_pdf_marker(self):
        sample = b"%PDF-1.7" + b" example" * 100
        verify_doc(DOCUMENTS[0], sample)

    def test_corrupt_pdf_rejected(self):
        with self.assertRaisesRegex(ValueError, "POLICY_DOCUMENT_FORMAT_INVALID"):
            verify_doc(DOCUMENTS[0], b"NOT A PDF" * 100)

    def test_google_page_missing_terms_rejected(self):
        with self.assertRaisesRegex(ValueError, "POLICY_DOCUMENT_MISSING_REQUIRED_MARKER"):
            verify_doc(DOCUMENTS[1], b"<html>just a login page</html>" * 100)

    def test_valid_policy_markers(self):
        body = b"Gemma Prohibited Use Policy | sexually explicit" + b" text" * 105
        verify_doc(DOCUMENTS[2], body)


if __name__ == "__main__":
    unittest.main()
