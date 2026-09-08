from localization_hook import *
from orientation_monitor import *

J="0x00000000000000000000000000000001"
POLICY=LocalizationPolicy(
    causal_members_by_surface={"PROVENANCE":["prov:root"],"PLACEMENT":["graph:vertex"],"GRAPH_TOPOLOGY":["graph:adj"],"JURISDICTION":["jur:binding"],"STATE_VECTOR":["state:nav"],"EPOCH":["epoch:clock"],"AUTHORITY_USE":["auth:attempt"],"BOUNDARY":["boundary:surface"],"ADJACENCY_STRUCTURE":["graph:adjacency"]},
    jurisdiction_members_by_surface={"JURISDICTION":[J],"GRAPH_TOPOLOGY":[J],"AUTHORITY_USE":[J],"ADJACENCY_STRUCTURE":[J],"BOUNDARY":[J]},
    unresolved_dependency_by_surface={"PROVENANCE":["dep:provenance"],"GRAPH_TOPOLOGY":["dep:graph"],"JURISDICTION":["dep:jurisdiction"]})
BASE=dict(object_id="O1",delta_id="D0",prior_orientation_hash="o0",prior_graph_hash="g0",current_graph_hash="g0",prior_jurisdiction_hash="j0",current_jurisdiction_hash="j0",prior_provenance_hash="p0",current_provenance_hash="p0",prior_placement_hash="v0",current_placement_hash="v0",prior_state_hash="s0",current_state_hash="s0",prior_boundary_hash="b0",current_boundary_hash="b0",adjacency_changed=False,prior_epoch="E1",current_epoch="E1",authority_use_attempted=False,evidence_complete=True)

def mk(**kw):
 d=BASE.copy(); d.update(kw); return FieldDelta(**d)

def assert_case(name, delta, standing, lifecycle):
 loc=localize(delta,POLICY); assert loc.standing==standing,(name,loc)
 ev=evaluate(PriorOrientation("OR1","O1","od",True,"SUPPORTED"),loc); assert ev.lifecycle==lifecycle,(name,ev)
 if ev.witness:
  assert ev.witness.historical_orientation_preserved and not ev.witness.repair_attempted and not ev.witness.auto_reorientation and not ev.witness.epistemic_standing_changed
 print("PASS",name,standing.value,lifecycle.value)

assert_case("NO_CHANGE",mk(),LocalizationStanding.NO_MATERIAL_INTERSECTION,OrientationLifecycle.CURRENT)
assert_case("PROVENANCE_CHANGE",mk(current_provenance_hash="p1"),LocalizationStanding.LOCALIZED,OrientationLifecycle.WITHDRAWN)
assert_case("UNRESOLVED_GRAPH",mk(current_graph_hash="g1",evidence_complete=False),LocalizationStanding.UNRESOLVED,OrientationLifecycle.SUSPENDED)
assert_case("STATE_VECTOR_ONLY",mk(current_state_hash="s1"),LocalizationStanding.LOCALIZED,OrientationLifecycle.WITHDRAWN)
assert_case("AUTHORITY_MISUSE",mk(authority_use_attempted=True),LocalizationStanding.LOCALIZED,OrientationLifecycle.SUSPENDED)
try:
 bad=LocalizationPolicy(POLICY.causal_members_by_surface,{"JURISDICTION":["0x0001000200030004"]},POLICY.unresolved_dependency_by_surface)
 localize(mk(current_jurisdiction_hash="j1"),bad); raise AssertionError("WIDTH CHECK FAILED")
except ValueError:
 print("PASS JURISDICTION_128BIT_WIDTH_ENFORCED")
