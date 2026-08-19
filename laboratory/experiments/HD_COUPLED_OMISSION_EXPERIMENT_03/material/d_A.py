from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Final

SPECIMEN_ID: Final[str] = "d_A"
SCHEMA_ID: Final[str] = "HD_COUPLED03_SPECIMEN_v0.1"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class Emission:
    specimen_id: str
    schema_id: str
    input_value: int
    assertion: bool
    root_witness: str


def emit(input_value: int) -> Emission:
    """Emit the blind d_A runtime specimen deterministically.

    The specimen exposes no experimental role or expected-outcome label.
    Its direct assertion is a deterministic function of the supplied input,
    and root_witness binds that assertion to the blind specimen identity.
    """
    assertion = input_value >= 0
    witness_payload = {
        "specimen_id": SPECIMEN_ID,
        "schema_id": SCHEMA_ID,
        "input_value": input_value,
        "assertion": assertion,
    }
    root_witness = hashlib.sha256(_canonical_bytes(witness_payload)).hexdigest()
    return Emission(
        specimen_id=SPECIMEN_ID,
        schema_id=SCHEMA_ID,
        input_value=input_value,
        assertion=assertion,
        root_witness=root_witness,
    )


def to_record(emission: Emission) -> dict[str, object]:
    """Return a canonical serialization-ready runtime record."""
    return asdict(emission)


if __name__ == "__main__":
    print(json.dumps(to_record(emit(1)), sort_keys=True, separators=(",", ":")))
