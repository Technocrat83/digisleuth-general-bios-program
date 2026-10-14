# Digisleuth next operational gate v0.2 candidate

This successor corrects the earlier inventory schema into an admitted-manifest
schema matching the Founder protocol. Every manifest record requires
`example_id`, `source_revision`, `reviewed_target`, `lineage_group`, and
`assigned_split`. The exact execution buckets are `train`, `regression_dev`,
and `holdout`. Records with missing provenance, independent review, lineage or
admission verification stay in a separate `PENDING_ADMISSION` intake ledger.

All ten counterexample repair families, all their derivatives, and all 66 known
development cases are restricted to `regression_dev`. The schema encodes direct
family/case restrictions. Full transitive ancestry, semantic derivative
classification, deterministic identifier recomputation, cross-record uniqueness
and single-split lineage membership require the separate admission checks in
`manifest_admission_contract.json`.

The schema requires accepted, verified review and admission evidence references.
It does not authenticate those receipts. An `ADMITTED` or `VERIFIED` field alone
cannot satisfy admission. The full admission implementation and reviewer trust
anchors remain unbound. Tests use explicitly synthetic development stubs, not
real reviewed targets or admitted corpus records.

`partition_freeze.schema.json` defines a detached freeze record binding the
manifest, split membership, review inventory, exclusions, custody/access policy
and exposure audit. SHA-256 digest computation and authenticated signing remain
distinct. Signatures stay outside the manifest to avoid circular hashes. Actual
custody and access evidence is required to support holdout isolation; neither a
digest nor a signature proves absence of historical leakage.

No actual admitted manifest, pending ledger, reviewed target list or partition
freeze is materialized. The finalized independent target list remains missing.
Schema correction and Git recording are authorized; corpus admission and model
execution are not effects of this record.

**Standing: candidate specification. Authority enforcement: NOT_EVALUATED.
Release: HOLD.** Corpus requalification, holdout execution, model comparisons,
training and production enforcement remain unestablished or unexecuted as
recorded in `gate_status.json`.

The exact v0.1 archive is preserved under `history/`. Its original labels and
inventory schema are historical evidence, not the current manifest contract.
Parent 350-file digest checks and reported 66/66 plus 6/6 development passes keep
their original scope. The repair validator was not rerun by this correction.
Its content hashes are references; its full execution ZIP is not incorporated.

## Local verification

Use Python 3.12 and the hash-pinned dependencies in `validation/requirements.lock`:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r validation/requirements.lock
.venv/bin/python tests/test_manifest_schemas.py
```

These checks assess schema guards on known synthetic development material. They
do not establish corpus admission, review independence, holdout generalization,
or runtime enforcement. Schema test source and derivatives are permanently
excluded from fresh-holdout claims.

`SHA256SUMS` binds all package members except itself. The recording commit creates
prospective Git ancestry; it is not an authenticated partition-freeze signature,
scientific ratification or release admission.
