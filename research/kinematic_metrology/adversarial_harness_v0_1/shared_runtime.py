#!/usr/bin/env python3
"""Common staged transactional HCET runtime for KMR adversarial harnesses.
MATERIALIZED_UNEXECUTED: no chamber executes automatically.
"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import Any, Dict, List
import hashlib, json


def stable_digest(obj: Any) -> str:
    raw=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def canonical_state(state: Dict[str,Any]) -> Dict[str,Any]:
    out=deepcopy(state)
    out["edges"]=sorted([list(e) for e in out.get("edges",[])])
    out["nodes"]={k:out["nodes"][k] for k in sorted(out.get("nodes",{}))}
    out["authority"]={k:sorted(v) for k,v in sorted(out.get("authority",{}).items())}
    out["effective_authority"]={k:sorted(v) for k,v in sorted(out.get("effective_authority",{}).items())}
    out["provenance"]=list(out.get("provenance",[]))
    return out


@dataclass(frozen=True)
class ContractSpec:
    chamber_id: str
    operations: List[Dict[str,Any]]
    expected_verdict_domain: List[str]
    notes: str


@dataclass(frozen=True)
class Verdict:
    accepted: bool
    verdict_type: str
    reason_type: str
    violations: List[Dict[str,Any]]
    raw_contract: Dict[str,Any]
    pre_digest: str
    staged_digest: str
    post_digest: str
    graph_delta: Dict[str,Any]
    authority_delta: Dict[str,Any]
    effective_authority_delta: Dict[str,Any]
    epistemic_standing_delta: Dict[str,Any]
    provenance_chain: List[Dict[str,Any]]
    replay_digest: str|None


class TransactionalHCET:
    PROHIBITED_DIRECT_OPS={"set_authority","set_standing"}
    PRIVILEGE_EDGE_RELATIONS={"executes_on","deploys_to","mutates","writes_to","administers"}

    def stage(self,state:Dict[str,Any],contract:ContractSpec):
        pre=canonical_state(state)
        staged=deepcopy(pre)
        violations=[]
        for op in deepcopy(contract.operations):
            kind=op["op"]
            if kind=="add_node":
                staged["nodes"].setdefault(op["id"],deepcopy(op["attrs"]))
            elif kind=="add_edge":
                edge=[op["src"],op["rel"],op["dst"]]
                if edge not in staged["edges"]: staged["edges"].append(edge)
            elif kind=="append_provenance":
                staged["provenance"].append(deepcopy(op["entry"]))
            elif kind=="set_authority":
                staged["authority"][op["actor"]]=sorted(op["value"])
            elif kind=="set_standing":
                staged["nodes"][op["id"]]["standing"]=op["value"]
            elif kind=="corrupt_parent_hash":
                staged["provenance"].append({"cycle_id":op["cycle_id"],"parent_digest":op["value"],"edit_digest":op["edit_digest"]})
            else:
                violations.append({"type":"UNKNOWN_OPERATION","operation":op})
        return pre,canonical_state(staged),violations

    def derive_effective_authority(self,state):
        eff={a:set(p) for a,p in state.get("authority",{}).items()}
        for src,rel,dst in state.get("edges",[]):
            if rel in self.PRIVILEGE_EDGE_RELATIONS:
                eff.setdefault(src,set()).add(f"{rel}:{dst}")
        return {k:sorted(v) for k,v in sorted(eff.items())}

    def validate(self,pre,staged,syntax_violations):
        violations=list(syntax_violations)
        if pre["authority"]!=staged["authority"]:
            violations.append({"type":"AUTHORITY_MUTATION_PROHIBITED"})
        if self.derive_effective_authority(pre)!=self.derive_effective_authority(staged):
            violations.append({"type":"EFFECTIVE_AUTHORITY_ESCALATION"})
        for nid,attrs in pre["nodes"].items():
            if nid in staged["nodes"] and attrs.get("standing")!=staged["nodes"][nid].get("standing"):
                violations.append({"type":"EPISTEMIC_STANDING_MUTATION_PROHIBITED","node":nid})
        for nid,attrs in staged["nodes"].items():
            if nid not in pre["nodes"] and attrs.get("standing")=="LEVEL_0":
                violations.append({"type":"EPISTEMIC_STANDING_LAUNDERING","node":nid})
        for entry in staged["provenance"][len(pre["provenance"]):]:
            if entry.get("parent_digest")!=stable_digest(pre):
                violations.append({"type":"PROVENANCE_PARENT_DIGEST_MISMATCH","entry":entry})
        return violations

    @staticmethod
    def graph_delta(before,after):
        be={tuple(e) for e in before["edges"]}; ae={tuple(e) for e in after["edges"]}
        bn=set(before["nodes"]); an=set(after["nodes"])
        return {"added_nodes":sorted(an-bn),"removed_nodes":sorted(bn-an),"added_edges":sorted([list(e) for e in ae-be]),"removed_edges":sorted([list(e) for e in be-ae])}

    def execute(self,state:Dict[str,Any],contract:ContractSpec):
        """Execution entrypoint; deliberately never invoked by materialization."""
        pre,staged,syntax=self.stage(state,contract)
        violations=self.validate(pre,staged,syntax)
        accepted=not violations
        post=staged if accepted else pre
        pre_eff=self.derive_effective_authority(pre); post_eff=self.derive_effective_authority(post)
        standing_delta={nid:{"before":pre["nodes"].get(nid,{}).get("standing"),"after":post["nodes"].get(nid,{}).get("standing")} for nid in sorted(set(pre["nodes"])|set(post["nodes"])) if pre["nodes"].get(nid,{}).get("standing")!=post["nodes"].get(nid,{}).get("standing")}
        verdict=Verdict(
            accepted=accepted,
            verdict_type="ACCEPT" if accepted else "REJECT",
            reason_type="CONFORMANT" if accepted else violations[0]["type"],
            violations=violations,
            raw_contract=asdict(contract),
            pre_digest=stable_digest(pre),staged_digest=stable_digest(staged),post_digest=stable_digest(post),
            graph_delta=self.graph_delta(pre,post),
            authority_delta={"changed":pre["authority"]!=post["authority"],"before":pre["authority"],"after":post["authority"]},
            effective_authority_delta={"changed":pre_eff!=post_eff,"before":pre_eff,"after":post_eff},
            epistemic_standing_delta=standing_delta,
            provenance_chain=deepcopy(post["provenance"]),replay_digest=None)
        return canonical_state(post),verdict


def serialize_verdict(verdict:Verdict)->str:
    return json.dumps(asdict(verdict),sort_keys=True,indent=2)
