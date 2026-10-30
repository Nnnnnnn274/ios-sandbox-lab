# Research log

## Project setup

- Target marketing model: iPhone 16
- ProductType: iPhone17,3
- Board configuration: D47AP
- SoC: A18
- Baseline requested: iOS 27.0.1 / build 24A446
- Comparison requested: iOS 27.2 / build 24B119

## Public lead identified

- CVE: CVE-2026-113897
- Apple component: WebKit Process Model
- WebKit Bugzilla: 328129
- Apple-described impact: remote attacker may be able to break out of Web Content sandbox
- Apple-described fix: vulnerable code removed
- Fixed release: iOS 27.2 (released 2026-10-26)
- Researchers credited: Luke Francis, Jackson Kuja
- Primary source: https://support.apple.com/en-us/149230
- Project status: public advisory confirmed; no independent binary verification or reproduction yet.

A second relevant advisory entry is CVE-2026-112690 under App Store, also describing a possible remote WebContent sandbox escape fixed with improved input validation. Keep it as a secondary lead, but do not assume it is the same root cause as CVE-2026-113897.

## Evidence ledger

No IPSW files have yet been supplied or inspected by this project. Therefore no local firmware hashes, manifest contents, component-level binary differences, or independent vulnerability findings are recorded.

For each firmware file, add:
- Trusted source URL and retrieval timestamp
- Exact filename and byte size
- SHA-256 of the complete IPSW
- ProductVersion and ProductBuildVersion from BuildManifest.plist
- Matching DeviceClass / BuildIdentity
- Tool version and exact command line
- Output report path and analyst notes

## Interpretation rules

- A changed digest only means the manifest records a different component digest.
- A changed path or component entry does not establish a security fix.
- A public advisory is a research lead, not independent validation.
- A sandbox escape does not automatically imply kernel privilege escalation or a full-device jailbreak.
- Any security conclusion needs supporting evidence and reproducible validation.
