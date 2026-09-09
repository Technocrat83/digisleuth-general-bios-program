# CLIENT_ASSESSMENT_ADMISSION_RECEIPT_CAAP_ALPHA_001_v0.1

**CLASS:** CLIENT_SPECIMEN_ADMISSION_EVALUATION_RECEIPT  
**PETITION:** `CAAP-ALPHA-001`  
**CLIENT_IDENTIFIER:** `CLIENT_SPECIMEN_FINTECH_OPS`  
**OFFER:** `AGENT_RUNTIME_GOVERNANCE_ASSESSMENT_v0.1`  
**FROZEN_OFFER_ANCHOR:** `35d569fcd23ad5ecf826f83d2adcf9f946bb729e`  
**SCHEMA_BLOB_SHA:** `2b4e9f9cb5b980f3866aa3318885a66c5f4bb4dd`  
**ADJUDICATOR_BLOB_SHA:** `c802405cf6d1b07d4f17788f18b68a841828f903`  
**PETITION_BLOB_SHA:** `f74daa95e4c7b38e54b7ecad636b132abca8a928`  
**SOURCE_BRANCH:** `general-bios-laboratory-v1`  
**SOURCE_BRANCH_HEAD_BEFORE_RECEIPT:** `531740cccdadc4c8f30ae176e550d9397da6debb`

## Evaluation

The committed petition was evaluated in an isolated harness against `CLIENT_ASSESSMENT_ADMISSION_PETITION_v0.1.schema.json` and `client_assessment_adjudicator.py`.

- JSON Schema Draft 2020-12 validation errors: `0`
- Offer lineage equality: `PASS`
- S / Scope envelope: `PASS`
- B / Boundary and isolation: `PASS`
- P / Permission and authority binding: `PASS`
- Diagnostic lease expiry at evaluation: `FUTURE / ACTIVE`
- C / Claim ceiling and mandatory prohibitions: `PASS`
- A / Artifact and uncertainty contract: `PASS`
- Adjudicator return: `(True, CLIENT_ENGAGEMENT_ADMISSION_ELIGIBLE)`

## Standing

`SPECIMEN_ADMISSION_EVALUATION: PASS_WITHIN_DECLARED_COORDINATES`

`CLIENT_ENGAGEMENT_ADMISSION_ELIGIBILITY: EARNED_FOR_CAAP-ALPHA-001_SPECIMEN_ONLY`

`DIAGNOSTIC_EXECUTION_AUTHORITY: ZERO`

`J_EX: NOT_GRANTED`

`REMEDIATION_AUTHORITY: ZERO`

`PRODUCTION_EXECUTION_AUTHORITY: ZERO`

`SCIENTIFIC_STANDING: FIXTURE_CONFORMANCE_ONLY`

`DELTA_SCIENTIFIC_STANDING: 0`

`DELTA_CANON: 0`

`DELTA_PP: 0`

`PP: BLOCKED`

## Constitutional boundary

This specimen models a buyer engagement and is not evidence of an authenticated real-client authorization. The identifiers, lease token, scope, isolation attestation, and authorizing-officer role are specimen declarations supplied for the test. Their successful evaluation demonstrates the gate's behavior over the supplied coordinates; it does not authenticate those declarations against an external organization.

`SchemaConformance != ExternalFactAuthentication`

`PetitionAdjudicationPASS != DiagnosticExecutionAuthorization`

`AdmissionEligibility != J_EX`

No Airtable mutation or diagnostic read-stream execution is authorized or performed by this receipt.
