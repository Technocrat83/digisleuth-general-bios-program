# \(\mathcal S_P\) Descendant Oracle & Topology Invariant Suite v0.2

**Standing:** `CANDIDATE_DESCENDANT_PREREGISTRATION_FROZEN`  
**Parent:** `SP_OPERATIONAL_TOPOLOGY_REFERENCE_v0.1`  
**Scientific evidence delta:** `ZERO`  
**Constitutional delta:** `ZERO`  
**Execution authority delta:** `ZERO`

## Verdict lattice

\[
Verdict(\mathcal S_P(\mathcal G,\Pi,\Omega))
\in
\{
VIOLATION\_DETECTED,
NO\_VIOLATION\_WITHIN\_SCOPE,
ABSTAIN
\}
\]

`NO_VIOLATION_WITHIN_SCOPE` is non-authorizing evidence bound to one topology digest and evaluation sequence.

`VIOLATION_DETECTED` and `ABSTAIN` fail closed at the EG10 bridge.

## Fixture battery

The frozen suite contains:
- SP-A01 through SP-A03 lawful controls,
- SP-A04 through SP-A09 adversarial topology violations,
- SP-A10a isomorphic alpha-renaming,
- SP-A10b semantic power reassignment,
- SP-A11 topology-stasis violation,
- SP-A12 incomplete observation producing abstention.

## Composition policy

SP-A09 and SP-A10a explicitly test:

\[
\neg\exists u:
\{MODIFY\_RULEBOOK,INVOKE\_DISPATCH\}\subseteq P_u
\]

under rule `POL-NO-SELF-AUTHORIZING-DISPATCH`.

## Failure trace

Every detected violation is normalized to:
- `failure_class`,
- `rule_id`,
- `transition_sequence`,
- `culpable_nodes`,
- `culpable_edges`,
- `compositional_trace`,
- `detail`.

## EG10 bridge

The reference bridge requires:
1. an independently valid `AuthorityBinding`,
2. `NO_VIOLATION_WITHIN_SCOPE`,
3. exact topology digest equality.

Therefore:

\[
StructuralEvidence \neq Authorization
\]

and:

\[
ABSTAIN \Rightarrow DENY
\]

## Claim ceiling

Passing establishes only that the supplied reference engine classifies the frozen synthetic fixtures according to the preregistered tripartite oracle and bridge semantics.

It does not establish complete model checking for arbitrary hypergraphs, production enforcement, distributed consensus, or physical impossibility of bypass.
