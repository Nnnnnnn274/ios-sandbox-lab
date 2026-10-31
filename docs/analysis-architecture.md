# Analysis architecture

## Pipeline

1. Acquire the exact IPSW files from documented sources.
2. Calculate local SHA-256 and compare with a recorded expected value; preserve the provenance class of that expected value.
3. Read only the root `BuildManifest.plist` for metadata triage.
4. Verify ProductVersion, ProductBuildVersion, ProductName and the requested DeviceClass.
5. Compare component records using stable BuildIdentity metadata rather than list position alone.
6. Correlate candidates with Apple advisories and independently sourced upstream evidence.
7. Preserve raw manifests, JSON reports, exact commands and analyst interpretation.

## Trust boundaries

- A SHA-256 match proves byte equality with the expected digest string, not who supplied that string.
- A filename does not prove firmware identity; inspect the embedded manifest.
- DeviceClass is not ProductType. Record both from their respective sources.
- Manifest component digests are metadata, not binary diffs.
- A CVE advisory is a research lead, not proof that a specific component changed.

## Report contract

Schema version 1 includes input provenance, sizes and hashes, product/build metadata, selected identity metadata, component paths/digests, added/removed/changed/unchanged counts, and an interpretation warning.

## Scope

The project remains read-only. It does not create exploit payloads, implement sandbox escapes, establish persistence, escalate privileges, flash firmware, or test against third-party devices. Any future binary analysis should be a separate read-only stage with independent provenance and validation.
