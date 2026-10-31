# iOS Sandbox Lab

Read-only iOS firmware metadata research for **iPhone 16** (ProductType `iPhone17,3`, board configuration `D47AP`, A18).

## Scope and safety

This project inspects IPSW `BuildManifest.plist` metadata and compares component records. It does not implement a jailbreak, sandbox escape, privilege escalation, persistence, device modification, or exploit payload. Manifest changes are triage leads—not proof of a security fix or exploitability.

## Current comparison target

| Role | iOS | Build |
|---|---:|---:|
| Baseline | 27.0.1 | 24A446 |
| Comparison | 27.2 | 24B119 |

Verify the version, build, product and device class from each downloaded manifest before interpreting results. `D47AP` is a BuildManifest DeviceClass, not the marketing ProductType.

## Requirements

- Python 3.10+
- IPSW files from Apple's CDN (download URLs are recorded in `docs/research-log.md`)
- No third-party Python packages

## Commands

Inspect an IPSW or extracted plist:

```sh
python3 tools/ipsw_manifest.py inspect path/to/file.ipsw --device-class D47AP
```

Compare two inputs:

```sh
python3 tools/ipsw_manifest.py diff baseline.ipsw comparison.ipsw --device-class D47AP --json reports/manifest-diff.json
```

For smaller uploads, extract only the manifests:

```sh
unzip -p baseline.ipsw BuildManifest.plist > baseline-BuildManifest.plist
unzip -p comparison.ipsw BuildManifest.plist > comparison-BuildManifest.plist
python3 tools/ipsw_manifest.py diff baseline-BuildManifest.plist comparison-BuildManifest.plist --device-class D47AP --json reports/manifest-diff.json
```

The inspector hashes the complete IPSW when given an archive and hashes the manifest when given a standalone plist. It validates the archive, manifest structure, selected BuildIdentity and component digest types. It does not unpack firmware payloads or assess exploitability.

## Research lead: CVE-2026-112690

Apple's iOS 27.2 advisory lists **CVE-2026-112690** under App Store and describes a possible remote WebContent sandbox escape, addressed with improved input validation. See [the research note](docs/CVE-2026-112690.md) and [Apple's iOS 27.2 security advisory](https://support.apple.com/en-us/149230).

**Correction:** CVE-2026-113897 / Bugzilla 328129 is listed in Apple's macOS Golden Gate advisory, not the iOS 27.2 advisory. It must not be represented as the iPhone 16 iOS lead. The historical note at `docs/CVE-2026-113897.md` records this correction.

## Workflows

- `Extract and compare iPhone 16 IPSW manifests`: downloads both IPSWs, checks catalogue-provided SHA-256 values, extracts manifests, validates the expected release identity, compares and uploads reports.
- `Compare cached iPhone 16 IPSW manifests`: same analysis with cached extracted manifests.

The expected hashes in the workflows are third-party catalogue claims, not Apple-signed checksums. A successful match verifies the downloaded bytes against those recorded values; it does not establish the provenance or correctness of the catalogue entry. Review and update them against independently trusted records before relying on them.

## Research protocol

1. Record source URL, retrieval time, exact filename, byte size and locally calculated SHA-256.
2. Verify ProductVersion, ProductBuildVersion, ProductName and matching DeviceClass in both manifests.
3. Compare component paths and digests; retain the raw manifests and JSON reports.
4. Correlate observations with Apple advisories and independently verifiable upstream evidence.
5. Never call a manifest difference a security patch without corroboration.
6. Keep exploit reproduction out of scope; if a vulnerability is independently validated, follow Apple's coordinated disclosure process.

See [architecture](docs/analysis-architecture.md), [evidence ledger](docs/evidence-ledger.md), and [research log](docs/research-log.md).

## Status

- [x] Read-only manifest inspector and comparator
- [x] Parser validation and regression tests
- [ ] Verify firmware files and record hashes locally
- [ ] Triage component changes with static analysis
- [ ] Correlate public advisory with independently verifiable code/binary evidence
- [ ] Responsible disclosure, if warranted

**No vulnerability has been independently reproduced or claimed by this repository.**
