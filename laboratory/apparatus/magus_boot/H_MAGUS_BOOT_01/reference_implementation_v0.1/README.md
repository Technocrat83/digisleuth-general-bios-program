# MAGUS Boot Reference Implementation v0.1

**Standing:** MATERIALIZED / UNEXECUTED

This package contains a pure Python reference implementation of the frozen
five-stage MAGUS corpus boot membrane:

`F -> I -> G -> J -> O`

## Boundaries

- No fixture bytes are included.
- No fixture archive was mounted or inspected.
- No expected per-fixture oracle outcomes are encoded.
- No execution sweep was run.
- No writes to foreign corpora are implemented.
- No missing dependency, authority, identity, or orientation data is repaired.
- `J_EX` is always emitted as `LATENT`.
- Materialization does not confer execution authorization.

## Next lawful gate

1. Seal this implementation's digest.
2. Perform oracle-isolation preflight.
3. Obtain explicit execution authorization.
4. Only then mount sealed fixture bytes and perform blind execution.
