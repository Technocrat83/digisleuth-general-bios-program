import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PATH = "Digisleuth/Research/General BIOS/OBSIDIAN_GOVERNED_BRIDGE_PROVENANCE_TEST_v0.1.md"

EXPECTED_SHA256 = (
    "e827fdd1c8e3d5f8930a94157fd8ca24"
    "ec9c1a024af3b2e0a24ee2e1bc84e76c"
)


async def main():
    server = StdioServerParameters(
        command="python",
        args=["server/governed_obsidian_mcp.py"],
        env=dict(os.environ),
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("=== READ-BACK TEST ===")
            read_result = await session.call_tool(
                "read_note",
                {"path": PATH},
            )
            print(read_result)

            print("\n=== REFERENTIAL BINDING TEST ===")
            binding_result = await session.call_tool(
                "verify_referential_binding",
                {
                    "path": PATH,
                    "expected_content_sha256": EXPECTED_SHA256,
                },
            )
            print(binding_result)


if __name__ == "__main__":
    asyncio.run(main())