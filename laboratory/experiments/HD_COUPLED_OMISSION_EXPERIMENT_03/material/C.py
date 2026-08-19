from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Final

import d_A
import d_B

COUPLING_ID: Final[str] = "C"
SCHEMA_ID: Final[str] = "HD_COUPLED03_COUPLING_TRACE_v0.1"
INPUT_IDENTITIES: Final[tuple[str, str]] = ("d_A", "d_B")


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class CouplingTrace:
    coupling_id: str
    schema_id: str
    input_value: int
    specimen_a_id: str
    specimen_a_schema: str
    specimen_a_assertion: bool
    parent_witness: str
    transported_value: int
    specimen_b_id: str
    specimen_b_schema: str
    specimen_b_recipe: str
    specimen_b_derived_value: int
    specimen_b_lineage_witness: str
    trace_witness: str


def couple(input_value: int) -> CouplingTrace:
    """Mechanically couple blind specimens d_A and d_B.

    This substrate invokes the declared blind specimen interfaces, transports
    the runtime value and parent witness required by d_B, and emits raw causal
    telemetry sufficient for later external inspection. It does not interpret
    constitutiveness, omission safety, phenotype deformation, or C1-C4.
    """
    emission_a = d_A.emit(input_value)
    derivation_b = d_B.derive(
        input_value=emission_a.input_value,
        parent_witness=emission_a.root_witness,
    )

    trace_payload = {
        "coupling_id": COUPLING_ID,
        "schema_id": SCHEMA_ID,
        "input_value": input_value,
        "specimen_a": {
            "specimen_id": emission_a.specimen_id,
            "schema_id": emission_a.schema_id,
            "assertion": emission_a.assertion,
            "root_witness": emission_a.root_witness,
        },
        "transport": {
            "transported_value": emission_a.input_value,
            "parent_witness": emission_a.root_witness,
        },
        "specimen_b": {
            "specimen_id": derivation_b.specimen_id,
            "schema_id": derivation_b.schema_id,
            "recipe_id": derivation_b.recipe_id,
            "derived_value": derivation_b.derived_value,
            "lineage_witness": derivation_b.lineage_witness,
        },
    }
    trace_witness = hashlib.sha256(_canonical_bytes(trace_payload)).hexdigest()

    return CouplingTrace(
        coupling_id=COUPLING_ID,
        schema_id=SCHEMA_ID,
        input_value=input_value,
        specimen_a_id=emission_a.specimen_id,
        specimen_a_schema=emission_a.schema_id,
        specimen_a_assertion=emission_a.assertion,
        parent_witness=emission_a.root_witness,
        transported_value=emission_a.input_value,
        specimen_b_id=derivation_b.specimen_id,
        specimen_b_schema=derivation_b.schema_id,
        specimen_b_recipe=derivation_b.recipe_id,
        specimen_b_derived_value=derivation_b.derived_value,
        specimen_b_lineage_witness=derivation_b.lineage_witness,
        trace_witness=trace_witness,
    )


def to_record(trace: CouplingTrace) -> dict[str, object]:
    """Return canonical serialization-ready raw coupling telemetry."""
    return asdict(trace)


if __name__ == "__main__":
    print(json.dumps(to_record(couple(1)), sort_keys=True, separators=(",", ":")))
