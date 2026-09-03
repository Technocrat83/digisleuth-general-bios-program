"""Digisleuth Governed Obsidian MCP Gateway v0.1.

Purpose: expose a deliberately narrow MCP capability surface over Obsidian Local REST API.
This gateway does NOT expose delete, arbitrary overwrite, Canon admission, PP, or standing origin.
"""
from __future__ import annotations
import os, json, hashlib, urllib.parse
from pathlib import Path
import requests, yaml
from mcp.server.mcpserver import MCPServer

ROOT = Path(__file__).resolve().parents[1]
GOV = yaml.safe_load((ROOT / "config" / "governance.yaml").read_text())
ROUTES = yaml.safe_load((ROOT / "config" / "helm_routes.yaml").read_text())["routes"]

API_URL = os.getenv("OBSIDIAN_API_URL", "https://127.0.0.1:27124").rstrip("/")
API_KEY = os.getenv("OBSIDIAN_API_KEY", "")
VERIFY_TLS = os.getenv("OBSIDIAN_VERIFY_TLS", "false").lower() == "true"
PROVENANCE_LOG = os.getenv("DIGISLEUTH_PROVENANCE_LOG", "Digisleuth/_Governance/PROVENANCE_LEDGER.md")

if not API_KEY:
    raise RuntimeError("OBSIDIAN_API_KEY is required")

mcp = MCPServer("digisleuth-obsidian-governed")

def _headers(extra=None):
    h = {"Authorization": f"Bearer {API_KEY}"}
    if extra: h.update(extra)
    return h

def _url(path: str) -> str:
    safe = "/".join(urllib.parse.quote(p, safe="") for p in path.strip("/").split("/"))
    return f"{API_URL}/vault/{safe}"

def _route(helm: str, object_class: str, artifact_id: str) -> str:
    if helm not in ROUTES:
        raise ValueError("Unknown Helm; default-deny")
    rule = ROUTES[helm]
    if object_class not in rule["allowed_classes"]:
        raise ValueError("Object class is outside Helm envelope")
    name = "".join(c if c.isalnum() or c in "-_." else "_" for c in artifact_id)
    return f'{rule["prefix"]}{name}.md'

def _require_identity(git_path: str, git_commit_sha: str, content_sha256: str):
    if not git_path.strip(): raise ValueError("git_path required")
    if len(git_commit_sha) < 7 or any(c not in "0123456789abcdefABCDEF" for c in git_commit_sha):
        raise ValueError("git_commit_sha must be hexadecimal")
    if len(content_sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in content_sha256):
        raise ValueError("content_sha256 must be exact SHA-256 hex")

def _frontmatter(artifact_id, object_class, helm, standing, jurisdiction_owner, jurisdiction_envelope, git_path, git_commit_sha, content_sha256):
    obj = {
        "artifact_id": artifact_id,
        "object_class": object_class,
        "helm": helm,
        "standing": standing,
        "canon": "BLOCKED",
        "pp": "BLOCKED",
        "authority_delta": 0,
        "scientific_standing_delta": 0,
        "jurisdiction": {"owner": jurisdiction_owner, "envelope": jurisdiction_envelope},
        "git": {"path": git_path, "commit_sha": git_commit_sha, "content_sha256": content_sha256},
        "provenance": {"created_by_surface": "OPENAI_EXECUTION_NODE", "standing_originated_here": False},
    }
    return "---\n" + yaml.safe_dump(obj, sort_keys=False).strip() + "\n---\n"

@mcp.tool()
def read_note(path: str) -> str:
    """Read a note. Read authority only; no standing implications."""
    r = requests.get(_url(path), headers=_headers(), verify=VERIFY_TLS, timeout=15)
    r.raise_for_status()
    return r.text

@mcp.tool()
def search_notes(query: str) -> str:
    """Search vault text. Search does not confer standing."""
    r = requests.post(f"{API_URL}/search/simple/", headers=_headers({"Content-Type":"application/json"}), json={"query": query}, verify=VERIFY_TLS, timeout=15)
    r.raise_for_status()
    return r.text

