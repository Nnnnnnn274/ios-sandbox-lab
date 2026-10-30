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
- Cross-platform confirmation: https://support.apple.com/en-la/149521
- Project status: public advisory confirmed; no independent binary verification or reproduction yet.

A second relevant advisory entry is CVE-2026-112690 under App Store, also describing a possible remote WebContent sandbox escape fixed with improved input validation. Keep it as a secondary lead, but do not assume it is the same root cause as CVE-2026-113897.

## Upstream trace checkpoint (2026-10-30)

- Queried the public WebKit Bugzilla page for bug 328129 and its REST endpoint. They were not retrievable through the current research interface.
- Searched the public WebKit/WebKit GitHub repository for the literal bug number in code and commit metadata. No matching result was returned.
- This is an access/search limitation, not evidence that the bug is private, absent from WebKit, or has no associated source change.
- No upstream patch, commit SHA, changed source file, or root cause has been independently identified.
- Apple’s phrase “removing the vulnerable code” is the only currently confirmed description of the remediation. Do not guess what code was removed.

## Firmware identity checkpoint

Third-party firmware catalogues consistently list the target pair for iPhone 16 (iPhone17,3 / D47AP):
- iOS 27.0.1 build 24A446
- iOS 27.2 build 24B119

References:
- https://ipsw.me/iPhone17%2C3/
- https://www.ipsw.dev/iPhone17%2C3
- https://www.applefirmwares.com/firmware/iPhone17%2C3/27.0.1

The 27.2 iPhone 16 restore image is listed as approximately 12.88 GB. A third-party catalogue reports SHA-256 `62158ad39a22fca5620deeb407cf367cab1775cf1c2fbbdf627321383af78f8b` for that exact image:
- https://betaprofile.dev/ipsw/ios-27-2-24b119/

This is a catalogue-reported checksum, not a hash calculated by this project. It must be verified against the downloaded file before being treated as an observed artifact.

## Evidence ledger

No IPSW files have yet been supplied or inspected by this project. Therefore no locally calculated firmware hashes, manifest contents, component-level binary differences, or independent vulnerability findings are recorded.

For each firmware file, add:
- Trusted source URL and retrieval timestamp
- Exact filename and byte size
- SHA-256 of the complete IPSW, calculated locally
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
