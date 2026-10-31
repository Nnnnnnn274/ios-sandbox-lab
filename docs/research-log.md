# Research log

## Project setup

- Target marketing model: iPhone 16
- ProductType: iPhone17,3
- Board configuration: D47AP
- SoC: A18
- Baseline requested: iOS 27.0.1 / build 24A446
- Comparison requested: iOS 27.2 / build 24B119

## Advisory correction (2026-10-31)

An earlier draft incorrectly associated CVE-2026-113897 with the iOS 27.2 sandbox-escape entry. Apple's advisories show:

- **iOS 27.2 / iPadOS 27.2:** CVE-2026-112690, App Store; possible remote WebContent sandbox escape; improved input validation; credited to Claudio Bozzato and Francesco Benvenuto of Cisco Talos.
- **macOS Golden Gate 27.2:** CVE-2026-113897, WebKit Process Model / Bugzilla 328129; malicious web content may lead to arbitrary code execution; vulnerable code removed.

Primary sources:
- https://support.apple.com/en-us/149230
- https://support.apple.com/en-us/149521
- https://support.apple.com/en-us/100100

The iPhone 16 investigation now tracks CVE-2026-112690. CVE-2026-113897 is retained only as a related-but-distinct macOS issue. Neither issue has been independently reproduced by this repository.

## Firmware identity checkpoint

Apple's developer release listing identifies iOS 27.2 build 24B119 (October 26, 2026). The project compares the following target pair:
- iOS 27.0.1 / 24A446
- iOS 27.2 / 24B119

Device identity to verify from the actual manifests:
- ProductType: iPhone17,3
- BuildManifest Info.DeviceClass: D47AP

References:
- https://developer.apple.com/news/releases/
- https://ipsw.me/iPhone17%2C3/
- https://www.ipsw.dev/iPhone17%2C3

## Firmware acquisition targets

- Baseline IPSW: https://updates.cdn-apple.com/2026FallFCS/38dca0ee-bb5d-4132-ad13-62d57bcd6d32/iPhone17%2C3_27.0.1_24A446_Restore.ipsw
- Comparison IPSW: https://updates.cdn-apple.com/2026FallFCS/c6c0afa0-c002-45b9-ad4c-d2db3bfa30ac/iPhone17%2C3_27.2_24B119_Restore.ipsw
- Catalogue-reported baseline SHA-256: `fc87bb9da8c03d0154d87531950f4a170195f6663ee5208653fa7a26bafb9469`
- Catalogue-reported comparison SHA-256: `62158ad39a22fca5620deeb407cf367cab1775cf1c2fbbdf627321383af78f8b`

These SHA-256 values are third-party catalogue claims, not values calculated by this project or checksums published in the cited Apple advisory. The GitHub workflows compare downloaded files against these recorded values, but that check alone does not independently establish catalogue integrity. Reconfirm values against a trusted source before use.

## Acquisition limitation checkpoint (2026-10-30)

The previous research run could not download the multi-gigabyte IPSWs in its execution environment. No local archive hash, extracted manifest, or component comparison was produced. The opt-in firmware acquisition job in `.github/workflows/tests.yml` downloads both archives on a GitHub-hosted runner, verifies the recorded catalogue hashes, records actual file hashes/sizes/timestamps, extracts manifests, and compares the target builds. A run is being requested from this branch; no successful acquisition is claimed until its artifact is available.

## Evidence ledger

No IPSW files have yet been supplied or locally inspected by this project. Therefore no locally calculated firmware hashes, manifest contents, component-level differences, binary findings, or independent vulnerability findings are recorded.

Use `docs/evidence-ledger.md` for each artifact and observation. Record source URL, retrieval time, filename, byte size, local SHA-256, product/build identity, exact command and report path.

## Interpretation rules

- A changed digest means only that the manifest records a different component digest.
- A changed path or component entry does not establish a security fix.
- A public advisory is a research lead, not independent validation.
- A WebContent sandbox escape does not automatically imply kernel privilege escalation or a full-device jailbreak.
- Any security conclusion needs supporting, reproducible evidence.
