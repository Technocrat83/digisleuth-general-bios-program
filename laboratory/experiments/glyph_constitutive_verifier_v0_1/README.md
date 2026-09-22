# GLYPH Constitutive Verifier v0.1 — bounded reference implementation

Standing: **IMPLEMENTED / BATTERY NOT EXECUTED**

This package implements the proposed local serialization profile and bounded verification/receipt-binding behavior for `GLYPH_CONSTITUTIVE_VERIFICATION_BATTERY_v0.1`.

## Constitutional ceiling

Implementation does **not** establish:

- transport losslessness;
- Least Viable Spectra minimality;
- issuer authentication;
- production enforcement;
- localization permission;
- admission;
- authority binding;
- permission for any specific action;
- constitutional promotion.

`membrane_strict_disconnect` remains `REQUIRED_NOT_YET_TESTED` until the 18-specimen battery is deliberately executed.

## Files

- `glyph_verifier.py` — local `glyph.json.v0.1` serializer, contract validation, residue aggregation, positive receipt construction, integrity validation, and stale-binding checks.
- `baseline.py` — fixed synthetic source, receiver, dependency/evaluator manifests, independent obligation profile, baseline contract, and baseline PASS residues.
- `expectation_matrix.json` — detached 18-specimen input/expectation matrix. This is the oracle surface; verifier code does not define it.
- `run_battery.py` — explicit runner for S01–S18. **Not executed as part of package construction.**
- `PREREGISTRATION.md` — concise preregistration record and corrections.

## Serialization profile

`glyph.json.v0.1` is a **local profile**, not a claim of compliance with any external canonical-JSON standard.

Implemented rules:

- UTF-8 JSON;
- unique string object keys when parsing;
- sorted object keys when serializing;
- no insignificant whitespace;
- exact Unicode code points; no normalization;
- strings, booleans, null, integers, arrays, objects only;
- JSON floating-point values, NaN, and infinity rejected;
- array order preserved;
- predicate residues sorted by `predicate_id` before positive receipt construction;
- SHA-256 over defined serialized bytes;
- digest encoded as lowercase hexadecimal with `sha256:` prefix.

Fractional quantities must be represented by domain schemas as explicit decimal strings carrying declared units/comparison semantics; the generic serializer only enforces that JSON floats are forbidden.

## Integrity boundary

The receipt body digest binds content when compared with a trusted reference. It does not authenticate an issuer. `reuse_receipt(...)` therefore requires an externally established `trusted_test_verifier_established` condition in addition to schema/integrity and binding checks.

## Execution

To deliberately execute the preregistered battery:

```bash
python run_battery.py
```

That command will create `battery_actual_results.json` and changes the factual execution standing of the specimen battery. This package has **not** run that command.
