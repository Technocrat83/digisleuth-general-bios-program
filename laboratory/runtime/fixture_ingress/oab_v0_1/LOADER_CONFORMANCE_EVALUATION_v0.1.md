# LOADER_CONFORMANCE_EVALUATION_v0.1

**Class:** STATIC_INGRESS_CONFORMANCE_EVALUATION  
**Scope:** `laboratory/runtime/fixture_ingress/oab_v0_1/`  
**Runner Authority:** NONE  
**Execution Qualification:** NOT GRANTED  
**Canon Delta:** 0  
**PP:** BLOCKED

## Acceptance expression

`PASS_loader = C_schema ∧ C_types ∧ C_manifest ∧ C_bytes ∧ C_negative ∧ C_positive`

## Schema closure verified

- `field_delta.additionalProperties = false`
- all required `field_delta` members have frozen primitive types
- localization standing is closed to `LOCALIZED | NO_MATERIAL_INTERSECTION | UNRESOLVED`
- affected surfaces are closed to the frozen OAB surface enum
- jurisdictional cone members are exactly `0x` + 32 hexadecimal nybbles (128 bits)
- lifecycle is closed to `CURRENT | SUSPENDED | WITHDRAWN`
- historical orientation preservation is `true`
- epistemic standing mutation is `false`
- repair attempt is `false`
- auto reorientation is `false`
- authority effect is `NONE`
- execution effect is closed to `NONE | BLOCKED`
- required provenance and prior-orientation identity fields are non-optional
- no standalone `InvalidationTrigger` field exists in OAB v0.1; trigger semantics are represented by typed delta coordinates plus the closed affected-surface domain

## Manifest authority verified

`battery_manifest.json` binds the exact raw bytes of OAB1–OAB8 through mandatory SHA-256 entries. Caller-supplied optional digests are not used as fixture identity authority.

## Negative ingress receipts

- `FL1_PROVENANCE_STRIP` -> `SCHEMA_REJECT:REQUIRED`
- `FL2_FIELD_DELTA_OVERFLOW` -> `SCHEMA_REJECT:ADDITIONALPROPERTIES`
- `FL3_PRIMITIVE_TYPE_COERCION` -> `SCHEMA_REJECT:TYPE`
- `FL4_UNMAPPED_AFFECTED_SURFACE` -> `SCHEMA_REJECT:ENUM`
- `FL5_JURISDICTION_128BIT_WIDTH` -> `SCHEMA_REJECT:PATTERN`
- `FL6_UNMAPPED_LIFECYCLE` -> `SCHEMA_REJECT:ENUM`
- `FL7_AUTHORITY_EFFECT_CLOSED` -> `SCHEMA_REJECT:CONST`
- `FL8_EXECUTION_EFFECT_CLOSED` -> `SCHEMA_REJECT:ENUM`
- `FL9_HISTORY_REWRITE` -> `SCHEMA_REJECT:CONST`
- `FL10_EPISTEMIC_MUTATION` -> `SCHEMA_REJECT:CONST`
- `FL11_DUPLICATE_JSON_KEY` -> `DUPLICATE_JSON_KEY`
- `FL12_MANIFEST_VERSION_DRIFT` -> `manifest:LOADER_CONTRACT_VERSION_MISMATCH`
- `FL13_MANIFEST_DUPLICATE_ID` -> `manifest:FIXTURE_ID_SEQUENCE_MISMATCH`
- `FL14_MANIFEST_DIGEST_ABSENCE` -> `manifest:FIXTURE_DIGEST_SET_MISMATCH`
- `FL15_RULE_IDENTITY_DRIFT` -> `manifest:RULE_IDENTITY_MISMATCH`
- `FL16_MANIFEST_BYTE_MISMATCH` -> `FIXTURE_DIGEST_MISMATCH`
- `FL17_DELTA_ID_DIVERGENCE` -> `fixture:DELTA_ID_MISMATCH`

## Positive raw-byte receipts

- OAB1 `068101937c391293d1cbb0f4c4d5a9af51b0be6835df903e7e37fc84a9b31ceb`
- OAB2 `e6726a3a6fc8d7dd8319934a54b6c4604418a2545a791b015af0037c1f1d0aa3`
- OAB3 `ade95bdd390c60077d454f72fec3fa29d5e5d423a4e1b12654e42855c3acfd39`
- OAB4 `8b9851ea00fdbe20c0585b568e789b447322292e0d2b6a54621a84e89748f61d`
- OAB5 `129a3c052c6f1eb528bc12e266f9046e464b9bef3707b5c1af19a44d78bd1cd7`
- OAB6 `77b988a2035ff90d6a29539086d9c53030bc6eca0a623cb48db859bcc97aa983`
- OAB7 `0f79a19fdfb5e3b73343be1fa93cffb645c04feec1d977fe8ce7d2e1e8f981a9`
- OAB8 `23e7e4ac2c8db5034eacdbe29d00c582deab0164d079dd0d04b54187634c4b97`

## Adjudication

`C_schema = PASS`  
`C_types = PASS`  
`C_manifest = PASS`  
`C_bytes = PASS`  
`C_negative = PASS`  
`C_positive = PASS`

Therefore static fixture-loader conformance is established for OAB v0.1 under the frozen contract and manifest.

This evaluation does **not** authorize construction or execution of the runtime runner, does not grant orientation execution qualification, and does not alter scientific standing, authority, Canon, or PP.
