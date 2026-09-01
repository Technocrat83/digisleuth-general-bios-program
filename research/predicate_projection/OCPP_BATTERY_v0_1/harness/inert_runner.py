#!/usr/bin/env python3
"""OCPP inert scaffold. Materialization does not authorize execution."""
from __future__ import annotations

EXECUTION_AUTHORIZED = False

def main() -> None:
    if not EXECUTION_AUTHORIZED:
        raise SystemExit("EXECUTION_LOCKED: separate dispatch authorization required")
    raise SystemExit("NO_RUNTIME_BOUND: materialization scaffold only")

if __name__ == "__main__":
    main()
