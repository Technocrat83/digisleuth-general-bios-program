from __future__ import annotations
from dataclasses import replace
from typing import Dict, Tuple
from .core import *
CHAMBERS=("T_0","T_OC","T_NC","T_U","T_G","T_C","T_X")

def graph():
    return TaskGraphContract("TG_FIXTURE","v1",frozenset({("c","CYCLE_COUNT","objective_step"),("m","PAGE_TOUCH","objective_step"),("n","MESSAGE_SEND","objective_step"),("q","ENQUEUE","objective_step")}),frozenset({"background_step","observer_false_claim"}))
def base_kwargs(node="objective_step",observer_claim="OBJECTIVE_CAUSAL",evidence=EvidenceState.OBSERVED):
    return dict(task_graph_id="TG_FIXTURE",task_graph_version="v1",task_node_id=node,causal_class_declared_by_observer=observer_claim,evidence_state=evidence,payload={})
def T_0():
    h=Harness(); h.begin_capture("T0"); ev=Observer(h).record(Resource.COMPUTE,action="CYCLE_COUNT",quantity=10,unit="hardware_cycles",handle="w0",**base_kwargs()); s=BindingAdjudicator(h,graph()).adjudicate_event(ev); return s==BindingStanding.VERIFIED and h.bind_ledger.events[-1].raw_event_id==ev.event_id
def T_OC():
    h=Harness(); h.begin_capture("TOC"); ev=Observer(h).record(Resource.COMPUTE,action="CYCLE_COUNT",quantity=10,unit="hardware_cycles",handle="w0",**base_kwargs(node="observer_false_claim",observer_claim="OBJECTIVE_CAUSAL")); return BindingAdjudicator(h,graph()).adjudicate_event(ev)==BindingStanding.NONCAUSAL
def T_NC():
    h=Harness(); h.begin_capture("TNC"); ev=Observer(h).record(Resource.NETWORK,action="KEEPALIVE",quantity=64,unit="bytes",handle="ch0",**base_kwargs(node="background_step",observer_claim="BACKGROUND")); s=BindingAdjudicator(h,graph()).adjudicate_event(ev); return len(h.raw_ledgers[Resource.NETWORK].events)==1 and s==BindingStanding.NONCAUSAL
def T_U():
    h=Harness(); h.begin_capture("TU"); ev=Observer(h).record(Resource.MEMORY,action="PAGE_TOUCH",quantity=4096,unit="bytes",handle="r0",**base_kwargs(node="unknown_step",evidence=EvidenceState.AMBIGUOUS)); return BindingAdjudicator(h,graph()).adjudicate_event(ev)==BindingStanding.UNRESOLVED
def T_G():
    h=Harness(); h.begin_capture("TG"); Observer(h).record(Resource.MEMORY,action="PAGE_TOUCH",quantity=4096,unit="bytes",handle="r0",**base_kwargs()); led=h.raw_ledgers[Resource.MEMORY]; led._dropped_event_count=1; led.seal(); c_m=CompletenessChecker().certificate(led); other=[]
    for r in (Resource.COMPUTE,Resource.NETWORK,Resource.QUEUE): h.raw_ledgers[r].seal(); other.append(CompletenessChecker().certificate(h.raw_ledgers[r])["standing"])
    return c_m["standing"]==CompletenessStanding.INCOMPLETE.value and all(x==CompletenessStanding.COMPLETE.value for x in other)
def T_C():
    h=Harness(); h.begin_capture("TC"); ev=Observer(h).record(Resource.COMPUTE,action="CYCLE_COUNT",quantity=10,unit="hardware_cycles",handle="w0",**base_kwargs()); led=h.raw_ledgers[Resource.COMPUTE]; led._events[0]=replace(ev,quantity=999); led.seal(); c=CompletenessChecker().certificate(led); return c["standing"]==CompletenessStanding.CONTRADICTED.value and not c["integrity_chain_valid"]
def T_X(): return all(PressureSemanticGuard().evaluate_request(x)==PressureSemanticStanding.ABSTAIN for x in ["usage/capacity","pressure","scarcity","saturation","distance_to_limit"])
def run_chambers()->Dict[str,bool]:
    f={"T_0":T_0,"T_OC":T_OC,"T_NC":T_NC,"T_U":T_U,"T_G":T_G,"T_C":T_C,"T_X":T_X}; return {k:bool(v()) for k,v in f.items()}
def _cross_write_check():
    h=Harness(); h.begin_capture("XWRITE")
    try: Observer(h).record(Resource.BIND,action="x",quantity=None,unit=None,handle="x",**base_kwargs()); return False
    except PermissionError: return not hasattr(h.raw_ledgers[Resource.COMPUTE],"append_reference") and not hasattr(h.bind_ledger,"append")
def _task_graph_version_check():
    h=Harness(); h.begin_capture("TGVER"); kw=base_kwargs(); kw["task_graph_version"]="WRONG"; ev=Observer(h).record(Resource.COMPUTE,action="CYCLE_COUNT",quantity=10,unit="hardware_cycles",handle="w0",**kw); return BindingAdjudicator(h,graph()).adjudicate_event(ev)==BindingStanding.UNRESOLVED
def _schema_check():
    h=Harness(); h.begin_capture("SCHEMA"); ev=Observer(h).record(Resource.COMPUTE,action="CYCLE_COUNT",quantity=10,unit="hardware_cycles",handle="w0",**base_kwargs()); BindingAdjudicator(h,graph()).adjudicate_event(ev); return raw_schema_exact(ev) and binding_schema_exact(h.bind_ledger.events[-1])
def _resource_locality_check():
    h=Harness(); h.begin_capture("LOCAL"); [l.seal() for l in h.raw_ledgers.values()]; c=CompletenessChecker().check_all(h); return all(c[r]["resource"]==r for r in ("c","m","n","q"))
def conformance_run()->Tuple[Harness,Dict[str,bool],Dict[str,bool],list[int],bool]:
    ch=run_chambers(); aux={"schema_exact":_schema_check(),"mutation_detected":ch["T_C"],"resource_locality":_resource_locality_check() and ch["T_G"],"binding_discrimination":all(ch[x] for x in ("T_0","T_OC","T_NC","T_U")),"raw_bind_cross_write_blocked":_cross_write_check(),"task_graph_version_enforced":_task_graph_version_check(),"pressure_semantic_abstention":ch["T_X"],"all_chambers_pass":all(ch.values()),"ground_truth_isolated":ConformanceOracle.ground_truth_isolated()}; vector=[int(aux[k]) for k in ("schema_exact","mutation_detected","resource_locality","binding_discrimination","raw_bind_cross_write_blocked","task_graph_version_enforced","pressure_semantic_abstention","all_chambers_pass","ground_truth_isolated")]
    h=Harness(); h.begin_capture("CONFORMANCE_SYNTHETIC"); o=Observer(h); b=BindingAdjudicator(h,graph())
    for r,a,q,u in ((Resource.COMPUTE,"CYCLE_COUNT",10,"hardware_cycles"),(Resource.MEMORY,"PAGE_TOUCH",4096,"bytes"),(Resource.NETWORK,"MESSAGE_SEND",128,"bytes"),(Resource.QUEUE,"ENQUEUE",1,"slots")): b.adjudicate_event(o.record(r,action=a,quantity=q,unit=u,handle=f"{r.value}0",**base_kwargs()))
    h.seal_all(); return h,ch,aux,vector,vector==[1]*9
