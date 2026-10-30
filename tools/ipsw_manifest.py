#!/usr/bin/env python3
"""Read-only IPSW BuildManifest inspector and comparator.

Uses only the Python standard library. Does not extract, modify, or flash firmware.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import sys
import zipfile
from pathlib import Path
from typing import Any

MANIFEST_NAME = "BuildManifest.plist"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_manifest(path: Path) -> tuple[dict[str, Any], str]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if MANIFEST_NAME not in names:
            raise ValueError(f"{path}: {MANIFEST_NAME} not found at IPSW archive root")
        raw = archive.read(MANIFEST_NAME)
    manifest = plistlib.loads(raw)
    if not isinstance(manifest, dict):
        raise ValueError(f"{path}: BuildManifest is not a plist dictionary")
    return manifest, hashlib.sha256(raw).hexdigest()


def identities_for(manifest: dict[str, Any], product: str) -> list[dict[str, Any]]:
    matches = []
    for identity in manifest.get("BuildIdentities", []):
        info = identity.get("Info", {})
        if info.get("DeviceClass") == product:
            matches.append(identity)
    return matches


def summarize(path: Path, product: str) -> dict[str, Any]:
    manifest, manifest_hash = read_manifest(path)
    identities = identities_for(manifest, product)
    if not identities:
        available = sorted({
            str(i.get("Info", {}).get("DeviceClass", "unknown"))
            for i in manifest.get("BuildIdentities", [])
        })
        raise ValueError(
            f"{path}: no build identity for {product}; "
            f"manifest device classes include: {', '.join(available)}"
        )

    components: dict[str, dict[str, Any]] = {}
    for identity_index, identity in enumerate(identities):
        for name, entry in identity.get("Manifest", {}).items():
            info = entry.get("Info", {}) if isinstance(entry, dict) else {}
            components[f"{identity_index}:{name}"] = {
                "path": entry.get("Path") if isinstance(entry, dict) else None,
                "digest": entry.get("Digest").hex()
                    if isinstance(entry, dict) and isinstance(entry.get("Digest"), bytes)
                    else None,
                "partial_digest": entry.get("PartialDigest").hex()
                    if isinstance(entry, dict) and isinstance(entry.get("PartialDigest"), bytes)
                    else None,
                "is_restore": info.get("IsRestore"),
                "is_personalized": info.get("IsPersonalized"),
            }

    return {
        "file": str(path),
        "file_size": path.stat().st_size,
        "file_sha256": sha256_file(path),
        "manifest_sha256": manifest_hash,
        "product_version": manifest.get("ProductVersion"),
        "product_build_version": manifest.get("ProductBuildVersion"),
        "product_name": manifest.get("ProductName"),
        "product": product,
        "identity_count": len(identities),
        "components": components,
    }


def compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    a, b = left["components"], right["components"]
    keys_a, keys_b = set(a), set(b)
    changed = []
    for key in sorted(keys_a & keys_b):
        if a[key] != b[key]:
            changed.append({
                "component": key,
                "baseline": a[key],
                "comparison": b[key],
            })
    return {
        "baseline": {k: v for k, v in left.items() if k != "components"},
        "comparison": {k: v for k, v in right.items() if k != "components"},
        "component_summary": {
            "baseline_count": len(keys_a),
            "comparison_count": len(keys_b),
            "added": sorted(keys_b - keys_a),
            "removed": sorted(keys_a - keys_b),
            "changed": changed,
            "unchanged_count": len(keys_a & keys_b) - len(changed),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_parser = sub.add_parser("inspect", help="inspect one IPSW BuildManifest")
    inspect_parser.add_argument("ipsw", type=Path)
    diff_parser = sub.add_parser("diff", help="compare two IPSW BuildManifests")
    diff_parser.add_argument("baseline", type=Path)
    diff_parser.add_argument("comparison", type=Path)
    for p in (inspect_parser, diff_parser):
        p.add_argument("--product", default="iPhone17,3")
        p.add_argument("--json", type=Path, help="also write the report to this path")

    args = parser.parse_args()
    try:
        if args.command == "inspect":
            report = summarize(args.ipsw, args.product)
        else:
            baseline = summarize(args.baseline, args.product)
            comparison = summarize(args.comparison, args.product)
            report = compare(baseline, comparison)

        rendered = json.dumps(report, indent=2, sort_keys=True)
        print(rendered)
        if args.json:
            args.json.write_text(rendered + "\n", encoding="utf-8")
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, plistlib.InvalidFileException) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
