from __future__ import annotations

from dataclasses import dataclass


REQUIRED_SOURCE_COORDINATES = {"identity", "meaning", "provenance", "jurisdiction", "authority"}
REQUIRED_CHAMBERS = {f"MP{i}" for i in range(7)}


@dataclass(frozen=True)
class ReferentialScopeResult:
    source_complete: bool
    preservation_complete: bool
    chamber_set_complete: bool

    @property
    def closed(self) -> bool:
        return self.source_complete and self.preservation_complete and self.chamber_set_complete


def verify_referential_scope(source: dict, preservation: dict, chamber_ids: set[str]) -> ReferentialScopeResult:
    source_complete = REQUIRED_SOURCE_COORDINATES <= set(source)
    preservation_complete = all(
        REQUIRED_SOURCE_COORDINATES <= set(contract)
        for name, contract in preservation.items()
        if name.startswith("Omega_")
    ) and bool(preservation)
    normalized = {cid.split("_", 1)[0] for cid in chamber_ids}
    chamber_set_complete = normalized == REQUIRED_CHAMBERS
    return ReferentialScopeResult(source_complete, preservation_complete, chamber_set_complete)
