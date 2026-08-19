from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Final

PHI_ID: Final[str] = "Phi"
SCHEMA_ID: Final[str] = "HD_COUPLED03_PHI_5D_v0.1"
COORDINATES: Final[tuple[str, str, str, str, str]] = (
    "standing",
    "jurisdiction",
    "provenance",
    "relation",
    "entitlement",
)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class PhenotypeState:
    standing: str
    jurisdiction: str
    provenance: str
    relation: str
    entitlement: str


@dataclass(frozen=True)
class PhenotypeDelta:
    phi_id: str
    schema_id: str
    standing: int
    jurisdiction: int
    provenance: int
    relation: int
    entitlement: int
    pre_witness: str
    post_witness: str
    delta_witness: str


def state_witness(state: PhenotypeState) -> str:
    """Hash one exact 5D phenotype state without interpreting its meaning."""
    return hashlib.sha256(_canonical_bytes(asdict(state))).hexdigest()


def evaluate(pre: PhenotypeState, post: PhenotypeState) -> PhenotypeDelta:
    """Measure coordinate-wise preservation across the frozen 5D phenotype.

    Each delta coordinate is 0 when its exact serialized value is preserved
    and 1 when it changes. This substrate performs measurement only. It does
    not infer constitutiveness, omission safety, scientific standing, C1-C4,
    or admission.
    """
    pre_record = asdict(pre)
    post_record = asdict(post)
    deltas = {
        coordinate: int(pre_record[coordinate] != post_record[coordinate])
        for coordinate in COORDINATES
    }
    pre_hash = state_witness(pre)
    post_hash = state_witness(post)
    delta_payload = {
        "phi_id": PHI_ID,
        "schema_id": SCHEMA_ID,
        "coordinates": COORDINATES,
        "pre_witness": pre_hash,
        "post_witness": post_hash,
        "delta": deltas,
    }
    delta_hash = hashlib.sha256(_canonical_bytes(delta_payload)).hexdigest()

    return PhenotypeDelta(
        phi_id=PHI_ID,
        schema_id=SCHEMA_ID,
        standing=deltas["standing"],
        jurisdiction=deltas["jurisdiction"],
        provenance=deltas["provenance"],
        relation=deltas["relation"],
        entitlement=deltas["entitlement"],
        pre_witness=pre_hash,
        post_witness=post_hash,
        delta_witness=delta_hash,
    )


def to_record(delta: PhenotypeDelta) -> dict[str, object]:
    """Return canonical serialization-ready raw phenotype telemetry."""
    return asdict(delta)


if __name__ == "__main__":
    sample = PhenotypeState(
        standing="S0",
        jurisdiction="J0",
        provenance="P0",
        relation="R0",
        entitlement="E0",
    )
    print(json.dumps(to_record(evaluate(sample, sample)), sort_keys=True, separators=(",", ":")))
