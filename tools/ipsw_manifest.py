#!/usr/bin/env python3
"""Read-only IPSW BuildManifest inspector/comparator (Python standard library only)."""
from __future__ import annotations
import argparse
import hashlib
import json
import plistlib
import sys
import zipfile
from pathlib import Path
from typing import Any

MANIFEST = "BuildManifest.plist"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(path: Path) -> tuple[dict[str, Any], str]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with zipfile.ZipFile(path) as archive:
        if MANIFEST not in archive.namelist():
            raise ValueError(f"{path}: {MANIFEST} is missing at archive root")
        raw = archive.read(MANIFEST)
    data = plistlib.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: manifest root is not a dictionary")
    return data, hashlib.sha256(raw).hexdigest()


def inspect(path: Path, device_class: str) -> dict[str, Any]:
    manifest, manifest_hash = load_manifest(path)
    identities = [
        item for item in manifest.get("BuildIdentities", [])
        if item.get("Info", {}).get("DeviceClass") == device_class
    ]
    if not identities:
        known = sorted({
            str(item.get("Info", {}).get("DeviceClass", "unknown"))
            for item in manifest.get("BuildIdentities", [])
        })
        raise ValueError(
            f"{path}: no identity for DeviceClass={device_class}; "
            f"manifest contains: {', '.join(known)}"
        )

    components: dict[str, Any] = {}
    for identity_index, identity in enumerate(identities):
        for component, entry in identity.get("Manifest", {}).items():
            if not isinstance(entry, dict):
                continue
            info = entry.get("Info", {})
            digest = entry.get("Digest")
            partial = entry.get("PartialDigest")
            components[f"{identity_index}:{component}"] = {
                "path": entry.get("Path"),
                "digest": digest.hex() if isinstance(digest, bytes) else None,
                "partial_digest": partial.hex() if isinstance(partial, bytes) else None,
                "is_restore": info.get("IsRestore"),
                "is_personalized": info.get("IsPersonalized"),
            }

    return {
        "ipsw": str(path),
        "ipsw_size": path.stat().st_size,
        "ipsw_sha256": sha256_file(path),
        "manifest_sha256": manifest_hash,
        "product_version": manifest.get("ProductVersion"),
        "product_build_version": manifest.get("ProductBuildVersion"),
        "product_name": manifest.get("ProductName"),
        "device_class": device_class,
        "identity_count": len(identities),
        "components": components,
    }


def diff(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    left, right = a["components"], b["components"]
    lk, rk = set(left), set(right)
    changed = [
        {"component": key, "baseline": left[key], "comparison": right[key]}
        for key in sorted(lk & rk) if left[key] != right[key]
    ]
    return {
        "baseline": {k: v for k, v in a.items() if k != "components"},
        "comparison": {k: v for k, v in b.items() if k != "components"},
        "components": {
            "baseline_count": len(lk),
            "comparison_count": len(rk),
            "added": sorted(rk - lk),
            "removed": sorted(lk - rk),
            "changed": changed,
            "unchanged_count": len(lk & rk) - len(changed),
        },
        "interpretation": (
            "Manifest differences are triage leads only. They do not establish "
            "a vulnerability, patch, reachable attack surface, or exploitability."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    one = commands.add_parser("inspect", help="inspect one IPSW")
    one.add_argument("ipsw", type=Path)
    two = commands.add_parser("diff", help="compare two IPSWs")
    two.add_argument("baseline", type=Path)
    two.add_argument("comparison", type=Path)
    for command in (one, two):
        command.add_argument("--device-class", default="D47AP",
                             help="BuildManifest Info.DeviceClass (default: D47AP)")
        command.add_argument("--json", type=Path, help="also write JSON to this path")
    args = parser.parse_args()

    try:
        if args.mode == "inspect":
            report = inspect(args.ipsw, args.device_class)
        else:
            report = diff(
                inspect(args.baseline, args.device_class),
                inspect(args.comparison, args.device_class),
            )
        output = json.dumps(report, indent=2, sort_keys=True)
        print(output)
        if args.json:
            args.json.write_text(output + "\n", encoding="utf-8")
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, plistlib.InvalidFileException) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
