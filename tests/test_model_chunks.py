import hashlib
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from model_chunks import split, assemble


class ModelChunksTests(unittest.TestCase):
    def test_split_and_assemble(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            original = root / "source.safetensors"
            raw = b"abcdef" * 601
            original.write_bytes(raw)
            out = root / "parts"
            manifest = split(original, out, chunk_bytes=1400, expected_sha=hashlib.sha256(raw).hexdigest())
            result = root / "restored.safetensors"
            self.assertEqual(assemble(manifest, result)["status"], "VERIFIED")
            self.assertEqual(result.read_bytes(), raw)
            self.assertEqual(assemble(manifest, result)["status"], "ALREADY_VERIFIED")

    def test_bad_chunk_fails_closed(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.safetensors"
            source.write_bytes(b"abcdef" * 100)
            manifest = split(source, root / "parts", chunk_bytes=100)
            (root / "parts" / "part-0001.bin").write_bytes(b"x" * 100)
            result = root / "out.safetensors"
            with self.assertRaisesRegex(ValueError, "CHUNK_SHA256_MISMATCH"):
                assemble(manifest, result)
            self.assertFalse(result.exists())

    def test_required_sha_rejects_modified_source(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.safetensors"
            source.write_bytes(b"fake")
            with self.assertRaisesRegex(ValueError, "MODEL_SHA256_MISMATCH"):
                split(source, root / "parts", chunk_bytes=3, expected_sha="0" * 64)


if __name__ == "__main__":
    unittest.main()
