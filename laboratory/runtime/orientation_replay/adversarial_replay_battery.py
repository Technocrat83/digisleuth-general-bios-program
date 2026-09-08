from copy import deepcopy
import pathlib, sys, json, hashlib

HERE = pathlib.Path(__file__).resolve().parent
LIFECYCLE_DIR = HERE.parent / "orientation_lifecycle"
for p in (HERE, LIFECYCLE_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from canonical_encoding import evidence_digest
from replay_validator import replay_validate, ReplayAxis
from localization_hook import FieldDelta, LocalizationPolicy, localize
from orientation_monitor import PriorOrientation, evaluate

J="0x00000000000000000000000000000001"
POLICY=LocalizationPolicy(
    causal_members_by_surface={"PROVENANCE":["prov:root"],"PLACEMENT":["graph:vertex"],"GRAPH_TOPOLOGY":["graph:adj"],"JURISDICTION":["jur:binding"],"STATE_VECTOR":["state:nav"],"EPOCH":["epoch:clock"],"AUTHORITY_USE":["auth:attempt"],"BOUNDARY":["boundary:surface"],"ADJACENCY_STRUCTURE":["graph:adjacency"]},
    jurisdiction_members_by_surface={"JURISDICTION":[J],"GRAPH_TOPOLOGY":[J],"AUTHORITY_USE":[J],"ADJACENCY_STRUCTURE":[J],"BOUNDARY":[J]},
    unresolved_dependency_by_surface={"PROVENANCE":["dep:provenance"],"GRAPH_TOPOLOGY":["dep:graph"],"JURISDICTION":["dep:jurisdiction"],"ADJACENCY_STRUCTURE":["dep:adjacency"]},
)
PRIOR=PriorOrientation("ORIENT_001","OAB_OBJECT_001","ORIENT_HASH_001",True,"SUPPORTED")
BASE_DELTA={
    "object_id":"OAB_OBJECT_001","delta_id":"REPLAY_BASE","prior_orientation_hash":"ORIENT_HASH_001",
    "prior_graph_hash":"GRAPH_A","current_graph_hash":"GRAPH_A",
    "prior_jurisdiction_hash":"JUR_A","current_jurisdiction_hash":"JUR_A",
    "prior_provenance_hash":"PROV_A","current_provenance_hash":"PROV_B",
    "prior_placement_hash":"PLACE_A","current_placement_hash":"PLACE_A",
    "prior_state_hash":"STATE_A","current_state_hash":"STATE_A",
    "prior_boundary_hash":"BOUND_A","current_boundary_hash":"BOUND_A",
    "prior_epoch":"EPOCH_001","current_epoch":"EPOCH_001",
    "adjacency_changed":False,"authority_use_attempted":False,"evidence_complete":True,
}

def witness_for(delta_dict):
    d=FieldDelta(**delta_dict); loc=localize(d,POLICY); ev=evaluate(PRIOR,loc)
    return {
        "object_id":d.object_id,"delta_id":d.delta_id,
        "prior_orientation_id":PRIOR.orientation_id,"prior_orientation_digest":PRIOR.orientation_digest,
        "evidence_digest":evidence_digest(d),
        "localization":{
            "standing":loc.standing.value,
            "affected_surfaces":sorted(loc.affected_surfaces),
            "causal_cone":sorted(loc.causal_cone),
            "jurisdictional_cone":sorted(loc.jurisdictional_cone),
        },
        "lifecycle":ev.lifecycle.value,
    }

def expect(name, result, axes):
    got=(result.input_binding,result.digest_binding,result.localization_reconstruction,result.disposition_reconstruction)
    assert got==axes,(name,result.to_dict())
    assert result.repair_attempted is False
    print("PASS",name,result.to_dict())

if __name__=="__main__":
    w=witness_for(BASE_DELTA)
    expect("VALID_CONTROL", replay_validate(BASE_DELTA,PRIOR,w,POLICY), (ReplayAxis.PASS,)*4)

    x=deepcopy(w); x["lifecycle"]="CURRENT"
    expect("CORRECT_DIGEST_WRONG_DISPOSITION", replay_validate(BASE_DELTA,PRIOR,x,POLICY), (ReplayAxis.PASS,ReplayAxis.PASS,ReplayAxis.PASS,ReplayAxis.FAIL))

    x=deepcopy(w); x["localization"]["causal_cone"]=["wrong:cone"]
    expect("CORRECT_DISPOSITION_ALTERED_CONE", replay_validate(BASE_DELTA,PRIOR,x,POLICY), (ReplayAxis.PASS,ReplayAxis.PASS,ReplayAxis.FAIL,ReplayAxis.PASS))

    x=deepcopy(w); x["evidence_digest"]=hashlib.sha256(json.dumps(BASE_DELTA,indent=2).encode()).hexdigest()
    expect("NONCANONICAL_BYTES_REJECTED", replay_validate(BASE_DELTA,PRIOR,x,POLICY), (ReplayAxis.PASS,ReplayAxis.FAIL,ReplayAxis.PASS,ReplayAxis.PASS))

    x=deepcopy(w); x["prior_orientation_digest"]="STALE_ORIENTATION"
    expect("STALE_PRIOR_WITNESS_BINDING", replay_validate(BASE_DELTA,PRIOR,x,POLICY), (ReplayAxis.FAIL,ReplayAxis.PASS,ReplayAxis.PASS,ReplayAxis.PASS))

    unresolved=deepcopy(BASE_DELTA); unresolved["delta_id"]="UNRES"; unresolved["current_graph_hash"]="GRAPH_B"; unresolved["evidence_complete"]=False
    uw=witness_for(unresolved); assert uw["lifecycle"]=="SUSPENDED"; uw["lifecycle"]="WITHDRAWN"
    expect("UNRESOLVED_COERCED_TO_WITHDRAWN", replay_validate(unresolved,PRIOR,uw,POLICY), (ReplayAxis.PASS,ReplayAxis.PASS,ReplayAxis.PASS,ReplayAxis.FAIL))

    x=deepcopy(w); x.pop("prior_orientation_id")
    expect("MISSING_INPUT_BINDING_UNRESOLVED", replay_validate(BASE_DELTA,PRIOR,x,POLICY), (ReplayAxis.UNRESOLVED,ReplayAxis.PASS,ReplayAxis.PASS,ReplayAxis.PASS))
