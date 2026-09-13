"""One-shot operator interface. Each invocation creates a new process and temp habitat."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Mapping, Sequence


class OperatorProtocolError(RuntimeError):
    pass


@dataclass(frozen=True)
class OneShotOperator:
    command: Sequence[str]
    timeout_seconds: float = 30.0

    def evaluate(self, x_i: bytes) -> bytes:
        if not self.command:
            raise OperatorProtocolError("operator command is empty")
        clean_env: Mapping[str, str] = {
            "PATH": os.environ.get("PATH", ""),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONHASHSEED": "0",
            "CFBFA_SESSION_MODE": "FRESH_PROCESS_PER_FIXTURE",
        }
        with tempfile.TemporaryDirectory(prefix="cfbfa-session-") as habitat:
            completed = subprocess.run(
                list(self.command),
                input=x_i,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=habitat,
                env=dict(clean_env),
                timeout=self.timeout_seconds,
                check=False,
            )
        if completed.returncode != 0:
            raise OperatorProtocolError("operator failed in isolated session")
        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise OperatorProtocolError("operator residue is not JSON") from exc
        return json.dumps(parsed, sort_keys=True, separators=(",", ":")).encode("utf-8")
