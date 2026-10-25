from __future__ import annotations

import base64
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SOURCE_ROOT))

from file_operations import (
    decrypt_file,
    decrypted_output_path,
    delete_source_after_success,
    encrypt_file,
)


PASSWORD = "quickcrypt-fixture-password"
LEGACY_PLAINTEXT = base64.b64decode(
    (FIXTURES / "legacy-quickcrypt-v2.plaintext.b64").read_text()
)


class FileOperationsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_plaintext(self, name: str = "sample.txt", content: bytes = LEGACY_PLAINTEXT) -> Path:
        path = self.root / name
        path.write_bytes(content)
        return path

    def legacy_ciphertext(self) -> Path:
        path = self.root / "legacy.aes"
        path.write_bytes(base64.b64decode((FIXTURES / "legacy-quickcrypt-v2.aes.b64").read_text()))
        return path

    def assert_no_temporary_output(self) -> None:
        self.assertEqual(list(self.root.glob(".*.tmp")), [])

    def test_decrypts_historical_quickcrypt_fixture(self) -> None:
        encrypted = self.legacy_ciphertext()

        output = decrypt_file(encrypted, PASSWORD)

        self.assertEqual(output.read_bytes(), LEGACY_PLAINTEXT)

    def test_encrypt_and_decrypt_round_trip_unicode_filename(self) -> None:
        source = self.write_plaintext("نمونه file.txt")

        encrypted = encrypt_file(source, PASSWORD)
        source.unlink()
        decrypted = decrypt_file(encrypted, PASSWORD)

        self.assertEqual(decrypted, source)
        self.assertEqual(decrypted.read_bytes(), LEGACY_PLAINTEXT)

    def test_large_streamed_input_round_trip(self) -> None:
        content = (b"QuickCrypt streamed data\n" * 8192) + b"tail"
        source = self.write_plaintext("large.bin", content)

        encrypted = encrypt_file(source, PASSWORD)
        source.unlink()
        decrypted = decrypt_file(encrypted, PASSWORD)

        self.assertEqual(decrypted.read_bytes(), content)

    def test_empty_file_round_trip(self) -> None:
        source = self.write_plaintext("empty.bin", b"")

        encrypted = encrypt_file(source, PASSWORD)
        source.unlink()
        decrypted = decrypt_file(encrypted, PASSWORD)

        self.assertEqual(decrypted.read_bytes(), b"")

    def test_wrong_password_keeps_input_and_creates_no_plaintext(self) -> None:
        encrypted = self.legacy_ciphertext()

        with self.assertRaises(ValueError):
            decrypt_file(encrypted, "wrong-password")

        self.assertTrue(encrypted.exists())
        self.assertFalse((self.root / "legacy").exists())
        self.assert_no_temporary_output()

    def test_truncated_and_tampered_ciphertext_create_no_plaintext(self) -> None:
        encrypted = self.legacy_ciphertext()
        for name, content in {
            "truncated.aes": encrypted.read_bytes()[:-20],
            "tampered.aes": encrypted.read_bytes()[:-1] + b"\x00",
        }.items():
            candidate = self.root / name
            candidate.write_bytes(content)
            with self.assertRaises(ValueError):
                decrypt_file(candidate, PASSWORD)
            self.assertFalse(candidate.with_suffix("").exists())

        self.assert_no_temporary_output()

    def test_aes_crypt_v2_final_size_byte_is_not_authenticated(self) -> None:
        encrypted = self.legacy_ciphertext()
        modified = bytearray(encrypted.read_bytes())
        modified[-33] = 0
        encrypted.write_bytes(modified)

        output = decrypt_file(encrypted, PASSWORD)

        self.assertTrue(output.read_bytes().startswith(LEGACY_PLAINTEXT))
        self.assertNotEqual(output.read_bytes(), LEGACY_PLAINTEXT)

    def test_refuses_existing_destination_and_keeps_it_unchanged(self) -> None:
        source = self.write_plaintext()
        destination = source.with_name(f"{source.name}.aes")
        destination.write_bytes(b"existing ciphertext")

        with self.assertRaises(FileExistsError):
            encrypt_file(source, PASSWORD)

        self.assertEqual(destination.read_bytes(), b"existing ciphertext")
        self.assertTrue(source.exists())
        self.assert_no_temporary_output()

    def test_refuses_existing_plaintext_destination_and_keeps_it_unchanged(self) -> None:
        encrypted = self.legacy_ciphertext()
        plaintext = self.root / "legacy"
        plaintext.write_bytes(b"do not overwrite")

        with self.assertRaises(FileExistsError):
            decrypt_file(encrypted, PASSWORD)

        self.assertEqual(plaintext.read_bytes(), b"do not overwrite")
        self.assertTrue(encrypted.exists())
        self.assert_no_temporary_output()

    def test_source_is_deleted_only_when_requested_after_success(self) -> None:
        source = self.write_plaintext()

        encrypt_file(source, PASSWORD)
        self.assertTrue(source.exists())
        delete_source_after_success(source, False)
        self.assertTrue(source.exists())
        delete_source_after_success(source, True)
        self.assertFalse(source.exists())

    def test_rejects_non_aes_decrypt_input_without_creating_output(self) -> None:
        source = self.write_plaintext("not-encrypted.txt")

        with self.assertRaises(ValueError):
            decrypt_file(source, PASSWORD)

        self.assertTrue(source.exists())
        self.assertEqual(decrypted_output_path(self.root / "example.AES"), self.root / "example")


if __name__ == "__main__":
    unittest.main()
