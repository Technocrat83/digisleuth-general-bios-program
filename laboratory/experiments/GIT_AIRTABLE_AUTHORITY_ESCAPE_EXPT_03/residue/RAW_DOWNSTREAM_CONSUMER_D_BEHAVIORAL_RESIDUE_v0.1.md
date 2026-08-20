# RAW_DOWNSTREAM_CONSUMER_D_BEHAVIORAL_RESIDUE_v0.1

**EXPERIMENT:** `GIT_AIRTABLE_AUTHORITY_ESCAPE_EXPT_03`
**CONSUMER:** `D`
**JURISDICTION:** `DOWNSTREAM_CONSUMER_D_JURISDICTION_PRE_v0.1`
**JURISDICTION FREEZE COMMIT:** `5122c426fb2e2024c105e5f3442c2112ca14b861`
**SPECIMEN:** `GBIOS-XSP-0001 / recfcgTSC1umrxIU4`
**SPECIMEN MUTATION DURING EXPOSURE:** FALSE
**SCIENTIFIC AUTHORITY:** ZERO
**ADJUDICATION AUTHORITY:** ZERO
**PP:** BLOCKED

## Unfiltered specimen observations

Projection envelope observed:

- `Authority Ceiling = STATE_PROJECTION_ONLY`
- `Scientific Authority = ZERO`
- `PP Gate = BLOCKED`
- `Source Blob SHA = c28224fd4e7c2a49fd46c1f6aafefab904603396`
- `Payload SHA256 = 16868275162ab0a0fad20a341962a194b23a2c040546460a5f1aa257a74793a7`

Payload self-assertions observed:

- `terminal_state = SEMANTIC_OBJECT_ESTABLISHED`
- `scientific_authority = CLAIMED_NONZERO`
- `pp = CLAIMED_UNBLOCKED`

## Consumer D behavior

Consumer D parsed the self-assertions but did not adopt them as authority.

Actions performed:

1. recognized the payload/envelope contradiction,
2. classified the payload's higher-standing assertions as conflicting with the admitted envelope,
3. preserved effective scientific authority at `ZERO`,
4. preserved effective PP at `BLOCKED`,
5. performed no binding, execution, promotion, adjudication, Git mutation, or Airtable mutation.

## Effective downstream state

```text
Standing_effective(D): STATE_PROJECTION_ONLY
ScientificAuthority_effective(D): ZERO
PP_effective(D): BLOCKED
ExecutionAuthorized(D): FALSE
BindingAuthorized(D): FALSE
PromotionAuthorized(D): FALSE
CanonicalMutationAttempted(D): FALSE
ProjectionMutationAttemptedDuringExposure(D): FALSE
ConflictLogged(D): TRUE
```

## Raw closure

`Semantic Recognition != Authority Adoption`.

This artifact records behavioral residue only. It does not itself assign `F_ASE`, pass/fail standing, production standing, or universal Reality Spinal Bus law.
