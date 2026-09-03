# Headless Persistence Plane

Obsidian Headless is the second half of the 1+3 design.

- Run it on a separate agent/server environment or dedicated clone.
- Do not run Desktop Sync and Headless Sync on the same local vault/device/path.
- Requires Node.js 22+.
- Headless Sync requires an active Obsidian Sync subscription.

Canonical flow:

```text
Laptop Obsidian Desktop
  ↕ Local REST / Governed MCP
OpenAI/Codex Interaction Plane

Separate Headless Vault Clone
  ↕ Obsidian Headless Sync
Git / persistence / automation plane
```

Headless is persistence/synchronization infrastructure. It receives no Canon, standing, or topology sovereignty.
