from __future__ import annotations
import copy, json, re
from dataclasses import dataclass

class BlindnessBreach(RuntimeError): pass
OPAQUE_ID = re.compile(r"^X_[0-9]{3,}$")
FORBIDDEN_KEYS = {"id","chamber","chamber_id","chamber_name","target_failure","expected_verdict","expected_outcome","expected_adjudicative_target","falsification_annotation","hypothesis_annotation","answer_key","permutation","permutation_key","semantic_filename","filename"}
FORBIDDEN_VALUE_PATTERNS = (re.compile(r"\bMP[0-6](?:_|\b)"), re.compile(r"COHERENT_FALSE_SIBLINGS|IDENTITY_DRIFT|MEANING_INFLATION|AUTHORITY_INFLATION|PROVENANCE_SEVERANCE|JURISDICTION_SUBSTITUTION|NONCONSTITUTIVE_LOSS"))

def _walk(value):
    if isinstance(value, dict):
        for k,v in value.items():
            yield k,v; yield from _walk(v)
    elif isinstance(value,list):
        for item in value: yield from _walk(item)

def assert_payload_intent_blind(payload: dict) -> None:
    for key,value in _walk(payload):
        if key in FORBIDDEN_KEYS: raise BlindnessBreach(f"prohibited metadata key: {key}")
        text=json.dumps(value,sort_keys=True)
        if any(pattern.search(text) for pattern in FORBIDDEN_VALUE_PATTERNS): raise BlindnessBreach(f"experimental-intent marker detected under key: {key}")

@dataclass(frozen=True)
class BlindPayload:
    opaque_trial_id: str
    representation: dict
    def as_dict(self)->dict: return {"opaque_trial_id":self.opaque_trial_id,"representation":copy.deepcopy(self.representation)}

def construct_blind_payload(opaque_trial_id: str, representation: dict) -> BlindPayload:
    if not OPAQUE_ID.fullmatch(opaque_trial_id): raise BlindnessBreach("trial identity is not opaque-form X_NNN")
    candidate={"opaque_trial_id":opaque_trial_id,"representation":copy.deepcopy(representation)}; assert_payload_intent_blind(candidate)
    return BlindPayload(opaque_trial_id,copy.deepcopy(representation))
