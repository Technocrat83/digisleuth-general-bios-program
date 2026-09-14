"""Single-fixture, fresh-process evaluator ingress."""

from __future__ import annotations

import json
import sys

from validators import validate_dag, validate_six_coordinate, validate_temporal


VALIDATORS = {
    "SERIALIZATION": validate_six_coordinate,
    "GRAPH": validate_dag,
    "TEMPORAL": validate_temporal,
}


def main() -> int:
    request = json.load(sys.stdin)
    surface = request.get("surface")
    if surface not in VALIDATORS:
        result = {"status": "REFUSED", "all_triggered_failures": ["UNKNOWN_SURFACE"]}
    else:
        result = VALIDATORS[surface](request.get("input")).as_dict()
    json.dump(result, sys.stdout, sort_keys=True, separators=(",", ":"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
