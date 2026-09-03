# MCP Client Template

The governed gateway is a local stdio MCP server. Point an MCP-compatible OpenAI/Codex client at the Python entrypoint.

Conceptual configuration:

```json
{
  "server_name": "digisleuth-obsidian-governed",
  "command": "python",
  "args": ["<ABSOLUTE_PATH>/server/governed_obsidian_mcp.py"],
  "env": {
    "OBSIDIAN_API_URL": "https://127.0.0.1:27124",
    "OBSIDIAN_API_KEY": "<LOCAL_REST_API_KEY>",
    "OBSIDIAN_VERIFY_TLS": "false"
  }
}
```

Do not commit the API key. Exact OpenAI/Codex MCP configuration syntax can vary by client/version; use the current client MCP settings surface and preserve this command/env contract.

Exposed capabilities are intentionally narrow:

- `read_note`
- `search_notes`
- `create_governed_note`
- `append_provenance_event`
- `append_to_authorized_heading`
- `verify_referential_binding`

Not exposed:

- delete
- arbitrary overwrite
- arbitrary path write
- Canon admission
- PP
- authority mutation
