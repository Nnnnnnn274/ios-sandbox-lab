# Research log

## Project setup

- Target marketing model: iPhone 16
- ProductType: iPhone17,3
- SoC: A18
- Manifest DeviceClass expected by the CLI default: D47AP (verify in each IPSW)
- Baseline requested: iOS 27.0.1 / build 24A446
- Comparison requested: iOS 27.2 / build 24B119

## Evidence ledger

No IPSW files have yet been supplied or inspected in this project. Therefore no file hashes, manifest contents, component differences, patch claims, or vulnerability findings are recorded.

For each firmware file, add:
- Trusted source URL and retrieval timestamp
- Exact filename and byte size
- SHA-256 of the complete IPSW
- ProductVersion and ProductBuildVersion read from BuildManifest.plist
- DeviceClass identity used
- Tool version / command line
- Output report path and analyst notes

## Interpretation rules

- A changed digest only means the manifest records a different component digest.
- A changed path or component entry does not establish a security fix.
- A security-relevant patch hypothesis needs supporting evidence, such as a code-level change, affected code path, security bulletin, or reproducible behavior.
- Do not claim a sandbox escape without a safely reproduced, independently verifiable demonstration and a clear impact analysis.
