from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


HEX128_RE = re.compile(r"^0x[0-9a-fA-F]{32}$")
ALLOWED_FIXTURE_IDS = {f"OAB{i}" for i in range(1, 9)}
ALLOWED_LOCALIZATION = {"LOCALIZED", "NO_MATERIAL_INTERSECTION", "UNRESOLVED"}
ALLOWED_LIFECYCLE = {"CURRENT", "SUSPENDED", "WITHDRAWN"}
REQUIRED_SEMANTIC_BINDINGS = {
    "delta_encoding_rule": "ORIENTATION_DELTA_CANONICAL_ENCODING_v0.1",
    "localization_rule": "JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v0.1",
    "monitor_rule": "ORIENTATION_INVALIDATION_MONITOR_v0.1",
    "replay_rule": "ORIENTATION_REPLAY_VALIDATOR_v0.1",
}


class LoaderDisposition(str, Enum):
    LOADED = "LOADED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class LoadedFixture:
    fixture_id: str
    source_path: str
    sha256: str
    manifest_id: str
    battery_id: str
    semantic_bindings: Mapping[str, str]
    fixture: Mapping[str, Any]
    disposition: LoaderDisposition
    reason: str | None = None


class FixtureIngressError(ValueError):
    pass


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _require_object(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise FixtureIngressError(f"{field}:OBJECT_REQUIRED")
    return value


def _require_fields(obj: Mapping[str, Any], fields: tuple[str, ...], scope: str) -> None:
    missing = [field for field in fields if field not in obj]
    if missing:
        raise FixtureIngressError(f"{scope}:MISSING_REQUIRED_FIELD:{','.join(missing)}")


def _validate_manifest(manifest: Mapping[str, Any]) -> None:
    _require_fields(
        manifest,
        (
            "manifest_id",
            "battery_id",
            "fixture_schema_version",
            "loader_contract_version",
            "semantic_bindings",
            "fixture_ids",
            "authority",
        ),
        "manifest",
    )
    bindings = _require_object(manifest["semantic_bindings"], "semantic_bindings")
    if dict(bindings) != REQUIRED_SEMANTIC_BINDINGS:
        raise FixtureIngressError("manifest:RULE_IDENTITY_MISMATCH")
    fixture_ids = manifest["fixture_ids"]
    if not isinstance(fixture_ids, list) or set(fixture_ids) != ALLOWED_FIXTURE_IDS:
        raise FixtureIngressError("manifest:FIXTURE_ID_SET_MISMATCH")
    authority = _require_object(manifest["authority"], "authority")
    for key in ("interpretation", "repair", "admission", "execution"):
        if authority.get(key) != 0:
            raise FixtureIngressError(f"manifest:AUTHORITY_NONZERO:{key}")


def _validate_jurisdiction_widths(value: Any, path: str = "$.") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}{key}"
            if "jurisdiction" in key.lower() and isinstance(child, str) and child.startswith("0x"):
                if not HEX128_RE.fullmatch(child):
                    raise FixtureIngressError(f"JURISDICTION_WIDTH_INVALID:{child_path}")
            _validate_jurisdiction_widths(child, child_path + ".")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_jurisdiction_widths(child, f"{path}[{index}].")


def _validate_fixture_shape(fixture: Mapping[str, Any]) -> None:
    _require_fields(
        fixture,
        ("fixture_id", "single_fault", "field_delta", "expected_localization", "expected_monitor"),
        "fixture",
    )
    fixture_id = fixture["fixture_id"]
    if fixture_id not in ALLOWED_FIXTURE_IDS:
        raise FixtureIngressError("UNKNOWN_FIXTURE_TYPE")
    if fixture["single_fault"] is not True:
        raise FixtureIngressError("fixture:SINGLE_FAULT_REQUIRED")

    delta = _require_object(fixture["field_delta"], "field_delta")
    _require_fields(
        delta,
        (
            "object_id",
            "delta_id",
            "prior_orientation_hash",
            "prior_graph_hash",
            "current_graph_hash",
            "prior_jurisdiction_hash",
            "current_jurisdiction_hash",
            "prior_provenance_hash",
            "current_provenance_hash",
            "prior_placement_hash",
            "current_placement_hash",
            "prior_state_hash",
            "current_state_hash",
            "prior_boundary_hash",
            "current_boundary_hash",
            "prior_epoch",
            "current_epoch",
            "adjacency_changed",
            "authority_use_attempted",
            "evidence_complete",
        ),
        "field_delta",
    )
    if delta["delta_id"] != fixture_id:
        raise FixtureIngressError("fixture:DELTA_ID_MISMATCH")

    localization = _require_object(fixture["expected_localization"], "expected_localization")
    _require_fields(localization, ("standing", "affected_surfaces", "causal_cone", "jurisdictional_cone"), "expected_localization")
    if localization["standing"] not in ALLOWED_LOCALIZATION:
        raise FixtureIngressError("fixture:LOCALIZATION_DOMAIN_INVALID")

    monitor = _require_object(fixture["expected_monitor"], "expected_monitor")
    _require_fields(
        monitor,
        (
            "lifecycle",
            "historical_orientation_preserved",
            "epistemic_standing_changed",
            "repair_attempted",
            "auto_reorientation",
            "authority_effect",
            "execution_effect",
        ),
        "expected_monitor",
    )
    if monitor["lifecycle"] not in ALLOWED_LIFECYCLE:
        raise FixtureIngressError("fixture:LIFECYCLE_DOMAIN_INVALID")
    if monitor["repair_attempted"] is not False:
        raise FixtureIngressError("fixture:REPAIR_ATTEMPT_DECLARED")
    if monitor["auto_reorientation"] is not False:
        raise FixtureIngressError("fixture:AUTO_REORIENTATION_DECLARED")

    _validate_jurisdiction_widths(fixture)


def load_fixture_bytes(
    raw_fixture: bytes,
    *,
    source_path: str,
    manifest: Mapping[str, Any],
    expected_sha256: str | None = None,
) -> LoadedFixture:
    """Parse and validate one fixture without executing or reinterpreting it."""
    _validate_manifest(manifest)
    digest = _sha256(raw_fixture)
    if expected_sha256 is not None and digest != expected_sha256:
        raise FixtureIngressError("FIXTURE_DIGEST_MISMATCH")

    try:
        fixture = json.loads(raw_fixture.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FixtureIngressError("NONCANONICAL_OR_INVALID_JSON") from exc

    fixture = _require_object(fixture, "fixture")
    _validate_fixture_shape(fixture)
    fixture_id = fixture["fixture_id"]
    if fixture_id not in manifest["fixture_ids"]:
        raise FixtureIngressError("manifest:FIXTURE_NOT_BOUND")

    return LoadedFixture(
        fixture_id=fixture_id,
        source_path=source_path,
        sha256=digest,
        manifest_id=str(manifest["manifest_id"]),
        battery_id=str(manifest["battery_id"]),
        semantic_bindings=dict(manifest["semantic_bindings"]),
        fixture=fixture,
        disposition=LoaderDisposition.LOADED,
    )


def load_fixture_file(
    fixture_path: Path,
    *,
    manifest_path: Path,
    expected_sha256: str | None = None,
) -> LoadedFixture:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return load_fixture_bytes(
        fixture_path.read_bytes(),
        source_path=str(fixture_path),
        manifest=manifest,
        expected_sha256=expected_sha256,
    )


__all__ = [
    "FixtureIngressError",
    "LoadedFixture",
    "LoaderDisposition",
    "load_fixture_bytes",
    "load_fixture_file",
]
