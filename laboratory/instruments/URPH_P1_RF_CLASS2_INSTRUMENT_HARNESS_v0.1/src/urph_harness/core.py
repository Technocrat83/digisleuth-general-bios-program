from __future__ import annotations

from dataclasses import dataclass, asdict, fields
from enum import Enum
from hashlib import sha256
import inspect
import json
import time
import uuid
from typing import Any, Dict, List, Mapping, Optional

HARNESS_ID = "URPH_P1_RF_CLASS2_INSTRUMENT_HARNESS_v0.1"
CONTRACT_ID = "URPH_P1_RF_CLASS2_WITNESS_MATERIALIZATION_CONTRACT_v0.1"
APPLICABILITY_ID = "URPH_P1_RF_CAUSAL_APPLICABILITY_CRITERIA_v0.1"

class Resource(str, Enum):
    COMPUTE="c"; MEMORY="m"; NETWORK="n"; QUEUE="q"; BIND="bind"
class EvidenceState(str, Enum):
    OBSERVED="OBSERVED"; DERIVED_LOSSLESS="DERIVED_LOSSLESS"; MISSING="MISSING"; AMBIGUOUS="AMBIGUOUS"; INSTRUMENT_ERROR="INSTRUMENT_ERROR"
class BindingStanding(str, Enum):
    VERIFIED="VERIFIED"; NONCAUSAL="NONCAUSAL"; UNRESOLVED="UNRESOLVED"
class CompletenessStanding(str, Enum):
    COMPLETE="COMPLETE"; INCOMPLETE="INCOMPLETE"; CONTRADICTED="CONTRADICTED"
class PressureSemanticStanding(str, Enum):
    ABSTAIN="PRESSURE_SEMANTIC_ABSTENTION"

