# JLK_OMEGA_LOCALIZATION_CONTRACT_v0.1

**Parent:** `TUPLE_GEOMETRIC_ORIENTATION_LAW_v0.1`  
**Class:** Jurisdictional Localization Contract  
**Status:** CANDIDATE_ARCHITECTURAL_SPECIFICATION  
**Canon:** FALSE  
**PP:** BLOCKED

## Constitutional ordering

`Jurisdictional Semantics -> Localization Contract -> Runtime Representation -> Executable Transition Functions`

Runtime structures MUST instantiate this contract. Runtime fields MUST NOT define or extend this contract.

## Omega carrier

`Omega(O) = <iota, tau, pi, xi, sigma, epsilon>`

The carrier is **closed, non-inferable, replay-bound**.

- `iota`: constitutional identity
- `tau`: type identity
- `pi`: provenance / replay lineage
- `xi`: jurisdictional coordinate
- `sigma`: state vector
- `epsilon`: epoch

Missing coordinates may not be synthesized by inference:

`Missing(iota,tau,pi,xi,sigma,epsilon) !=> Infer(iota,tau,pi,xi,sigma,epsilon)`

Provenance replay remains required:

`Replay(pi)` MUST be possible when the referenced lineage is available and authenticated.

## JLK input contract

JLK consumes exactly:

`<Omega(O), G, v_O>`

where:

- `Omega(O)`: validated tuple carrier;
- `G`: authenticated graph/topology observation;
- `v_O`: explicit placement of O in G.

Missing input identity, graph identity, or placement identity yields `UNRESOLVED`; it MUST NOT be repaired locally.

## Localization witness

JLK emits:

`L_O = <C_minus_causal, C_plus_jurisdictional, boundary_xi, S_O, W_D_resolved, U_L>`

Coordinates:

- `C_minus_causal`: demonstrated backward causal/provenance cone.
- `C_plus_jurisdictional`: maximum demonstrated forward authority-impact cone.
- `boundary_xi`: jurisdictional boundary surface plus permeability declaration.
- `S_O`: localized scope.
- `W_D_resolved`: only warrants already resolved as applicable at this placement.
- `U_L`: unresolved localization coordinates preserved explicitly.

`JLK(O) = L_O`

JLK MUST NOT emit or imply `Authority(O)`.

## Separation of powers

`Localization Authority != Admission Authority != Enforcement Authority`

JLK may:

- localize demonstrated causal dependence;
- localize demonstrated jurisdictional impact;
- preserve boundary permeability declarations;
- report applicable resolved warrants;
- preserve unresolved localization coordinates;
- mark orientation inputs stale or unresolved.

JLK may not:

- admit a relation;
- grant residency;
- assign execution authority;
- enforce a transition;
- infer missing tuple coordinates;
- repair provenance;
- repair graph topology;
- repair a warrant;
- expand jurisdiction beyond demonstrated boundaries.

## Cone non-substitution

`C_minus(O) != C_plus(O)`

A backward-cone mutation requires identity/provenance re-observation.

A forward-cone mutation requires jurisdiction/consequence re-localization.

Neither transition repairs the other.

## Orientation witness contract

`O_O = <I_Omega, I_G, v_O, L_O, H_G, H_J, epsilon_O, epsilon_G>`

An orientation is current iff:

`Valid(Omega(O)) AND Valid(L_O) AND Current(H_G) AND Current(H_J)`

The orientation witness is historical evidence and MUST be preserved when stale.

## Staleness rule

Any demonstrated change in placement, graph topology, jurisdiction topology, boundary state, source-cone identity, tuple jurisdiction, or relevant epoch marks the current orientation witness `STALE`.

`STALE(O_O) != NoHistoricalOrientation(O)`

but:

`STALE(O_O) => NOT ExecutionEligible(O)`

## Five-state separation

`I -> P -> O -> A -> X`

- `I`: identity established
- `P`: placement established
- `O`: orientation current
- `A`: authority independently established
- `X`: execution independently authorized

No implication is permitted across stages:

`I !=> P`
`P !=> O`
`O !=> A`
`A !=> X`

## Governing runtime constraint

Geometry determines placement, dependency, possible lawful impact, and the information required before authority may be considered. Geometry never grants authority.
