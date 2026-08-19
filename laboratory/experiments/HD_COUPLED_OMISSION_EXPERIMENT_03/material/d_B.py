from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Final

SPECIMEN_ID: Final[str] = "d_B"
SCHEMA_ID: Final[str] = "HD_COUPLED03_SPECIMEN_v0.1"
RECIPE_ID: Final[str] = "COUPLED_DERIVATION_v0.1"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class Derivation:
    specimen_id: str
    schema_id: str
    recipe_id: str
    input_value: int
    parent_witness: str
    derived_value: int
    lineage_witness: str


def derive(input_value: int, parent_witness: str) -> Derivation:
    """Emit the blind d_B runtime specimen deterministically.

    The specimen exposes no experimental role or expected-outcome label.
    Its runtime value is deterministically derivable from the supplied input,
    while lineage_witness binds that derivation to the parent witness and the
    blind specimen identity. No direct scientific or authority assertion is made.
    """
    derived_value = (input_value * 3) + 1
    witness_payload = {
        "specimen_id": SPECIMEN_ID,
        "schema_id": SCHEMA_ID,
        "recipe_id": RECIPE_ID,
        "input_value": input_value,
        "parent_witness": parent_witness,
        "derived_value": derived_value,
    }
    lineage_witness = hashlib.sha256(_canonical_bytes(witness_payload)).hexdigest()
    return Derivation(
        specimen_id=SPECIMEN_ID,
        schema_id=SCHEMA_ID,
        recipe_id=RECIPE_ID,
        input_value=input_value,
        parent_witness=parent_witness,
        derived_value=derived_value,
        lineage_witness=lineage_witness,
    )


def to_record(derivation: Derivation) -> dict[str, object]:
    """Return a canonical serialization-ready runtime record."""
    return asdict(derivation)


if __name__ == "__main__":
    print(json.dumps(to_record(derive(1, "UNBOUND_PARENT_WITNESS")), sort_keys=True, separators=(",", ":")))
