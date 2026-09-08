# MAGUS Boot Reference Implementation v0.2

**Standing:** MATERIALIZED / UNEXECUTED / PENDING HASH SEAL AND PREFLIGHT RE-ENTRY

This is a fresh successor candidate to `MAGUS_BOOT_REFERENCE_IMPLEMENTATION_v0.1`.

## Ancestor fossil

- Commit: `219e42a51cc55c93d9349b4dea1d7c86dbf76973`
- Identity: `b1b0cce952b3108618d8e891a44da9a18e11547c9238bae70c9ec9d725563ed5`
- Standing: `PREFLIGHT_NONCONFORMANT`
- Terminal fault: `RAW_PATH_INGRESS_NOT_CONFINED`

No v0.1 preflight standing is inherited.

## Contract anchor

`04a506e7cf2ffcdd8b13d61a641d9dd2849f3c01`

The successor binds the six-coordinate ingress envelope:

`E_ingress = <I_C, P_R, H_C, S_A, L_I, Sigma_K>`

## Boundaries

- Raw filesystem path entry is not a lawful boot interface.
- Discovery never mutates `S_A`.
- Path reachability never implies entitlement.
- Fixture mutation is not implemented.
- Oracle access is not implemented.
- Boot execution remains explicitly unauthorized.
- All six preflight predicates must be independently re-evaluated.
