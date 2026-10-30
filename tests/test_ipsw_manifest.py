import plistlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.ipsw_manifest import diff, inspect


def sample_manifest(build: str, digest: bytes) -> dict:
    return {
        "ProductVersion": "27.0.1",
        "ProductBuildVersion": build,
        "BuildIdentities": [{
            "Info": {"DeviceClass": "D47AP"},
            "Manifest": {
                "KernelCache": {
                    "Path": "kernelcache.test",
                    "Digest": digest,
                    "Info": {"IsRestore": True},
                }
            },
        }],
    }


def make_ipsw(path: Path, build: str, digest: bytes) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("BuildManifest.plist", plistlib.dumps(sample_manifest(build, digest)))


class ManifestToolTests(unittest.TestCase):
    def test_inspect_reads_expected_device_class(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.ipsw"
            make_ipsw(path, "TEST1", b"one")
            result = inspect(path, "D47AP")
            self.assertEqual(result["product_build_version"], "TEST1")
            self.assertIn("0:KernelCache", result["components"])
            self.assertEqual(result["source_kind"], "ipsw")

    def test_diff_reports_digest_change(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.ipsw"
            second = Path(directory) / "second.ipsw"
            make_ipsw(first, "TEST1", b"one")
            make_ipsw(second, "TEST2", b"two")
            result = diff(inspect(first, "D47AP"), inspect(second, "D47AP"))
            self.assertEqual(len(result["components"]["changed"]), 1)

    def test_inspect_accepts_extracted_manifest_without_full_ipsw(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "BuildManifest.plist"
            path.write_bytes(plistlib.dumps(sample_manifest("TEST1", b"one")))
            result = inspect(path, "D47AP")
            self.assertEqual(result["source_kind"], "manifest")
            self.assertIsNone(result["source_size"])
            self.assertIsNotNone(result["source_sha256"])
            self.assertEqual(result["product_build_version"], "TEST1")

    def test_wrong_device_class_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.ipsw"
            make_ipsw(path, "TEST1", b"one")
            with self.assertRaises(ValueError):
                inspect(path, "NOT_A_DEVICE")


if __name__ == "__main__":
    unittest.main()
