import argparse,json
from pathlib import Path
from .fixtures import conformance_run
from .core import CompletenessChecker

def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["conform"]); p.add_argument("--out",default="artifacts"); a=p.parse_args(); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    h,ch,aux,v,eligible=conformance_run(); report={"harness_id":"URPH_P1_RF_CLASS2_INSTRUMENT_HARNESS_v0.1","contract_id":"URPH_P1_RF_CLASS2_WITNESS_MATERIALIZATION_CONTRACT_v0.1","standing":["PRE_BASELINE","PRE_APPLICABILITY","PRE_INTERVENTION"],"chambers":ch,"PASS_I":all(ch.values()),"auxiliary_conformance_checks":aux,"machine_conformance_vector":v,"vector_compact":"".join(map(str,v)),"baseline_materialization_eligible":eligible,"baseline_evidence_generated":False,"applicability_claim_generated":False,"pressure_evidence_generated":False,"raw_completeness_certificates":CompletenessChecker().check_all(h)}
    (out/"conformance_report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    for r,l in h.raw_ledgers.items(): (out/f"L_raw_{r.value}.ndjson").write_text(l.export_ndjson())
    (out/"L_bind.ndjson").write_text(h.bind_ledger.export_ndjson()); print(json.dumps(report,indent=2,sort_keys=True)); return 0 if eligible else 2
if __name__=="__main__": raise SystemExit(main())
