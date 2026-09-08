# OMEGA_TUPLE_RUNTIME_INTERFACE_v0.1

**Parent semantic contract:** `governance/jlk/JLK_OMEGA_LOCALIZATION_CONTRACT_v0.1.md`  
**Class:** Runtime representation interface  
**Status:** PRE_EXECUTION_RUNTIME_MATERIALIZATION  
**Canon:** FALSE  
**PP:** BLOCKED

This package materializes already-frozen JLK semantics. It does not define them.

## Carrier

`Omega = <iota, tau, pi, xi, sigma, epsilon>`

Properties: `CLOSED`, `NON_INFERABLE`, `REPLAY_BOUND`.

## Exposed operations

- `validate_tuple()`
- `place_tuple()`
- `propagate_candidate()`
- `localize_jurisdiction()`
- `observe_orientation()`
- `invalidate_orientation()`
- `petition_authority()`
- `petition_execution()`

The last two emit petitions only. They grant nothing.

## Deliberately absent operations

- `infer_missing_identity()`
- `repair_provenance()`
- `self_assign_jurisdiction()`
- `promote_orientation_to_authority()`
- `execute_if_oriented()`

## Runtime non-equivalence

`Identity != Placement != Orientation != Authority != Execution`

A stale orientation remains historical provenance but is operationally execution-ineligible.
