import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "runtime" / "orientation_lifecycle"))
from localization_hook import *
from orientation_monitor import *

J="0x00000000000000000000000000000001"
POLICY=LocalizationPolicy(causal_members_by_surface={"PROVENANCE":["prov:root"],"PLACEMENT":["graph:vertex"],"GRAPH_TOPOLOGY":["graph:adj"],"JURISDICTION":["jur:binding"],"STATE_VECTOR":["state:nav"],"EPOCH":["epoch:clock"],"AUTHORITY_USE":["auth:attempt"],"BOUNDARY":["boundary:surface"],"ADJACENCY_STRUCTURE":["graph:adjacency"]},jurisdiction_members_by_surface={"JURISDICTION":[J],"GRAPH_TOPOLOGY":[J],"AUTHORITY_USE":[J],"ADJACENCY_STRUCTURE":[J],"BOUNDARY":[J]},unresolved_dependency_by_surface={"PROVENANCE":["dep:provenance"],"GRAPH_TOPOLOGY":["dep:graph"],"JURISDICTION":["dep:jurisdiction"],"ADJACENCY_STRUCTURE":["dep:adjacency"]})
PRIOR=PriorOrientation("ORIENT_001","OAB_OBJECT_001","ORIENT_HASH_001",True,"SUPPORTED")

def run_one(path):
 f=json.loads(path.read_text()); loc=localize(FieldDelta(**f["field_delta"]),POLICY); exp=f["expected_localization"]
 assert loc.standing.value==exp["standing"]
 assert sorted(loc.affected_surfaces)==sorted(exp["affected_surfaces"])
 assert sorted(loc.causal_cone)==sorted(exp["causal_cone"])
 assert sorted(loc.jurisdictional_cone)==sorted(exp["jurisdictional_cone"])
 ev=evaluate(PRIOR,loc); em=f["expected_monitor"]; assert ev.lifecycle.value==em["lifecycle"]
 if ev.lifecycle.value=="CURRENT": assert ev.witness is None
 else:
  w=ev.witness; assert w is not None; assert w.historical_orientation_preserved==em["historical_orientation_preserved"]; assert w.epistemic_standing_changed==em["epistemic_standing_changed"]; assert w.repair_attempted==em["repair_attempted"]; assert w.auto_reorientation==em["auto_reorientation"]; assert w.authority_effect==em["authority_effect"]; assert w.execution_effect==em["execution_effect"]
 print("PASS",f["fixture_id"],loc.standing.value,ev.lifecycle.value)

if __name__=="__main__":
 here=pathlib.Path(__file__).parent
 for p in sorted(here.glob("OAB[1-8].json")): run_one(p)
