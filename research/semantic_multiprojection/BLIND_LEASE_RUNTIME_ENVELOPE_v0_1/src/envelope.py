from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .integrity import BatteryIntegrityWitness, read_only_integrity_inspection


TERMINAL_STATES = frozenset({"COMPLETED", "ABSTAINED", "INTEGRITY_HALT", "BLINDNESS_BREACH", "EXECUTION_FAULT"})


@dataclass(frozen=True)
class MechanicalPreflight:
    battery_witness: BatteryIntegrityWitness
    terminal_states_closed: bool

    @property
    def passed(self) -> bool:
        return self.battery_witness.manifest_verified and self.battery_witness.unchanged and self.terminal_states_closed


def run_mechanical_preflight(battery_root: Path) -> MechanicalPreflight:
    """Mechanically inspects battery integrity only; never evaluates scientific specimens."""
    witness = read_only_integrity_inspection(battery_root)
    return MechanicalPreflight(witness, TERMINAL_STATES == {
        "COMPLETED", "ABSTAINED", "INTEGRITY_HALT", "BLINDNESS_BREACH", "EXECUTION_FAULT"
    })
