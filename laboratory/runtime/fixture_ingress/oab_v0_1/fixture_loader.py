from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

ALLOWED_FIXTURE_IDS = tuple(f"OAB{i}" for i in range(1, 9))
ALLOWED_FIXTURE_ID_SET = set(ALLOWED_FIXTURE_IDS)
EXPECTED_MANIFEST_ID = "OAB_FIXTURE_INGRESS_MANIFEST_v0.1"
EXPECTED_BATTERY_ID = "OMEGA_ORIENTATION_ADVERSARIAL_BATTERY_01"
EXPECTED_FIXTURE_SCHEMA_VERSION = "OAB_FIXTURE_SHAPE_v0.1"
EXPECTED_LOADER_CONTRACT_VERSION = "OAB_FIXTURE_LOADER_v0.1"
REQUIRED_SEMANTIC_BINDINGS = {
    "delta_encoding_rule": "ORIENTATION_DELTA_CANONICAL_ENCODING_v0.1",
    "localization_rule": "JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v0.1",
    "monitor_rule": "ORIENTATION_INVALIDATION_MONITOR_v0.1",
    "replay_rule": "ORIENTATION_REPLAY_VALIDATOR_v0.1",
}
EXPECTED_AUTHORITY = {"interpretation": 0, "repair": 0, "admission": 0, "execution": 0}
HEX256_RE = re.compile(r"^[0-9a-f]{64}$")

SCHEMA_PATH = Path(__file__).with_name("loader_contract.schema.json")
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
SCHEMA_VALIDATOR = Draft202012Validator(SCHEMA)


class LoaderDisposition(str, Enum):
    LOADED = "LOADED"
    REJECTED = "REJECTED"


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


def _closed_object_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise FixtureIngressError(f"DUPLICATE_JSON_KEY:{key}")
        out[key] = value
    return out


def _reject_constant(value: str):
    raise FixtureIngressError(f"NONSTANDARD_JSON_CONSTANT:{value}")


def _parse_json_bytes(raw: bytes, scope: str) -> Mapping[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FixtureIngressError(f"{scope}:UTF8_REQUIRED") from exc
    try:
        obj = json.loads(text, object_pairs_hook=_closed_object_pairs, parse_constant=_reject_constant)
    except FixtureIngressError:
        raise
    except json.JSONDecodeError as exc:
        raise FixtureIngressError(f"{scope}:INVALID_JSON") from exc
    if not isinstance(obj, dict):
        raise FixtureIngressError(f"{scope}:OBJECT_REQUIRED")
    return obj


def _validate_schema(fixture: Mapping[str, Any]) -> None:
    errors = sorted(SCHEMA_VALIDATOR.iter_errors(fixture), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        path = "$" + "".join(f"[{p!r}]" if not isinstance(p, int) else f"[{p}]" for p in first.path)
        validator = str(first.validator).upper()
        raise FixtureIngressError(f"SCHEMA_REJECT:{validator}:{path}:{first.message}")


def _validate_manifest(manifest: Mapping[str, Any]) -> None:
    expected_keys = {
        "manifest_id", "battery_id", "fixture_schema_version", "loader_contract_version",
        "semantic_bindings", "fixture_root", "fixture_ids", "fixture_sha256", "authority", "boundary_law"
    }
    if set(manifest) != expected_keys:
        raise FixtureIngressError("manifest:FIELD_SET_MISMATCH")
    if manifest["manifest_id"] != EXPECTED_MANIFEST_ID:
        raise FixtureIngressError("manifest:MANIFEST_ID_MISMATCH")
    if manifest["battery_id"] != EXPECTED_BATTERY_ID:
        raise FixtureIngressError("manifest:BATTERY_ID_MISMATCH")
    if manifest["fixture_schema_version"] != EXPECTED_FIXTURE_SCHEMA_VERSION:
        raise FixtureIngressError("manifest:FIXTURE_SCHEMA_VERSION_MISMATCH")
    if manifest["loader_contract_version"] != EXPECTED_LOADER_CONTRACT_VERSION:
        raise FixtureIngressError("manifest:LOADER_CONTRACT_VERSION_MISMATCH")
    if manifest["semantic_bindings"] != REQUIRED_SEMANTIC_BINDINGS:
        raise FixtureIngressError("manifest:RULE_IDENTITY_MISMATCH")
    ids = manifest["fixture_ids"]
    if not isinstance(ids, list) or ids != list(ALLOWED_FIXTURE_IDS) or len(ids) != len(set(ids)):
        raise FixtureIngressError("manifest:FIXTURE_ID_SEQUENCE_MISMATCH")
    if manifest["authority"] != EXPECTED_AUTHORITY:
        raise FixtureIngressError("manifest:AUTHORITY_ENVELOPE_MISMATCH")
    sha_map = manifest["fixture_sha256"]
    if not isinstance(sha_map, dict) or set(sha_map) != ALLOWED_FIXTURE_ID_SET:
        raise FixtureIngressError("manifest:FIXTURE_DIGEST_SET_MISMATCH")
    for fixture_id, digest in sha_map.items():
        if not isinstance(digest, str) or not HEX256_RE.fullmatch(digest):
            raise FixtureIngressError(f"manifest:FIXTURE_DIGEST_FORMAT_INVALID:{fixture_id}")


def load_fixture_bytes(raw_fixture: bytes, *, source_path: str, manifest: Mapping[str, Any]) -> LoadedFixture:
    """Parse and validate one fixture without executing, repairing, or reinterpreting it."""
    _validate_manifest(manifest)
    fixture = _parse_json_bytes(raw_fixture, "fixture")
    _validate_schema(fixture)
    fixture_id = fixture["fixture_id"]
    if fixture["field_delta"]["delta_id"] != fixture_id:
        raise FixtureIngressError("fixture:DELTA_ID_MISMATCH")
    if fixture_id not in manifest["fixture_ids"]:
        raise FixtureIngressError("manifest:FIXTURE_NOT_BOUND")
    digest = _sha256(raw_fixture)
    expected = manifest["fixture_sha256"][fixture_id]
    if digest != expected:
        raise FixtureIngressError("FIXTURE_DIGEST_MISMATCH")
    return LoadedFixture(
        fixture_id=fixture_id,
        source_path=source_path,
        sha256=digest,
        manifest_id=manifest["manifest_id"],
        battery_id=manifest["battery_id"],
        semantic_bindings=dict(manifest["semantic_bindings"]),
        fixture=fixture,
        disposition=LoaderDisposition.LOADED,
    )


def load_fixture_file(fixture_path: Path, *, manifest_path: Path) -> LoadedFixture:
    manifest = _parse_json_bytes(manifest_path.read_bytes(), "manifest")
    return load_fixture_bytes(fixture_path.read_bytes(), source_path=str(fixture_path), manifest=manifest)


__all__ = [
    "FixtureIngressError",
    "LoadedFixture",
    "LoaderDisposition",
    "load_fixture_bytes",
    "load_fixture_file",
]