def canonical_json(obj: Any)->str:
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def digest(obj: Any)->str:
    return sha256(canonical_json(obj).encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class RawEvent:
    event_id:str; epoch_id:str; seq:int; timestamp_ns:int; resource:str
    observer_id:str; observer_version:str; action:str; quantity:Optional[int|float]; unit:Optional[str]; handle:str
    task_graph_id:str; task_graph_version:str; task_node_id:str; causal_class_declared_by_observer:str
    evidence_state:str; payload:Dict[str,Any]; prev_hash:str; event_hash:str

@dataclass(frozen=True)
class BindingRecord:
    binding_id:str; epoch_id:str; seq:int; timestamp_ns:int; resource:str; raw_event_id:str; raw_event_digest:str
    task_graph_id:str; task_graph_version:str; task_node_id:str; binding_basis:str; adjudicator_id:str; adjudicator_version:str
    standing:str; prev_hash:str; event_hash:str

@dataclass(frozen=True)
class TaskGraphContract:
    graph_id:str; version:str; required_signatures:frozenset[tuple[str,str,str]]; known_noncausal_nodes:frozenset[str]=frozenset()
    def classify(self,event:RawEvent)->BindingStanding:
        if event.task_graph_id!=self.graph_id or event.task_graph_version!=self.version: return BindingStanding.UNRESOLVED
        if (event.resource,event.action,event.task_node_id) in self.required_signatures: return BindingStanding.VERIFIED
        if event.task_node_id in self.known_noncausal_nodes: return BindingStanding.NONCAUSAL
        return BindingStanding.UNRESOLVED

class AppendOnlyRawLedger:
    def __init__(self,resource:Resource):
        if resource==Resource.BIND: raise ValueError("raw ledger cannot be binding resource")
        self.resource=resource; self._events:List[RawEvent]=[]; self._sealed=False; self._epoch_id:Optional[str]=None; self._dropped_event_count=0
    @property
    def events(self): return tuple(self._events)
    def begin_epoch(self,epoch_id:str):
        if self._epoch_id is not None: raise RuntimeError("epoch already active")
        self._epoch_id=epoch_id
    def append(self,*,observer_id:str,observer_version:str,action:str,quantity:Optional[int|float],unit:Optional[str],handle:str,task_graph_id:str,task_graph_version:str,task_node_id:str,causal_class_declared_by_observer:str,evidence_state:EvidenceState,payload:Optional[Dict[str,Any]]=None,timestamp_ns:Optional[int]=None)->RawEvent:
        if self._sealed: raise RuntimeError("ledger sealed")
        if self._epoch_id is None: raise RuntimeError("capture epoch not started")
        seq=len(self._events); prev=self._events[-1].event_hash if self._events else "0"*64
        body={"event_id":str(uuid.uuid4()),"epoch_id":self._epoch_id,"seq":seq,"timestamp_ns":timestamp_ns or time.monotonic_ns(),"resource":self.resource.value,"observer_id":observer_id,"observer_version":observer_version,"action":action,"quantity":quantity,"unit":unit,"handle":handle,"task_graph_id":task_graph_id,"task_graph_version":task_graph_version,"task_node_id":task_node_id,"causal_class_declared_by_observer":causal_class_declared_by_observer,"evidence_state":evidence_state.value,"payload":payload or {},"prev_hash":prev}
        event=RawEvent(**body,event_hash=digest(body)); self._events.append(event); return event
    def seal(self): self._sealed=True
    def verify_chain(self):
        prev="0"*64
        for ev in self._events:
            if ev.prev_hash!=prev: return False
            body=asdict(ev); eh=body.pop("event_hash")
            if digest(body)!=eh: return False
            prev=ev.event_hash
        return True
    def export_ndjson(self): return "\n".join(canonical_json(asdict(e)) for e in self._events)+("\n" if self._events else "")

class AppendOnlyBindingLedger:
    def __init__(self): self.resource=Resource.BIND; self._events:List[BindingRecord]=[]; self._sealed=False; self._epoch_id:Optional[str]=None
    @property
    def events(self): return tuple(self._events)
    def begin_epoch(self,epoch_id:str):
        if self._epoch_id is not None: raise RuntimeError("epoch already active")
        self._epoch_id=epoch_id
    def append_reference(self,raw:RawEvent,standing:BindingStanding,basis:str,adjudicator_id:str,adjudicator_version:str)->BindingRecord:
        if self._sealed: raise RuntimeError("binding ledger sealed")
        if self._epoch_id is None: raise RuntimeError("capture epoch not started")
        seq=len(self._events); prev=self._events[-1].event_hash if self._events else "0"*64
        body={"binding_id":str(uuid.uuid4()),"epoch_id":self._epoch_id,"seq":seq,"timestamp_ns":time.monotonic_ns(),"resource":"bind","raw_event_id":raw.event_id,"raw_event_digest":raw.event_hash,"task_graph_id":raw.task_graph_id,"task_graph_version":raw.task_graph_version,"task_node_id":raw.task_node_id,"binding_basis":basis,"adjudicator_id":adjudicator_id,"adjudicator_version":adjudicator_version,"standing":standing.value,"prev_hash":prev}
        rec=BindingRecord(**body,event_hash=digest(body)); self._events.append(rec); return rec
    def seal(self): self._sealed=True
    def verify_chain(self):
        prev="0"*64
        for ev in self._events:
            if ev.prev_hash!=prev: return False
            body=asdict(ev); eh=body.pop("event_hash")
            if digest(body)!=eh: return False
            prev=ev.event_hash
        return True
    def export_ndjson(self): return "\n".join(canonical_json(asdict(e)) for e in self._events)+("\n" if self._events else "")

class Harness:
    def __init__(self):
        self.raw_ledgers={r:AppendOnlyRawLedger(r) for r in (Resource.COMPUTE,Resource.MEMORY,Resource.NETWORK,Resource.QUEUE)}; self.bind_ledger=AppendOnlyBindingLedger()
    def begin_capture(self,epoch_id:Optional[str]=None):
        eid=epoch_id or str(uuid.uuid4())
        for l in self.raw_ledgers.values(): l.begin_epoch(eid)
        self.bind_ledger.begin_epoch(eid); return eid
    def seal_all(self):
        for l in self.raw_ledgers.values(): l.seal()
        self.bind_ledger.seal()

class Observer:
    def __init__(self,harness:Harness,observer_id:str="observer",version:str="0.1"): self.harness=harness; self.observer_id=observer_id; self.version=version
    def record(self,resource:Resource,**kwargs:Any)->RawEvent:
        if resource==Resource.BIND: raise PermissionError("observer cannot write L_bind")
        return self.harness.raw_ledgers[resource].append(observer_id=self.observer_id,observer_version=self.version,**kwargs)

class CompletenessChecker:
    def certificate(self,ledger:AppendOnlyRawLedger):
        events=ledger.events; seq=[e.seq for e in events]; seq_contiguous=(seq==list(range(len(seq)))) and ledger._dropped_event_count==0
        resource_local=all(e.resource==ledger.resource.value for e in events); times=[e.timestamp_ns for e in events]; monotonic=times==sorted(times); epoch_consistent=len({e.epoch_id for e in events})<=1; chain_valid=ledger.verify_chain()
        if not chain_valid or not resource_local or not monotonic or not epoch_consistent: standing=CompletenessStanding.CONTRADICTED
        elif not ledger._sealed or not seq_contiguous: standing=CompletenessStanding.INCOMPLETE
        else: standing=CompletenessStanding.COMPLETE
        cert={"resource":ledger.resource.value,"event_count":len(events),"sequence_gap_count":ledger._dropped_event_count,"seq_contiguous":seq_contiguous,"resource_local":resource_local,"monotonic_time":monotonic,"epoch_consistent":epoch_consistent,"integrity_chain_valid":chain_valid,"standing":standing.value}; cert["integrity_digest"]=digest(cert); return cert
    def check_all(self,h:Harness): return {r.value:self.certificate(l) for r,l in h.raw_ledgers.items()}

class BindingAdjudicator:
    def __init__(self,harness:Harness,task_graph:TaskGraphContract,adjudicator_id:str="binding_adjudicator",version:str="0.1"): self.harness=harness; self.task_graph=task_graph; self.adjudicator_id=adjudicator_id; self.version=version
    def adjudicate_event(self,event:RawEvent)->BindingStanding:
        if event.evidence_state in {EvidenceState.MISSING.value,EvidenceState.AMBIGUOUS.value,EvidenceState.INSTRUMENT_ERROR.value}: standing=BindingStanding.UNRESOLVED; basis="EVIDENCE_STATE_UNRESOLVED"
        else: standing=self.task_graph.classify(event); basis="FROZEN_TASK_GRAPH_RELATION"
        self.harness.bind_ledger.append_reference(event,standing,basis,self.adjudicator_id,self.version); return standing

class PressureSemanticGuard:
    def evaluate_request(self,requested_semantic:str)->PressureSemanticStanding: return PressureSemanticStanding.ABSTAIN

class ConformanceOracle:
    def evaluate(self,emitted:Mapping[str,str],truth:Mapping[str,str])->bool: return dict(emitted)==dict(truth)
    @staticmethod
    def ground_truth_isolated()->bool:
        params=set(inspect.signature(BindingAdjudicator.__init__).parameters); return not bool(params & {"truth","fixture_truth","ground_truth","answer_key"})

def raw_schema_exact(event:RawEvent)->bool: return set(asdict(event))=={f.name for f in fields(RawEvent)}
def binding_schema_exact(event:BindingRecord)->bool: return set(asdict(event))=={f.name for f in fields(BindingRecord)}
