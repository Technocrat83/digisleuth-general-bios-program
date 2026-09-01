# Blind Extraction and Adjudication Contracts

## Frozen execution order

1. Load immutable `S0.json`.
2. Load one chamber specimen without revealing its target label to the extractor.
3. Apply representation-specific extractor `C_k`.
4. Emit only:
   - `S_hat_k`
   - `q_k` extraction-status vector
   - `w_k` witness vector
5. Apply preservation contract `Omega_k` outside the extractor.
6. Produce typed error/evidence vector `E_k`.
7. Pass `E_k` to conformance adjudicator `A_C`.
8. Emit `CONFORMANT`, `NONCONFORMANT`, or `UNRESOLVED`.
9. Evaluate sibling compatibility independently.
10. Reveal chamber identity and audit against frozen target.

## Separation constraints

`Pi_k != C_k != Omega_k != A_C`

`Extraction Status != Preservation Obligation != Conformance Verdict`

`ABSENT` means only that no admissible recoverable value was extracted.

`ABSENT AND omega=1` may support `CONSTITUTIVE_LOSS`.

`ABSENT AND omega=0` may remain conformant unless another coordinate independently violates identity, meaning, provenance, jurisdiction, or authority constraints.

The extractor may not inspect `Omega_k`.
The adjudicator may not repair extractor output.
Missing provenance may not be reconstructed.
Missing semantics may not be inferred.
Sibling agreement may not create source truth.
