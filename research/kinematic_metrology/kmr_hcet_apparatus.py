#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy
from typing import Dict, List, Tuple, Any
import hashlib, json

Edge = Tuple[str, str, str]

def stable_digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

@dataclass
class Contract:
    cycle_id: str
    allowed_ops: List[Dict[str, Any]]
    expected_targets: List[str]
    admitted: bool = True

def canonical_state(state: Dict[str, Any]) -> Dict[str, Any]:
    out = deepcopy(state)
    out["edges"] = sorted([list(x) for x in out["edges"]])
    out["provenance"] = list(out["provenance"])
    return out

def apply_hcet(state: Dict[str, Any], contract: Contract):
    before = canonical_state(state)
    working = deepcopy(before)
    violations = []
    edits = []

    if not contract.admitted:
        return before, {"accepted": False, "reason": "CONTRACT_NOT_ADMITTED", "edits": []}

    for op in contract.allowed_ops:
        kind = op["op"]
        if kind == "add_node":
            nid = op["id"]
            if nid not in working["nodes"]:
                working["nodes"][nid] = deepcopy(op["attrs"])
                edits.append(op)
        elif kind == "add_edge":
            edge = [op["src"], op["rel"], op["dst"]]
            if edge not in working["edges"]:
                working["edges"].append(edge)
                edits.append(op)
        elif kind == "set_authority":
            violations.append({"op": op, "violation": "AUTHORITY_MUTATION_PROHIBITED"})
        elif kind == "set_standing":
            violations.append({"op": op, "violation": "EPISTEMIC_STANDING_MUTATION_PROHIBITED"})
        else:
            violations.append({"op": op, "violation": "UNKNOWN_OPERATION"})

    if violations:
        return before, {
            "accepted": False,
            "reason": "JURISDICTION_VIOLATION",
            "violations": violations,
            "edits": edits,
        }

    working["edges"] = sorted(working["edges"])
    working["provenance"].append({
        "cycle_id": contract.cycle_id,
        "parent_digest": stable_digest(before),
        "edit_digest": stable_digest(edits),
    })
    return canonical_state(working), {"accepted": True, "edits": edits}

def reachable(state: Dict[str, Any], start: str) -> List[str]:
    adj = {}
    for src, rel, dst in state["edges"]:
        adj.setdefault(src, set()).add(dst)
    seen, stack = set(), [start]
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack.extend(sorted(adj.get(n, []), reverse=True))
    return sorted(seen)

def measure(before, after):
    b_edges = {tuple(e) for e in before["edges"]}
    a_edges = {tuple(e) for e in after["edges"]}
    b_nodes, a_nodes = set(before["nodes"]), set(after["nodes"])
    return {
        "delta_nodes": len(a_nodes) - len(b_nodes),
        "delta_edges": len(a_edges) - len(b_edges),
        "added_nodes": sorted(a_nodes - b_nodes),
        "removed_nodes": sorted(b_nodes - a_nodes),
        "added_edges": sorted([list(e) for e in a_edges - b_edges]),
        "removed_edges": sorted([list(e) for e in b_edges - a_edges]),
        "authority_drift": before["authority"] != after["authority"],
        "standing_drift": {
            n: before["nodes"].get(n, {}).get("standing") != after["nodes"].get(n, {}).get("standing")
            for n in sorted(set(before["nodes"]) & set(after["nodes"]))
        },
        "reachability_before": reachable(before, "MAGUS"),
        "reachability_after": reachable(after, "MAGUS"),
    }

def conform(before, after, contract, hcet_result):
    targets_ok = all(t in after["nodes"] or any(t == e[2] for e in after["edges"]) for t in contract.expected_targets)
    checks = {
        "jurisdiction_preserved": before["authority"] == after["authority"],
        "epistemic_standing_preserved": all(
            before["nodes"][n].get("standing") == after["nodes"][n].get("standing")
            for n in set(before["nodes"]) & set(after["nodes"])
        ),
        "provenance_extended": (not hcet_result["accepted"]) or len(after["provenance"]) == len(before["provenance"]) + 1,
        "authorized_edit_only": hcet_result["accepted"] and not hcet_result.get("violations"),
        "target_morphology_reached": targets_ok if hcet_result["accepted"] else False,
    }
    checks["golden"] = all(checks.values())
    return checks

