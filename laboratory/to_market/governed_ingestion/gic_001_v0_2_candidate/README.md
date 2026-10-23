# GIC-001 governed ingestion candidate — ruleset 0.2

Standing: candidate procedure and archival case snapshot. Case: `AWAITING_SUBMITTER_INPUT`. Admission: `HELD`. Epistemic standing: `UNRESOLVED`.

## Purpose and earned contribution

GIC-001 converts the proposed Digisleuth Governed AI Ingestion service into a bounded recovery procedure: a submitted source, an intended AVIV output, an intended destination, and a documented disposition. The historical specimen label is “Constellation Aviv / Source: X”.

This package records the procedure and its unresolved first case. It establishes no original-source recovery, ingestion success, admission, publication approval, execution enforcement, verified signature, or commercial demand.

## Decision order and stopping conditions

1. Respect an existing terminal disposition or explicit submitter stop.
2. Check required inputs before assessing reliability. A recovery submission, intended AVIV output, and destination are required. Author, posting date, and original URL are requested where available.
3. At or after **2026-10-29 23:59 EDT** (`2026-10-30T03:59:00Z`), any missing required input, including a partial submission, yields administrative `EXPLAINED_BLOCK`.
4. Unknown input presence is not classified as missing. Present inputs with unreliable assessment, or unknown input presence, yield `REVIEW_UNRESOLVED` before the review deadline, with admission held.
5. At or after **2026-10-30 23:59 EDT** (`2026-10-31T03:59:00Z`), remaining unresolved review yields administrative `EXPLAINED_BLOCK`; epistemic standing remains `UNRESOLVED`.
6. Record ingestion, destination admission, and publication decisions separately. Recovery alone grants no admission authority.

Administrative closure ends active handling under this scope; it establishes neither source absence nor source falsity. Reopening requires a newly recorded bounded scope. The saved record contains the full rules, including explicit decline and successful-ingestion paths.

## Evidence boundaries

The historical `ACCESS_LIMITATION_OBSERVED` event is supplied history, not an independently inspected retrieval receipt. Historical attempt count and exhaustion remain unverified. `EXHAUSTED_UNRESOLVED` requires an inspectable attempt record evaluated against a declared budget.

The prospective automatic source-retrieval budget is zero. It does not retrospectively establish exhaustion. No original X source content is included.

Captured-byte integrity and source attribution are separate checks. A digest can identify captured bytes and support comparison with a recorded capture baseline. It cannot establish that those bytes belong to the submitted locator, author, or post.

The hold and prohibitions are declared constraints. Runtime enforcement, zero-leakage verification, tamper-evidence, and receipt signing remain unestablished. A fresh configuration read is not an independent runtime audit.

## Contents and provenance

- `GIC-001_Recovery_Record_v0.1.json`: exact 13,454-byte snapshot of Library item `libfile_1efe553798a08191b61af12bebdeb481`, version `2`. Its record format is 0.1 and its ruleset is 0.2; the historical filename is retained.
- `GIC-001_CHECKPOINT_CONFIGURATION_RECEIPT_v0.1.json`: selected checkpoint configuration, exact observed task prompt, and explicitly limited execution/signature standing.
- `GIC-001_LINEAGE_MANIFEST_v0.1.json`: content sizes, SHA-256 digests, Git blob identities, source version, and observed parent revision.
- This README: rationale and claim boundaries.

The live case remains in the identified Library item. The scheduled task addresses that live item. This Git package is a snapshot and does not replace the live case or update automatically. Later receipts require a subsequent recorded revision.

This follows `laboratory/README.md` at parent revision `b194dd3fe745350f870a63a2f139e170dcb8f530`: execution, adjudication, and promotion authorities remain separate. The proposed commercial willingness to pay remains an untested hypothesis.

