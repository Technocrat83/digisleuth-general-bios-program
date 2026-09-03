# DIGISLEUTH_OBSIDIAN_GOVERNED_BRIDGE_v0.1

## Standing

**INSTANTIATED CONFIGURATION BUNDLE — NOT YET CONNECTED TO YOUR PHYSICAL VAULT**

This bundle materializes the Digisleuth **1 + 3** Obsidian architecture:

1. **Obsidian Headless** — separate persistence/sync/automation plane.
3. **Local REST API + governed MCP gateway** — physical-vault interaction plane.

## Constitutional factorization

```text
OpenAI/Codex
    ↓ proposed operation
Governed MCP Gateway
    ↓ predicate + Helm routing
Local REST API
    ↓ authorized topological projection
Obsidian Vault

Separate environment:
Obsidian Headless ↔ synchronized vault clone ↔ Git/persistence
```

### Invariants

- OpenAI write capability != OpenAI topology authority != OpenAI standing authority.
- Helm routing != admission.
- Obsidian represents topology; it does not originate standing.
- Git byte identity and commit lineage remain upstream identity witnesses.
- No downstream stage may repair an upstream identity/provenance deficiency.
- All bridge-originated authority, Canon and PP deltas are fixed at zero.

## Start here

Read `docs/LAPTOP_ACTIVATION.md`, then `docs/HEADLESS_PLANE.md`.

## What this bundle already enforces

- default-deny Helm routing
- object-class envelopes
- no delete capability
- no arbitrary path write
- no existing-note overwrite
- Git path + commit SHA + SHA-256 required before governed note creation
- append-only provenance capability
- zero bridge authority/Canon/PP deltas

## What remains physical

Your laptop must supply:

1. the real vault;
2. Local REST API plugin installation/activation;
3. the locally generated API key;
4. MCP client registration;
5. optionally a separate Headless Sync environment.

Do **not** send the API key back into chat.
