# iOS Sandbox Lab

Read-only iOS firmware research for **iPhone 16 (iPhone17,3 / A18)**.

## Scope

This repository starts with IPSW metadata inspection and BuildManifest comparison. It is intended for reproducible defensive research and vulnerability triage.

It does **not** contain a jailbreak, sandbox escape, privilege-escalation payload, persistence mechanism, or device-modification workflow. A firmware difference is only a lead; it is not proof of a vulnerability.

## Firmware comparison target

| Role | iOS version | Build |
|---|---:|---:|
| Baseline | 27.0.1 | 24A446 |
| Comparison | 27.2 | 24B119 |

Verify that downloaded IPSWs actually match the target product and builds before drawing conclusions. Firmware availability and signing status can change.

## Requirements

- Python 3.10+
- Two IPSW files obtained from a trusted source
- No third-party Python packages

## Usage

Inspect one IPSW:

```sh
python3 tools/ipsw_manifest.py inspect path/to/firmware.ipsw --product iPhone17,3
```

Compare two IPSW manifests:

```sh
python3 tools/ipsw_manifest.py diff baseline.ipsw comparison.ipsw --product iPhone17,3
```

Write machine-readable output:

```sh
python3 tools/ipsw_manifest.py diff baseline.ipsw comparison.ipsw --product iPhone17,3 --json report.json
```

The tool reads ZIP members directly and does not extract or flash firmware. It reports manifest metadata and component-path/digest changes; it does not disassemble binaries or establish exploitability.

## Safety and handling

- Work on copies of firmware and preserve original hashes.
- Do not flash research firmware onto a daily-use device.
- Do not run unknown payloads or exploit code on personal devices.
- Keep any suspected issue in a controlled, non-production test environment.
- Follow Apple's current Security Research Device and vulnerability disclosure guidance when applicable.

## Project status

- [x] Read-only IPSW BuildManifest inspector
- [x] BuildManifest comparison
- [ ] Verify the supplied firmware files and record their SHA-256 hashes
- [ ] Triage relevant component changes using static analysis
- [ ] Document and responsibly report any validated security issue

No vulnerability or exploit is currently claimed.
