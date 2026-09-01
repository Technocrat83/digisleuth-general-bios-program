from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import FrozenSet
from .blinding import BlindnessBreach, assert_payload_intent_blind

class FirewallDenied(PermissionError): pass
ALLOWED_OPERATIONS: FrozenSet[str]=frozenset({"LOAD","EXTRACT","COMPARE","ADJUDICATE","EMIT_RAW_OBSERVATION"})
PROHIBITED_OPERATIONS: FrozenSet[str]=frozenset({"REPAIR","REWRITE","INFER_MISSING","RECONSTRUCT_PROVENANCE","REGENERATE","ALTER_SPECIMEN","ALTER_SOURCE_STATE","ALTER_PRESERVATION_CONTRACT","ALTER_EVALUATOR_CONTRACT","PROMOTE","MUTATE_CANON","MUTATE_PUBLICATION_BIOS","MUTATE_MAGUS","MUTATE_LIVING_FUNNEL"})

@dataclass(frozen=True)
class EvaluatorFirewall:
    readable_roots: tuple[Path,...]
    def authorize_operation(self,operation:str)->None:
        if operation not in ALLOWED_OPERATIONS: raise FirewallDenied(f"operation not authorized: {operation}")
    def authorize_read(self,path:Path)->Path:
        resolved=path.resolve(strict=False)
        if not any(root.resolve(strict=False)==resolved or root.resolve(strict=False) in resolved.parents for root in self.readable_roots): raise FirewallDenied(f"read outside evaluator allowlist: {resolved}")
        return resolved
    def validate_payload(self,payload:dict)->None:
        try: assert_payload_intent_blind(payload)
        except BlindnessBreach as exc: raise FirewallDenied(str(exc)) from exc
