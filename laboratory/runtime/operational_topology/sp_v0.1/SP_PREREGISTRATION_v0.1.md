# Operational Topology Operator \(\mathcal{S}_P\) — Reference Testbed v0.1

**Standing:** `CANDIDATE_ANALYTICAL_OPERATOR_REFERENCE_MODEL`  
**Scientific evidence delta:** `ZERO`  
**Constitutional delta:** `ZERO`  
**Execution authority:** `ZERO`

## Topology object

\[
\mathcal G=(V,E,\tau)
\]

`E` is represented as directed attributed hyperedges with one-or-more sources and one-or-more targets. DAG acyclicity is optional scope metadata, not the identity of the topology.

## Operator

\[
\mathcal S_P(\mathcal G)=
\langle \mathbf{Src},\mathbf{Bind},\mathbf{Reach}_{bypass},\mathbf{Scope}\rangle
\]

### Src
Traces holders of each consequential power through active authorization/delegation ancestry to a declared `SOVEREIGN_ROOT`. Unrooted consequential powers emit `UNROOTED_CONSEQUENTIAL_POWER`.

### Bind
Enumerates direct powers, computes fixed-point effective power closure, and evaluates declared resource-budget conservation.

### Reach_bypass
Emits concrete counterexample traces for:
- implicit authority escalation by composition,
- consequential execution edges lacking `AuthorityBinding`,
- budget conservation failure,
- unbound scheduler influence,
- optional acyclicity violations.

### Scope
Binds the result to schema version, canonical topology SHA-256, execution-model assumptions, and the evaluation interval.

## Scheduler adversary battery

A separate bounded behavioral harness exercises:
- starvation with independent fail-closed liveness,
- budget hoarding against partitioned child quotas,
- CEASE filtering against a direct out-of-band cease path.

These tests demonstrate the reference mechanism only; they do not establish OS-level or hardware-level scheduler isolation.

## Claim ceiling

> The supplied analyzer and scheduler harness conform to the frozen synthetic fixtures and declared detection oracle.

No result establishes completeness of arbitrary hypergraph reachability, production enforcement, distributed consensus, cryptographic infrastructure correctness, or physical impossibility of bypass.
