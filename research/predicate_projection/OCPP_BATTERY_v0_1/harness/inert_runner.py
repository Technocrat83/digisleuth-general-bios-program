#!/usr/bin/env python3
"""OCPP inert dispatch-binding surface.

This file proves only that the observation runtime is structurally bound behind
a denied dispatch gate. It does not invoke observation functions or chambers.
"""
from __future__ import annotations

import ocpp_observation_runtime as observation_runtime

EXECUTION_AUTHORIZED = False
DISPATCH_AUTHORIZED = False


def main() -> None:
    if EXECUTION_AUTHORIZED or DISPATCH_AUTHORIZED:
        raise SystemExit("EXECUTION_LOCK_INTEGRITY_FAILURE")
    observation_runtime.assert_dispatch_locked()
    raise SystemExit("EXECUTION_LOCKED: observation runtime bound but not invocable")


if __name__ == "__main__":
    main()
