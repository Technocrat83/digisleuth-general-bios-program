# Architecture Traversal → BIOS entitlement → governed commercialization

**Version 0.1 candidate · Data Scientist role · local compiler tested · live integrations unbound.**

This workflow turns architecture observations into immutable propositions, routes theorem claims to independent evaluation, and compiles externally admitted relationship records into an Obsidian execution-graph staging bundle. Successful, independently witnessed transformations can supply BIOSpub editorial preparation for **Substack DigiProse**.

The implementation is an offline verifier and compiler. It neither proves theorems nor issues decisions. It does not execute product workloads, activate a vault, call a live BIOSpub service, or publish to Substack. The workflow is reviewable in Git and produces typed records and Markdown suitable for a later bound writer.

## Workflow and decision owners

| Stage | Input and output | Decision boundary |
|---|---|---|
| 1. Git/source capture | Repository, full commit, exact source bytes, line bounds, declared coverage | Byte identity is checked; origin metadata does not establish authorship or ratification. |
| 2. Understand Anything | Raw export, producer revision, source/scope digest → candidate observations | Actual UA extraction remains external; raw graph is preserved as opaque input. |
| 3. Architecture traversal | IDs, dependency/authority cones, gaps and counterexamples → immutable propositions | Observation and candidate meaning carry no admission authority. |
| 4. BIOS theorem evaluation | Derivation, applicability, provenance, abstention, falsification protocol → scoped decision | Independent theorem adjudicator signs; this compiler checks the receipt, not the mathematics. |
| 5. Graph certification and admission | Exact normalized records → certified delta and Kernel admission | Separate certification and Kernel decisions; no authority inferred from links. |
| 6. Execution boundary | Admitted plan → separately authorized runtime and independent outcome witness | Runtime acts elsewhere. Plan hash precedes outcomes; outcome hash binds later evidence. |
| 7. Product qualification | Preregistered criteria and observed outcomes → scoped qualification and commercialization decisions | Scientific validity, customer usefulness, demand and permission are separately recorded. |
| 8. BIOSpub preparation | Qualified transformation and permitted claims → six-record editorial package | Preparation permission and claim approval are verified separately. |
| 9. DigiProse review | Traceable EBA/DBA draft → explicit editorial disposition | Separate exact-asset, account/audience/destination publication decision is still required. |

The proposed flow and requirements are in `workflow_contract.json`. The signed record envelope and payload are defined by closed Pydantic models in `workflow.py`, exported to `schemas/`. They are **new candidate integration schemas**, not a claim of conformance to an unseen authoritative Dossier registry or an existing Kernel API.

## What constitutes a successful transformation here

Success is a non-compensatory conjunction: exact source and raw-UA binding; resolved scoped theorem obligations; independent reconciliation and certification; Kernel graph admission; separately signed execution authorization and observed outcome; product qualification against preregistered criteria; commercialization authorization; scoped editorial preparation; and approval of the bound claims. A later PASS cannot compensate for an earlier gap.

The four theorem obligations are `derivation`, `applicability`, `provenance`, and `abstention`. Their checks are an integration-level entitlement envelope. `SATISFIED` is not universal proof, Canon promotion, a participation warrant, or permission to execute. The actual theorem class, mathematical proof method, authoritative evaluator and certified representation domain must be supplied and reviewed. The existing `MT_BIOS` genesis freeze is not amended by this candidate.

## Run the compiler

Dependencies tested here: Python 3.11+, Pydantic 2.14.1 and cryptography 50.0.2. `requirements.txt` pins the two direct packages; a complete transitive environment lock has not been produced.

```bash
python -m unittest -v test_workflow
python workflow.py --packet fixtures/unbound_packet.json \
  --trust-snapshot fixtures/unbound_trust_snapshot.json \
  --staging-output /tmp/digisleuth-new-held-generation
```

