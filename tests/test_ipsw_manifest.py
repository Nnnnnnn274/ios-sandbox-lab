import plistlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.ipsw_manifest import diff, inspect, load_manifest


def sample_manifest(build: str, digest: bytes = b"one", device_class: str = "D47AP") -> dict:
    return {
        "ProductVersion": "27.0.1",
        "ProductBuildVersion": build,
        "ProductName": "iPhone OS",
        "BuildIdentities": [{
            "Info": {"DeviceClass": device_class, "Variant": "Customer Upgrade Install"},
            "Manifest": {
                "KernelCache": {
                    "Path": "kernelcache.test",
                    "Digest": digest,
                    "Info": {"IsRestore": True},
                }
            },
        }],
    }


def make_ipsw(path: Path, build: str, digest: bytes = b"one", device_class: str = "D47AP") -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("BuildManifest.plist", plistlib.dumps(sample_manifest(build, digest, device_class)))


class ManifestToolTests(unittest.TestCase):
    def test_inspect_reads_expected_device_class_and_hashes_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.ipsw"
            make_ipsw(path, "TEST1")
            result = inspect(path, "D47AP")
            self.assertEqual(result["product_build_version"], "TEST1")
            self.assertIn("D47AP|Customer Upgrade Install|||#0:KernelCache", result["components"])
            self.assertEqual(result["source_kind"], "ipsw")
            self.assertEqual(len(result["source_sha256"]), 64)
            self.assertEqual(result["identities"][0]["device_class"], "D47AP")

    def test_diff_reports_digest_change(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.ipsw"
            second = Path(directory) / "second.ipsw"
            make_ipsw(first, "TEST1", b"one")
            make_ipsw(second, "TEST2", b"two")
            result = diff(inspect(first, "D47AP"), inspect(second, "D47AP"))
            self.assertEqual(len(result["components"]["changed"]), 1)
            self.assertEqual(result["schema_version"], 1)

    def test_inspect_accepts_extracted_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "BuildManifest.plist"
            path.write_bytes(plistlib.dumps(sample_manifest("TEST1")))
            result = inspect(path, "D47AP")
            self.assertEqual(result["source_kind"], "manifest")
            self.assertIsNone(result["source_size"])
            self.assertEqual(len(result["source_sha256"]), 64)

    def test_wrong_device_class_fails_with_known_classes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.ipsw"
            make_ipsw(path, "TEST1")
            with self.assertRaisesRegex(ValueError, "D47AP"):
                inspect(path, "NOT_A_DEVICE")

    def test_empty_device_class_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.ipsw"
            make_ipsw(path, "TEST1")
            with self.assertRaisesRegex(ValueError, "must not be empty"):
                inspect(path, " ")

    def test_invalid_zip_is_reported_as_value_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.ipsw"
            path.write_bytes(b"not a zip")
            with self.assertRaisesRegex(ValueError, "not a valid ZIP"):
                load_manifest(path)

    def test_missing_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.ipsw"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("other.txt", "no manifest")
            with self.assertRaisesRegex(ValueError, "expected exactly one"):
                load_manifest(path)

    def test_duplicate_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.ipsw"
            with zipfile.ZipFile(path, "w") as archive:
                raw = plistlib.dumps(sample_manifest("TEST1"))
                archive.writestr("BuildManifest.plist", raw)
                archive.writestr("BuildManifest.plist", raw)
            with self.assertRaisesRegex(ValueError, "exactly one"):
                load_manifest(path)

    def test_malformed_plist_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "BuildManifest.plist"
            path.write_bytes(b"not plist")
            with self.assertRaisesRegex(ValueError, "invalid BuildManifest plist"):
                load_manifest(path)

    def test_oversized_extracted_manifest_is_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "BuildManifest.plist"
            with path.open("wb") as stream:
                stream.truncate(64 * 1024 * 1024 + 1)
            with self.assertRaisesRegex(ValueError, "64 MiB safety limit"):
                load_manifest(path)

    def test_diff_rejects_different_device_classes(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.ipsw"
            second = Path(directory) / "second.ipsw"
            make_ipsw(first, "TEST1", device_class="D47AP")
            make_ipsw(second, "TEST2", device_class="D48AP")
            with self.assertRaisesRegex(ValueError, "different device classes"):
                diff(inspect(first, "D47AP"), inspect(second, "D48AP"))


if __name__ == "__main__":
    unittest.main()