@mcp.tool()
def create_governed_note(helm: str, object_class: str, artifact_id: str, standing: str,
                         jurisdiction_owner: str, jurisdiction_envelope: str,
                         git_path: str, git_commit_sha: str, content_sha256: str,
                         content: str) -> str:
    """Create a new note only inside a Helm-authorized prefix. Existing-note overwrite is forbidden."""
    _require_identity(git_path, git_commit_sha, content_sha256)
    path = _route(helm, object_class, artifact_id)
    # Refuse overwrite: GET success means object already exists.
    exists = requests.get(_url(path), headers=_headers(), verify=VERIFY_TLS, timeout=10)
    if exists.status_code == 200:
        raise ValueError("Existing note detected; overwrite prohibited")
    body = _frontmatter(artifact_id, object_class, helm, standing, jurisdiction_owner, jurisdiction_envelope,
                        git_path, git_commit_sha, content_sha256)
    body += f"\n{content}"
    r = requests.put(_url(path), headers=_headers({"Content-Type":"text/markdown"}), data=body.encode(), verify=VERIFY_TLS, timeout=15)
    r.raise_for_status()
    return json.dumps({"status":"CREATED", "path": path, "authority_delta":0, "canon_delta":0, "pp":"BLOCKED"})

@mcp.tool()
def append_provenance_event(event_json: str) -> str:
    """Append an immutable provenance event to the configured ledger. No retyping or overwrite."""
    event = json.loads(event_json)
    sd = event.get("standing_delta", {})
    if sd.get("authority") != 0 or sd.get("canon") != 0 or sd.get("pp") != 0:
        raise ValueError("Bridge provenance events may not originate authority/Canon/PP deltas")
    payload = "\n```json\n" + json.dumps(event, indent=2, sort_keys=True) + "\n```\n"
    h = _headers({"Operation":"append", "Target-Type":"heading", "Target":"Events", "Content-Type":"text/plain"})
    r = requests.patch(_url(PROVENANCE_LOG), headers=h, data=payload.encode(), verify=VERIFY_TLS, timeout=15)
    r.raise_for_status()
    return json.dumps({"status":"APPENDED", "ledger":PROVENANCE_LOG})

@mcp.tool()
def append_to_authorized_heading(helm: str, object_class: str, artifact_id: str, heading: str, content: str) -> str:
    """Append to an existing governed note heading. Arbitrary path selection is unavailable."""
    path = _route(helm, object_class, artifact_id)
    h = _headers({"Operation":"append", "Target-Type":"heading", "Target":heading, "Content-Type":"text/plain"})
    r = requests.patch(_url(path), headers=h, data=content.encode(), verify=VERIFY_TLS, timeout=15)
    r.raise_for_status()
    return json.dumps({"status":"APPENDED", "path":path, "heading":heading})

@mcp.tool()
def verify_referential_binding(
    path: str,
    expected_content_sha256: str
) -> str:
    """
    Verify source-content identity inside a governed Obsidian projection.

    Source identity and materialized-object identity are distinct.
    The source body must match the expected Git-backed SHA-256,
    while the complete governed note may possess a different digest.
    """

    r = requests.get(
        _url(path),
        headers=_headers(),
        verify=VERIFY_TLS,
        timeout=15,
    )
    r.raise_for_status()

    raw = r.content
    materialized_sha256 = hashlib.sha256(raw).hexdigest()

    text = raw.decode("utf-8")

    if not text.startswith("---\n"):
        raise ValueError("governed frontmatter missing")

    frontmatter_end = text.find("\n---\n", 4)
    if frontmatter_end < 0:
        raise ValueError("governed frontmatter malformed")

    frontmatter_text = text[4:frontmatter_end]
    source_body = text[frontmatter_end + 5:]

    # create_governed_note inserts one separator newline
    # between the governed frontmatter and source content.
    if source_body.startswith("\n"):
        source_body = source_body[1:]

    metadata = yaml.safe_load(frontmatter_text) or {}

    origin = metadata.get("git", {})
    declared_source_sha256 = origin.get("content_sha256")

    source_actual_sha256 = hashlib.sha256(
    source_body.encode("utf-8")
).hexdigest()

    expected = expected_content_sha256.lower()

    return json.dumps({
        "path": path,
        "expected_source_sha256": expected,
        "declared_source_sha256": declared_source_sha256,
        "actual_source_sha256": source_actual_sha256,
        "materialized_sha256": materialized_sha256,
        "declared_match": (
            isinstance(declared_source_sha256, str)
            and declared_source_sha256.lower() == expected
        ),
        "source_match": source_actual_sha256.lower() == expected,
        "materialized_distinct_from_source": (
            materialized_sha256.lower() != expected
        ),
    })
if __name__ == "__main__":
    mcp.run()