The deliberately unbound fixture returns exit code **2** and a reviewable held bundle. Exit code **0** means only that the supplied evidence passed the candidate compiler's editorial-preparation gates. For actual inputs also pass `--source-root /path/to/checkout` and `--ua-export /path/to/preserved-raw-export.json`. Staging output must be a new directory outside the source checkout and every active vault. Detected `.obsidian` ancestors are rejected; the operator must supply a genuinely nonindexed staging location because absence of that marker does not prove a directory is unindexed.

No API credential is needed by this compiler. No source-provided code is executed. Source bytes are read with Git object commands; raw UA bytes are digest-checked, not interpreted as instructions. New source, theorem, graph, criteria, claim, audience or destination revisions require matching receipts.

## Receipts and trust

`TrustSnapshot` is provisioned by an external operator through a separately protected channel. It binds public keys to named principals/roles and supplies a current revocation snapshot. It is not accepted from the packet itself. Never use the ephemeral test authorities for real data. The program cannot authenticate how a trust-snapshot file was provisioned; deployment must protect that file and the process that loads it.

The first five decisions sign `plan_digest(payload)`, which excludes post-run source records, claim text and observed market-demand status. The five later decisions sign the full payload digest, including those outcomes. This avoids requiring future outcomes before execution authorization. The field `payload_sha256` in an early decision carries that stage's plan digest; both commitments are included in the report. Encoding is the local sorted, compact UTF-8 JSON protocol in `canonical()`, not a claim of RFC 8785 compatibility.

Every decision binds its stage, run, transformation, scope, destination, principal, authority and validity interval. The producer cannot adjudicate its own packet. Semantic reviewer/theorem adjudicator, theorem adjudicator/certifier, and runtime authorizer/outcome observer must be distinct principals. There is exactly one receipt per presented stage; duplicate or unknown stages hold the packet. Historical failures and contradictions remain in source lineage rather than being overwritten.

These checks operate on an offline snapshot. They do not establish non-bypassable production isolation, live revocation ordering, independent CEASE availability, atomic remote commitment, signer competence, or the truth of signed evidence. A production boundary still requires trusted admission services, constrained runtime/writer interfaces, current authorization checks at commitment, continuously available CEASE and readback witnesses against an uncooperative workload.

## Obsidian and BIOSpub outputs

After graph admission, the compiler can stage a native `Execution_Graph.canvas`, Markdown objects, lossless typed relationship records and checksums. All eight relationship coordinates plus source standing are retained in `relations.json`; Canvas edges are navigational views. Activation is still withheld until a separate projection plan/grant and bounded writer/readback protocol are bound. Existing structural topology is never edited by this compiler.

After every editorial gate passes, `biospub/handoff.json` contains the six publication-contract envelopes: source record, claim/evidence map, draft asset, authority record, compilation receipt and disposition. `biospub/DigiProse_Draft.md` includes only supported or explicitly labeled inferred claims, evidence IDs and limitations. Disputed/unresolved claims stay out of the draft. The handoff is `READY_FOR_REVIEW`, not published, and the live BIOSpub transport remains unbound.

The new blueprint notes under `obsidian_staging/blueprint/` are candidate specifications with zero authority. Their Canvas has no transition edges: the current real source remains held. The initial held execution bundle is under `current_run/`. No automatic vault import or structural graph mutation was performed.

## Current standing and lineage

This candidate builds on invocation `UA_OBSIDIAN_BINDING_20261028_01`, commit `d6757c9138cd18d1cfd8dcfeeae6b3ab11ef9d84`, draft PR #7. That invocation preserved `HOLD_SOURCE / SOURCE_SUFFICIENCY_UNESTABLISHED` at observed laboratory head `285089fb54ecb908a2c5f457033290f5de19c09a`.

Still unresolved for a real run: exact local research commit `e05f1e9` and dossier/register bytes; a source-bound UA export; actual Dossier schema/identity/relationship registry; theorem specimen and independent ratification; trusted roles and receipts; runtime and writer bindings; real transformation evidence; and live BIOSpub destination interface. The remote laboratory snapshot is not silently substituted for the missing local research apparatus. Real successful transformations admitted by this workflow: **0**.

No scientific or canonical promotion is conferred by this candidate commit, its tests, its Markdown notes or its Canvas.
