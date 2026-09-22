# MAGUS EG10 Execution Gate & Invalidation Model — Preregistration v0.1

**Standing:** `CANDIDATE_PREREGISTRATION_FROZEN_FOR_BOUNDED_REFERENCE_MODEL`  
**Scientific evidence delta:** `ZERO`  
**Constitutional delta:** `ZERO`  
**Execution authority:** `ZERO`  
**Implementation scope:** single-process in-memory reference runner only

## 1. Purpose

This preregistration binds the EG10 execution-gate doctrine to a deterministic reference model. The model evaluates only consequential boundaries directly governed by the reference MAGUS runtime. It explicitly rejects claims of multi-system atomicity.

## 2. Controlled Boundary Taxonomy

| Boundary | Controlled primitive | Ordering contract | Post-invalidation semantics |
|---|---|---|---|
| `LOCAL_STATE` | Internal coordination/ledger mutation | Gate check and state commit share one bounded linearization enclosure and monotonic sequence source. | If invalidation is ordered before actuation, controlled local mutation is denied. |
| `EGRESS_DISPATCH` | Outbound transport release | Gate check and release share the same bounded linearization enclosure. | Release before invalidation is authorized at egress; remote completion remains asynchronous. |
| `REMOTE_EFFECT` | Third-party state transition | Uncontrolled by this model. | Observational/reconciliation domain only. |

Invariant:

\[
\operatorname{Seq}(\text{Invalidation}) < \operatorname{Seq}(\text{ActuationRelease})
\Rightarrow \operatorname{Outcome}=\text{DENY}
\]

## 3. Predetermined Oracle

| Scenario | Interleaving | Expected outcome | Required consequence |
|---|---|---|---|
| `HIST-01` | Unmount before actuation release | `DENY` | No controlled actuation; reservation may be released to parent. |
| `HIST-02` | Local actuation release before unmount | `PERMIT` | Mutation stands; later attempts on dead mount fail. |
| `HIST-03` | Egress release before unmount | `PERMIT_RELEASED` / pending settlement if timeout | Remote outcome not inferred; liability retained. |
| `HIST-04` | Sequence coherence unavailable | `DENY_CLOSED` | No actuation; ambiguity preserved. |
| `HIST-05` | Remote response timeout after egress | `SET_PENDING_RECONCILIATION` | Reservation remains encumbered; no implicit retry. |

## 4. Reference Linearization Model

The implementation uses a process-local mutex around execution-gate state observation and the controlled actuation-release sequence increment.

This establishes a bounded reference linearization point for the in-memory model only.

It does **not** establish:

- distributed consensus,
- cross-process atomicity,
- remote transactional rollback,
- socket/third-party effect atomicity,
- hardware-enforced isolation,
- formal verification of production behavior.

## 5. Resource Conservation

For resource metric \(r\):

\[
Spent_p(r)+ReservedOutstanding_p(r)\le Budget_p(r)
\]

Active reservations include both ordinary held reservations and uncertain external liabilities awaiting settlement.

Timeout does not reclaim liability.

Permitted settlement states in the reference model:

- authoritative success → settle spend,
- verified failure → release,
- confirmed void → release,
- unknown/timeout → remain encumbered.

## 6. Single-Use Execution Attempt

An `attempt_id` consumed by a successful actuation-release decision cannot authorize another actuation in the reference runtime.

Replay must return:

`DENY_SINGLE_USE_ATTEMPT_REPLAY`

## 7. Invalidation Source of Truth

The mount registry is consulted synchronously at execution-gate evaluation.

Event-bus notification is not modeled as authority.

Therefore:

\[
\text{RevocationNotification}\neq\text{RevocationAuthority}
\]

A missed notification cannot preserve authority in this reference model if the source-of-truth registry reports the mount inactive.

## 8. Frozen Test Battery

Required passing tests:

- `HIST-01` unmount before actuation
- `HIST-02` local actuation before unmount
- `HIST-03` egress release with uncertain remote settlement
- `HIST-04` unknown ordering → fail closed
- `HIST-05` timeout → pending reconciliation
- single-use attempt replay denial
- sibling concurrent reservation conservation
- registry invalidation denial without bus-event dependence

## 9. Claim Boundary

Passing this battery establishes only:

> The supplied in-memory reference implementation conforms to the preregistered oracle under the exercised bounded test histories.

It does not establish that any production MAGUS runtime, distributed deployment, operating-system sandbox, external API, remote actuator, or cryptographic infrastructure satisfies the same properties.

## 10. Stop Condition

If all frozen tests pass without altering the predetermined oracle, the reference implementation may be classified:

`REFERENCE_MODEL_CONFORMS_TO_PREREGISTERED_EG10_ORACLE_v0.1`

Any oracle modification after observing test results requires a new preregistration version.
