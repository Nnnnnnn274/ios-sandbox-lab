# Evidence ledger

Use one entry per downloaded artifact and one per analytical observation. Preserve unverified catalogue values separately from locally verified values.

## Artifact record

| Field | Value |
|---|---|
| Artifact ID | |
| Filename | |
| Source URL and source class | |
| Retrieval timestamp (UTC) | |
| File size (bytes) | |
| Local SHA-256 | |
| Expected SHA-256 and provenance | |
| ProductVersion / ProductBuildVersion | |
| ProductName | |
| ProductType (external device mapping) | |
| DeviceClass (manifest) | |
| BuildIdentity index / variant | |
| Inspector commit and command | |
| Report path | |
| Notes | |

## Observation record

| Field | Value |
|---|---|
| Observation ID | |
| Related artifact IDs | |
| Component / path | |
| Observed difference | |
| Supporting evidence | |
| Alternative explanations | |
| Confidence (low / medium / high) | |
| Independently reproduced? | No |
| Security conclusion | None until supported |

## Current state

No firmware archive has been locally hashed or inspected by this repository yet. Workflow SHA-256 values are third-party catalogue expectations, not local observations. No component change has been attributed to CVE-2026-112690 and no vulnerability has been independently reproduced.
