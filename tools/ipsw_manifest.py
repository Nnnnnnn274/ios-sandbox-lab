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
MAX_MANIFEST_SIZE = 64 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_manifest(path: Path) -> tuple[bytes, str]:
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".plist":
        size = path.stat().st_size
        if size > MAX_MANIFEST_SIZE:
            raise ValueError(f"{path}: manifest exceeds the 64 MiB safety limit")
        return path.read_bytes(), "manifest"

    try:
        with zipfile.ZipFile(path) as archive:
            matches = [item for item in archive.infolist() if item.filename == MANIFEST]
            if len(matches) != 1:
                raise ValueError(
                    f"{path}: expected exactly one {MANIFEST} at archive root; found {len(matches)}"
                )
            if matches[0].file_size > MAX_MANIFEST_SIZE:
                raise ValueError(f"{path}: {MANIFEST} exceeds the 64 MiB safety limit")
            return archive.read(matches[0]), "ipsw"
    except zipfile.BadZipFile as exc:
        raise ValueError(f"{path}: not a valid ZIP/IPSW archive") from exc


def load_manifest(path: Path) -> tuple[dict[str, Any], str, str]:
    raw, source_kind = _read_manifest(path)
    try:
        data = plistlib.loads(raw)
    except (plistlib.InvalidFileException, ValueError, TypeError) as exc:
        raise ValueError(f"{path}: invalid BuildManifest plist: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: manifest root must be a dictionary")
    identities = data.get("BuildIdentities")
    if not isinstance(identities, list) or not identities:
        raise ValueError(f"{path}: BuildIdentities must be a non-empty array")
    return data, sha256_bytes(raw), source_kind


def _identity_info(identity: Any, path: Path, index: int) -> dict[str, Any]:
    if not isinstance(identity, dict):
        raise ValueError(f"{path}: BuildIdentities[{index}] must be a dictionary")
    info = identity.get("Info")
    components = identity.get("Manifest")
    if not isinstance(info, dict):
        raise ValueError(f"{path}: BuildIdentities[{index}].Info must be a dictionary")
    if not isinstance(components, dict):
        raise ValueError(f"{path}: BuildIdentities[{index}].Manifest must be a dictionary")
    return info


def inspect(path: Path, device_class: str) -> dict[str, Any]:
    if not device_class or not device_class.strip():
        raise ValueError("device_class must not be empty")
    manifest, manifest_hash, source_kind = load_manifest(path)
    all_identities = manifest["BuildIdentities"]
    identities: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    known: set[str] = set()

    for index, identity in enumerate(all_identities):
        info = _identity_info(identity, path, index)
        value = info.get("DeviceClass")
        if value is not None:
            known.add(str(value))
        if str(value or "").casefold() == device_class.casefold():
            identities.append((index, identity, info))

    if not identities:
        raise ValueError(
            f"{path}: no identity for DeviceClass={device_class}; "
            f"manifest contains: {', '.join(sorted(known)) or '(none)'}"
        )

    components: dict[str, Any] = {}
    identity_records: list[dict[str, Any]] = []
    identity_key_counts: dict[str, int] = {}
    for identity_index, identity, info in identities:
        identity_records.append({
            "index": identity_index,
            "device_class": info.get("DeviceClass"),
            "variant": info.get("Variant"),
            "restore_behavior": info.get("RestoreBehavior"),
            "ap_board_id": info.get("ApBoardID"),
            "ap_chip_id": info.get("ApChipID"),
        })
        stable_identity = "|".join(
            str(info.get(field) or "")
            for field in ("DeviceClass", "Variant", "RestoreBehavior", "ApBoardID", "ApChipID")
        )
        duplicate_number = identity_key_counts.get(stable_identity, 0)
        identity_key_counts[stable_identity] = duplicate_number + 1
        stable_identity = f"{stable_identity}#{duplicate_number}"
        for component, entry in identity["Manifest"].items():
            if not isinstance(entry, dict):
                raise ValueError(
                    f"{path}: identity {identity_index} component {component!r} must be a dictionary"
                )
            entry_info = entry.get("Info", {})
            if not isinstance(entry_info, dict):
                raise ValueError(
                    f"{path}: identity {identity_index} component {component!r} Info must be a dictionary"
                )
            digest = entry.get("Digest")
            partial = entry.get("PartialDigest")
            if digest is not None and not isinstance(digest, bytes):
                raise ValueError(f"{path}: {component}.Digest must be bytes")
            if partial is not None and not isinstance(partial, bytes):
                raise ValueError(f"{path}: {component}.PartialDigest must be bytes")
            key = f"{stable_identity}:{component}"
            components[key] = {
                "identity_index": identity_index,
                "component": component,
                "path": entry.get("Path"),
                "digest": digest.hex() if digest is not None else None,
                "partial_digest": partial.hex() if partial is not None else None,
                "is_restore": entry_info.get("IsRestore"),
                "is_personalized": entry_info.get("IsPersonalized"),
            }

    return {
        "source": str(path),
        "source_kind": source_kind,
        "source_size": path.stat().st_size if source_kind == "ipsw" else None,
        "source_sha256": sha256_file(path) if source_kind == "ipsw" else sha256_bytes(path.read_bytes()),
        "manifest_sha256": manifest_hash,
        "product_version": manifest.get("ProductVersion"),
        "product_build_version": manifest.get("ProductBuildVersion"),
        "product_name": manifest.get("ProductName"),
        "device_class": device_class,
        "identity_count": len(identities),
        "identities": identity_records,
        "components": components,
    }


def diff(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    if a.get("device_class") != b.get("device_class"):
        raise ValueError("cannot compare manifests inspected for different device classes")
    left, right = a["components"], b["components"]
    lk, rk = set(left), set(right)
    changed = [
        {"component": key, "baseline": left[key], "comparison": right[key]}
        for key in sorted(lk & rk) if left[key] != right[key]
    ]
    warnings = []
    for field in ("product_name", "device_class"):
        if a.get(field) != b.get(field):
            warnings.append(f"{field} differs between inputs")
    return {
        "schema_version": 1,
        "baseline": {k: v for k, v in a.items() if k != "components"},
        "comparison": {k: v for k, v in b.items() if k != "components"},
        "warnings": warnings,
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
    one = commands.add_parser("inspect", help="inspect one IPSW or extracted BuildManifest.plist")
    one.add_argument("input", type=Path)
    two = commands.add_parser("diff", help="compare two IPSWs or extracted BuildManifest.plist files")
    two.add_argument("baseline", type=Path)
    two.add_argument("comparison", type=Path)
    for command in (one, two):
        command.add_argument("--device-class", default="D47AP",
                             help="BuildManifest Info.DeviceClass (default: D47AP)")
        command.add_argument("--json", type=Path, help="also write JSON to this path")
    args = parser.parse_args()

    try:
        if args.mode == "inspect":
            report = inspect(args.input, args.device_class)
        else:
            report = diff(
                inspect(args.baseline, args.device_class),
                inspect(args.comparison, args.device_class),
            )
        output = json.dumps(report, indent=2, sort_keys=True)
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(output + "\n", encoding="utf-8")
        print(output)
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, plistlib.InvalidFileException) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
