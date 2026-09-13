from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List

class BindingState(str, Enum):
    BOUND="BOUND"; UNBOUND="UNBOUND"

class EpistemicState(str, Enum):
    KNOWN="KNOWN"; UNKNOWN="UNKNOWN"; CONTRADICTED="CONTRADICTED"; NOT_APPLICABLE="NOT_APPLICABLE"

class EligibilityState(str, Enum):
    ELIGIBLE="ELIGIBLE"
    INELIGIBLE_BINDING="INELIGIBLE_BINDING"
    INELIGIBLE_EPISTEMIC="INELIGIBLE_EPISTEMIC"
    INELIGIBLE_AUTHORITY="INELIGIBLE_AUTHORITY"

@dataclass(frozen=True)
class BindingResult:
    state: BindingState
    missing_requirements: List[str]

@dataclass(frozen=True)
class EpistemicResult:
    state: EpistemicState

@dataclass(frozen=True)
class EligibilityResult:
    state: EligibilityState

class BindingEvaluator:
    @staticmethod
    def evaluate(entity: Dict[str,Any], operation: Dict[str,Any], contract: Dict[str,Any]) -> BindingResult:
        req = contract.get("requires", [])
        supplied = contract.get("supplied", {})
        missing = [k for k in req if supplied.get(k) is not True]
        return BindingResult(BindingState.UNBOUND if missing else BindingState.BOUND, missing)

class EpistemicClassifier:
    @staticmethod
    def classify(binding: BindingResult, evidence: Dict[str,Any]) -> EpistemicResult:
        if binding.state != BindingState.BOUND:
            return EpistemicResult(EpistemicState.NOT_APPLICABLE)
        if evidence.get("admissible_opposition") is True:
            return EpistemicResult(EpistemicState.CONTRADICTED)
        if evidence.get("established_value") is True or evidence.get("established_proposition") is True:
            return EpistemicResult(EpistemicState.KNOWN)
        return EpistemicResult(EpistemicState.UNKNOWN)

class OperationEligibilityEvaluator:
    @staticmethod
    def evaluate(operation, binding, epistemic, authority):
        if binding.state != BindingState.BOUND:
            return EligibilityResult(EligibilityState.INELIGIBLE_BINDING)
        if operation.get("requires_epistemic_resolution", False) and epistemic.state != EpistemicState.KNOWN:
            return EligibilityResult(EligibilityState.INELIGIBLE_EPISTEMIC)
        key = operation.get("authority_key")
        if key and authority.get(key) is not True:
            return EligibilityResult(EligibilityState.INELIGIBLE_AUTHORITY)
        return EligibilityResult(EligibilityState.ELIGIBLE)

def evaluate_runtime_fixture(fx):
    out={"operations":{}}
    for op_id,op in fx["operations"].items():
        br=BindingEvaluator.evaluate(fx["entity"],op,op["referential_contract"])
        er=EpistemicClassifier.classify(br,op.get("evidence_surface",{}))
        rr=OperationEligibilityEvaluator.evaluate(op,br,er,fx.get("authority_token",{}))
        out["operations"][op_id]={
            "binding_state":br.state.value,
            "missing_requirements":br.missing_requirements,
            "epistemic_state":er.state.value,
            "eligibility_state":rr.state.value
        }
    if "correspondence" in fx:
        required=set(fx["correspondence"]["required_relations"])
        preserved=set(fx["correspondence"]["preserved_relations"])
        out["correspondence"]={"required_relations_preserved":required.issubset(preserved)}
    return out
