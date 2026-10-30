# iOS Sandbox Lab

Read-only iOS firmware research for **iPhone 16 (ProductType `iPhone17,3`, A18)**.

## Scope

The project begins with reproducible IPSW metadata inspection and BuildManifest comparison for defensive security research. It does **not** contain a jailbreak, sandbox escape, privilege-escalation payload, persistence mechanism, or device-modification workflow.

A manifest difference is a lead for further review, not proof of a vulnerability or an exploitable patch.

## Comparison target

| Role | iOS | Build |
|---|---:|---:|
| Baseline | 27.0.1 | 24A446 |
| Comparison | 27.2 | 24B119 |

The CLI defaults to BuildManifest `Info.DeviceClass=D47AP`, which is distinct from the marketing ProductType `iPhone17,3`. Verify the identity in both manifests before interpreting a report. Firmware build identifiers and signing status should be independently verified against trusted sources at research time.

## Requirements

- Python 3.10+
- IPSW files from a trusted source
- No third-party Python packages

## Commands

Inspect an IPSW:

```sh
python3 tools/ipsw_manifest.py inspect path/to/file.ipsw --device-class D47AP
```

Compare baseline and comparison:

```sh
python3 tools/ipsw_manifest.py diff baseline.ipsw comparison.ipsw --device-class D47AP --json reports/manifest-diff.json
```

The tool can also compare extracted `BuildManifest.plist` files directly. This is useful when the full IPSWs are too large to upload or share:

```sh
python3 tools/ipsw_manifest.py diff baseline/BuildManifest.plist comparison/BuildManifest.plist --device-class D47AP --json reports/manifest-diff.json
```

Extract the manifest from each IPSW without unpacking the firmware payloads:

```sh
unzip -p baseline.ipsw BuildManifest.plist > baseline-BuildManifest.plist
unzip -p comparison.ipsw BuildManifest.plist > comparison-BuildManifest.plist
```

Share the two small plist files or the generated JSON report for review. A plist-only report records the manifest file hash; an IPSW-based report also calculates the full IPSW SHA-256. The tool does not unpack firmware payloads, disassemble code, modify a device, or assess exploitability.

## Public lead under investigation\n\nApple documents a WebKit Process Model Web Content sandbox escape fixed in iOS 27.2: [CVE-2026-113897 research note](docs/CVE-2026-113897.md). This is a public advisory, not a vulnerability independently discovered or reproduced by this repository.\n\n## Research protocol

1. Record source URLs, retrieval date, file size, and SHA-256 for each IPSW.
2. Verify product version, build version, and matching device class in each manifest.
3. Review changed component paths and digests; prioritize changes supported by public security notes or independently reproduced observations.
4. Keep a research log with exact commands and evidence. Do not label a change as a security fix without evidence.
5. If a vulnerability is validated, follow Apple's current coordinated disclosure process.

## Safety

Use a separate test device or isolated analysis environment. Do not flash experimental firmware onto a daily-use phone or run untrusted payloads.

## Status

- [x] Read-only manifest inspector and comparator
- [ ] Verify firmware files and record hashes
- [ ] Triage component changes with static analysis
- [ ] Validate any suspected issue safely
- [ ] Responsible disclosure, if warranted

**No vulnerability or exploit is currently claimed.**
