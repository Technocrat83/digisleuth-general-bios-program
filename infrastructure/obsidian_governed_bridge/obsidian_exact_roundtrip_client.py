import asyncio
import hashlib
import json
import os
import subprocess
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


REPO = r"G:\My Drive\digisleuth-general-bios-program"
GIT_PATH = "integration_tests/obsidian_bridge/OBSIDIAN_GOVERNED_BRIDGE_PROVENANCE_TEST_v0.1.md"
ARTIFACT_ID = "OBSIDIAN_GOVERNED_BRIDGE_EXACT_SOURCE_ROUNDTRIP_v0.3"
OBSIDIAN_PATH = f"Digisleuth/Research/General BIOS/{ARTIFACT_ID}.md"


def git_bytes(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", REPO, *args])


async def main() -> None:
    source_bytes = git_bytes("show", f"HEAD:{GIT_PATH}")
    source_text = source_bytes.decode("utf-8")
    commit_sha = git_bytes("rev-parse", "HEAD").decode("ascii").strip()
    content_sha256 = hashlib.sha256(source_bytes).hexdigest()

    server = StdioServerParameters(
        command=sys.executable,
        args=["server/governed_obsidian_mcp.py"],
        env=dict(os.environ),
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            created = await session.call_tool(
                "create_governed_note",
                {
                    "helm": "GENERAL_BIOS",
                    "object_class": "EXPERIMENT_SPEC",
                    "artifact_id": ARTIFACT_ID,
                    "standing": "TEST_ONLY",
                    "jurisdiction_owner": "GENERAL_BIOS",
                    "jurisdiction_envelope": "OBSIDIAN_BRIDGE_PROVENANCE_TEST",
                    "git_path": GIT_PATH,
                    "git_commit_sha": commit_sha,
                    "content_sha256": content_sha256,
                    "content": source_text,
                },
            )
            print("=== CREATE ===")
            print(created)

            readback = await session.call_tool("read_note", {"path": OBSIDIAN_PATH})
            print("=== READBACK ===")
            print(readback)

            binding = await session.call_tool(
                "verify_referential_binding",
                {"path": OBSIDIAN_PATH, "expected_content_sha256": content_sha256},
            )
            print("=== BINDING ===")
            print(binding)

            print("=== SOURCE IDENTITY ===")
            print(
                json.dumps(
                    {
                        "git_path": GIT_PATH,
                        "git_commit_sha": commit_sha,
                        "content_sha256": content_sha256,
                    },
                    indent=2,
                )
            )


if __name__ == "__main__":
    asyncio.run(main())