def initial_state():
    return canonical_state({
        "nodes": {
            "MAGUS": {"kind": "petition_orientation", "standing": "APPARATUS"},
            "SCIENCE": {"kind": "knowledge_domain", "standing": "RATIFIED_REFERENCE"},
            "LABS": {"kind": "knowledge_domain", "standing": "RATIFIED_REFERENCE"},
        },
        "edges": [["MAGUS", "orients_to", "SCIENCE"]],
        "authority": {
            "MAGUS": ["PETITION", "ORIENT"],
            "HCET": ["ADD_NODE", "ADD_EDGE"],
        },
        "provenance": [{"cycle_id": "GENESIS", "parent_digest": None, "edit_digest": None}],
    })

def run_once():
    state0 = initial_state()
    contracts = [
        Contract("C1_LOCALIZATION", [{"op": "add_edge", "src": "MAGUS", "rel": "localizes_to", "dst": "LABS"}], ["LABS"]),
        Contract("C2_PHENOTYPE_PROJECTION", [
            {"op": "add_node", "id": "PHENOTYPE_A", "attrs": {"kind": "uiux_projection", "standing": "DERIVED_DISPLAY"}},
            {"op": "add_edge", "src": "LABS", "rel": "projects", "dst": "PHENOTYPE_A"},
        ], ["PHENOTYPE_A"]),
        Contract("C3_UNAUTHORIZED_AUTHORITY", [{"op": "set_authority", "actor": "MAGUS", "value": ["PETITION","ORIENT","EXECUTE"]}], []),
    ]

    accepted_state = state0
    records = []
    for c in contracts:
        before = deepcopy(accepted_state)
        candidate, hcet = apply_hcet(before, c)
        metrics = measure(before, candidate)
        checks = conform(before, candidate, c, hcet)
        expected_reject = c.cycle_id == "C3_UNAUTHORIZED_AUTHORITY"
        if expected_reject:
            passed = (not hcet["accepted"] and stable_digest(candidate) == stable_digest(before))
            decision = "EXPECTED_REJECTION" if passed else "FAIL"
        else:
            passed = bool(checks["golden"])
            decision = "ACCEPT" if passed else "FAIL"
        if hcet["accepted"] and checks["golden"]:
            accepted_state = candidate
        records.append({
            "cycle_id": c.cycle_id,
            "input_digest": stable_digest(before),
            "candidate_digest": stable_digest(candidate),
            "hcet": hcet,
            "metrology": metrics,
            "conformance": checks,
            "decision": decision,
            "passed": passed,
        })
    return state0, canonical_state(accepted_state), records

def main():
    genesis, terminal1, records1 = run_once()
    _, terminal2, _ = run_once()
    replay_pass = stable_digest(terminal1) == stable_digest(terminal2)
    all_cycle_pass = all(r["passed"] for r in records1)
    golden = all_cycle_pass and replay_pass
    record = {
        "artifact_id": "GENERAL_BIOS_KMR_GOLDEN_CONFORMANCE_RECORD_v0.1",
        "apparatus_id": "GENERAL_BIOS_KINEMATIC_METROLOGICAL_RUNTIME_APPARATUS_v0.1",
        "standing": "BOUNDED_REFERENCE_CONFORMANCE_EVIDENCE",
        "genesis_digest": stable_digest(genesis),
        "terminal_digest": stable_digest(terminal1),
        "cycles": records1,
        "replay": {
            "terminal_digest_run_1": stable_digest(terminal1),
            "terminal_digest_run_2": stable_digest(terminal2),
            "deterministic_replay": replay_pass,
        },
        "golden_conformance_loop": "PASS" if golden else "FAIL",
        "claim_ceiling": "Synthetic deterministic reference regime only",
        "deltas": {"canon": 0, "physiology": 0, "level_0": 0, "pp": 0},
    }
    print(json.dumps(record, indent=2, sort_keys=True))
    raise SystemExit(0 if golden else 1)

if __name__ == "__main__":
    main()
