# Laptop Activation — Physical Vault

1. Open the intended Obsidian vault in Desktop.
2. Settings → Community plugins → browse/install **Local REST API** (the current plugin documentation also describes MCP support).
3. Enable it.
4. Settings → Local REST API → copy the API key. Keep it local; do not paste it into notes or Git.
5. Confirm the HTTPS endpoint/port shown by the plugin (commonly `https://127.0.0.1:27124`).
6. In a terminal, set `OBSIDIAN_API_KEY` and run the appropriate `scripts/test_rest.*` script.
7. Create the provenance ledger note at `Digisleuth/_Governance/PROVENANCE_LEDGER.md` with a heading `# Events`.
8. Install the gateway dependencies:
   `python -m pip install -r server/requirements.txt`
9. Start the gateway locally:
   `python server/governed_obsidian_mcp.py`
10. Register that local stdio MCP server in the OpenAI/Codex MCP client you use on the laptop.

## Safety boundary

The ChatGPT web session itself cannot call your laptop's `127.0.0.1`; localhost is your laptop, not this hosted session. Once the local MCP client is registered, OpenAI/Codex on that machine can invoke the governed tools.
