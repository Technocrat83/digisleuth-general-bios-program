# GENERAL_BIOS_BOUNDED_AGENCY_SYNTHETIC_FIXTURE_CONSTITUTION_v0.1

## Standing

```text
SPECIFICATION: FROZEN
MATERIALIZATION: PRESENT
INTERVENTION_EXECUTION: WITHHELD
ADJUDICATION: WITHHELD
SCIENTIFIC_EVIDENCE: ZERO
PP: BLOCKED
```

## Candidate coordinate model

\[
\mathfrak B = \langle \mathcal P,\mathcal M,\mathcal J;\mathcal C\rangle
\]

Operational distinguishability is the target. Dynamical independence is not assumed.

## Maneuver metrology hardening

\[
\mathcal M = \langle \mathcal G_M,\mathcal R_M\rangle
\]

where:

- `G_M` = declared candidate transition topology.
- `R_M` = operationally realizable/reachable transitions under the current physiology, habitat, and object state.

Candidate relation:

\[
\mathcal R_M = R(\mathcal G_M,\mathcal P,\mathcal H,O)
\]

This relation is a fixture-computation target, not a theorem claim.

```text
NON_EQUIVALENCES:
  DECLARED_TRANSITION != REALIZABLE_TRANSITION
  REALIZABLE_TRANSITION != ADMITTED_TRANSITION
```

## Delta typing

Every observed delta must be typed as one of:

```text
DIRECT
INDUCED
UNRESOLVED
```

Coupling must not be silently collapsed into intervention contamination.

## Intervention definitions

### B_P

```text
DIRECT_TARGET: P
DIRECT_DELTA_P: NONZERO
DIRECT_DELTA_G_M: ZERO
DIRECT_DELTA_J: ZERO
INDUCED_DELTA_R_M: OBSERVABLE_NOT_ASSUMED
```

### B_M

```text
DIRECT_TARGET: G_M
DIRECT_DELTA_G_M: NONZERO
DIRECT_DELTA_P: ZERO
DIRECT_DELTA_J: ZERO
DELTA_R_M: OBSERVABLE_NOT_ASSUMED
```

### B_J

```text
DIRECT_TARGET: J
DIRECT_DELTA_J: NONZERO
DIRECT_DELTA_P: ZERO
DIRECT_DELTA_G_M: ZERO
DIRECT_DELTA_R_M: ZERO
```

The last clause means the B_J operator may not directly mutate realizability. Whether any downstream measurement changes is not pre-adjudicated.

## Raw response object

For each intervention chamber `i`, preserve:

\[
D_i =
\begin{bmatrix}
\Delta P\\
\Delta G_M\\
\Delta R_M\\
\Delta J
\end{bmatrix}
\]

The raw apparatus must preserve all four surfaces. Any later reduction to `(P,M,J)` belongs to separate adjudication.

## Intervention purity

```text
INTERVENTION_PURITY != OUTCOME_ORTHOGONALITY
```

The apparatus constrains only which surface an operator may mutate directly. It does not encode what other surfaces must or must not change as an induced result.

## Authorization boundary

```text
FIXTURE_MATERIALIZATION: AUTHORIZED
MECHANICAL_PREFLIGHT: ELIGIBLE_AFTER_MATERIALIZATION
INTERVENTION_EXECUTION: WITHHELD
ADJUDICATION: WITHHELD
AUTOMATIC_EXECUTION_ON_IMPORT: PROHIBITED
```

## Governing sequence

\[
\boxed{\text{Materialize what may be changed. Preflight what actually changes. Execute only after independent admission.}}
\]

## Delta ledger

```text
CANON_DELTA: ZERO
PHYSIOLOGY_DELTA: ZERO
LEVEL_0_DELTA: ZERO
SCIENTIFIC_EVIDENCE_DELTA: ZERO
PP: BLOCKED
```
