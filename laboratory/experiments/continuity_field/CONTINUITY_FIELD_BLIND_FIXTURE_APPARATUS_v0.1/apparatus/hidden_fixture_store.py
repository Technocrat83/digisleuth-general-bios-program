"""Harness-only access to complete fixtures. Never pass this object to an operator."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

_FIXTURE_ID = re.compile(r"^CC_F(0[1-9]|1[0-2])$")


class FixtureStoreError(RuntimeError):
    pass


class HiddenFixtureStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve(strict=True)

    def load(self, fixture_id: str) -> Mapping[str, Any]:
        if not _FIXTURE_ID.fullmatch(fixture_id):
            raise FixtureStoreError("invalid fixture identifier")
        path = (self._root / f"{fixture_id}.json").resolve()
        if path.parent != self._root:
            raise FixtureStoreError("fixture path escaped hidden store")
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise FixtureStoreError("fixture unavailable or malformed") from exc
        if value.get("fixture_id") != fixture_id:
            raise FixtureStoreError("fixture identity mismatch")
        required = {"fixture_id", "chamber_id", "operator_input", "witness_artifact", "predicate_bundle"}
        if not required.issubset(value):
            raise FixtureStoreError("fixture is structurally incomplete")
        return deepcopy(value)
