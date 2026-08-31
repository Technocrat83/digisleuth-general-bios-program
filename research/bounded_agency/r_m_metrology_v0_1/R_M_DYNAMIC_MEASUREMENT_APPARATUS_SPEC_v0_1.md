# R_M_DYNAMIC_MEASUREMENT_APPARATUS_SPEC_v0.1

```text
SPECIFICATION: FROZEN
ISOLATED_MATERIALIZATION: AUTHORIZED
SCIENTIFIC_CHAMBER_EXECUTION: WITHHELD
SCIENTIFIC_ADJUDICATION: WITHHELD
PP: BLOCKED
```

## Measurement law

\[
\boxed{Reachable \neq Traversed \neq Admitted}
\]

\[
\boxed{MeasureRealizability(e) \neq Execute(e)}
\]

The meter proves realizability only from declared prerequisites, habitat membership, current physiology, object origin, and counterfactual graph closure. It may not traverse an edge, mutate the specimen, alter jurisdiction, or infer missing prerequisites.

Missing or incomplete prerequisite declarations SHALL yield `UNRESOLVED`, never `NONREALIZABLE`.

## Five-gate preflight

- `G1 SIDE_EFFECT_FREE`: no mutation to P, G_M, J, objects, habitat; traversal count = 0.
- `G2 DETERMINISTIC`: identical inputs and provenance produce identical raw observations.
- `G3 EPISTEMIC_ABSTENTION`: absent prerequisites return UNRESOLVED.
- `G4 PROVENANCE_BOUND`: observation contains source lineage identifiers and stable input digest.
- `G5 SCHEMA_AND_AUTHORITY_CONFORMANCE`: O_RM fields present; meter emits no scientific verdict, grant, geometry classification, or PP state.

Clearance requires `G1 && G2 && G3 && G4 && G5`.

If `G1 = 0`, terminal state is `METROLOGICAL_SIDE_EFFECT_HALT` and output has zero standing as evidence about R_M.
