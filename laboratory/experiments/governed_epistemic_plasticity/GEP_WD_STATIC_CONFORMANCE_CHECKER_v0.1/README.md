# GEP_WD_STATIC_CONFORMANCE_CHECKER_v0.1

**Class:** PRE_EXECUTION_VALIDATION_APPARATUS  
**Parent:** GOVERNED_EPISTEMIC_PLASTICITY_EXPERIMENT_01

## Authority

The checker may verify only:

- warrant structure
- derivation-rule identity and version
- exact input binding
- SourceCone binding
- assumptions
- permissible semantic scope
- jurisdiction
- epoch
- issuer
- provenance/replay information

It has **zero authority** to repair warrants or SourceCones, infer missing lineage, admit relations, assign epistemic standing, mutate topology, or promote fixtures into semantics.

## Frozen result domain

`Verify(W_D) ∈ {VALID, INVALID, UNRESOLVED}`

- `INVALID`: a demonstrated violation exists.
- `UNRESOLVED`: required identity/authentication/evidence is missing or unresolved.
- `VALID`: all static coordinates conform to the supplied upstream policy.

`VALID` means only **eligible to continue**. It does not admit a relation or assign epistemic standing.

## Identity vector

`W_D = <I_R, V_R, I_inputs, I_SC, A, S, J, E, I_issuer, P>`

The implementation returns coordinate-wise dispositions and typed violations. It never returns a scalar confidence score.

## Constitutional invariants

- `Missing(W_D) != Infer(W_D)`
- `Invalid(W_D) != Repair(W_D)`
- `Valid(SourceCone) !=> Valid(W_D)`
- `Valid(W_D) !=> Admission`
- `Fixture Generation != Fixture Validity`

## Run static adversarial battery

```bash
python adversarial_battery.py
```

No GEP1–GEP7 concrete fixtures are included in this package by design.
