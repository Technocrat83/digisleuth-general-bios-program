"""Materialize a new repair evidence archive without changing either parent's receipts."""
import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest=read(ROOT/'manifest.json')
    summary=read(ROOT/'results/observer_summary.json')
    regression=read(ROOT/'results/repair_regressions.json')
    if regression['failed']:raise SystemExit('Regressions failed; preserve results and repair in a new revision.')
    for path,h in manifest['files'].items():
        if sha(ROOT/path)!=h:raise RuntimeError('Frozen file changed: '+path)
    prior=read(ROOT/'history/prior_execution.json')
    if sha(ROOT/prior['previous_archive'])!=prior['previous_archive_sha256']:
        raise RuntimeError('Historical archive changed')
    positive=read(ROOT/'results/sandbox/PHC-01/positive/attempts/1/package.json')
    (ROOT/'results/positive_control_draft.md').write_text(positive['components']['draft_asset']['data']['text'])
    cases=[read(p) for p in sorted((ROOT/'results/case_receipts').glob('PHC-*.json'))]
    case_rows='\n'.join(f"| {r['case_id']} | {r['completeness']['status']} | {r['acceptance_applied']} | {r['verdict']} |" for r in cases)
    primary=[p for p in regression['probes'] if p['kind']=='PRIMARY_PHC_10_OMISSION']
    omissions=[p for p in regression['probes'] if p['kind'] in ('PRIMARY_PHC_10_OMISSION','MULTI_SCENARIO_OMISSION_SWEEP')]
    total_attempts=prior['total_prior_runtime_attempts']+summary['workflow_attempts']
    source=(ROOT/'src/phc_runtime.py').read_bytes()
    with zipfile.ZipFile(ROOT/prior['previous_archive']) as z:
        old_runtime=z.read('PHC_PROTOTYPE_EVIDENCE_v0.1.1_candidate/src/phc_runtime.py')
    if source!=old_runtime:raise RuntimeError('Runtime changed outside observer repair scope')
    text=f'''---
artifact_id: PHC_OBSERVER_COMPLETENESS_REPAIR
version: '0.1.2'
date: '{datetime.now(ZoneInfo("America/New_York")).date()}'
standing: EXECUTED_LOCAL_REPAIR_CANDIDATE_UNPROMOTED
defect_id: PHC-10-OBSERVER-01
parent_commit: f36edde767d445524ce4d3ea8e49679b12d7095b
independent_review: OUTSTANDING
source_admission: HELD
publication_authority: WITHHELD
pp_gate: BLOCKED
git_binding: UNBOUND
---

# Publication observer completeness repair

This is a new candidate revision implementing the supplied locked repair specification. The earlier v0.1.1 archive and all its historical receipts are preserved byte-for-byte. The task runtime is unchanged; the observer, frozen acceptance plan, case receipt schema, revision bindings, regression suite, and packaging were revised.

## Locked decision order

1. Bind mandatory scenario IDs to the frozen acceptance plan.
2. Validate the entire result index for duplicate or unexpected scenario IDs before applying any acceptance predicate. Either condition raises a schema violation and aborts aggregation globally, including when one duplicate is unusable.
3. Require exactly one usable, revision-bound result for every mandatory scenario. Missing or unusable mandatory evidence yields UNRESOLVED, with the missing IDs or reasons recorded and acceptance_applied false.
4. Apply the existing case acceptance predicate only after mandatory evidence closure. Complete evidence can still yield CONTRADICTED; completeness does not confer support.

Unassignable or unusable records create an explicit unresolved evidence condition. An index with an unexpected case ID also aborts aggregation. The observer's executable main path records a schema-abort artifact and exits without producing acceptance receipts when aggregation is aborted.

## Frozen mandatory sets

The plan declares 17 mandatory scenario IDs across the publication contract's 12 cases. Its multi-scenario cases are PHC-02 (missing source and missing permission), PHC-10 (revoked, stopped, budget), and PHC-11 (crash after capture, draft, or receipt). These identities are not derived from whatever results happen to arrive.

The publication harness still uses its own six delivery records and PHC-01–PHC-12 namespace. No transformation-experiment equivalence is introduced.

## Observed results

- New candidate workflow execution: {summary['scenario_count']} scenarios and {summary['workflow_attempts']} runtime attempts.
- New candidate case verdicts: `{json.dumps(summary['verdict_counts'],sort_keys=True)}`.
- Producer-side oracle regressions: {regression['passed']}/{regression['probe_count']} passed; {regression['failed']} failed.
- Primary PHC-10 omission probes: {sum(p['passed'] for p in primary)}/{len(primary)} passed, each yielding UNRESOLVED with no PHC-10 acceptance call.
- Omission sweep across every multi-scenario case: {sum(p['passed'] for p in omissions)}/{len(omissions)} passed.
- Additional probes cover unusable evidence, duplicate and unexpected IDs, invalid mandatory plans, missing files or traces, wrong revision bindings, unavailable observations, and complete evidence that fails an acceptance predicate.

The regression suite instruments the actual acceptance function. Omission and unusable-evidence probes require zero calls for the affected case; schema-abort probes require zero calls across the entire aggregation. A complete-evidence negative control requires the acceptance function to run and return CONTRADICTED. Probes use copies of result indexes or derivative temporary files. The original observed results and historical receipts remain unchanged.

| Case | Evidence closure | Acceptance applied | Producer verdict |
|---|---|---|---|
{case_rows}

The recorded history contains {total_attempts} workflow attempts: 17 in the preserved original failed run, 20 in v0.1.1, and {summary['workflow_attempts']} in this revision. Oracle regression assessments reuse this revision's records; they add no workflow attempts.

## Exact bindings

| Referent | SHA-256 |
|---|---|
| Publication contract | `{manifest['contract_sha256']}` |
| Repaired implementation path-to-digest map | `{manifest['implementation_sha256']}` |
| Frozen acceptance plan | `{manifest['acceptance_plan_sha256']}` |
| New manifest bytes | `{summary['bindings']['manifest_sha256']}` |
| Preserved v0.1.1 archive | `{prior['previous_archive_sha256']}` |

Each runtime package, case receipt, and repair regression result binds to the repaired implementation and acceptance plan. Both schema digests are recorded in manifest.json and the result bindings. Whole-package witness digests and the final evidence index remain separate to avoid self-reference.

## Review files

- [Frozen repair scope](fixtures/repair_scope.json)
- [Mandatory acceptance plan](fixtures/plan.json)
- [Completeness guard](src/scenario_completeness.py)
- [Observer](src/phc_observer.py)
- [Regression implementation](src/test_scenario_completeness.py)
- [Regression receipts](results/repair_regressions.json)
- [Case receipts](results/case_receipts/)
- [Observer summary](results/observer_summary.json)
- [Preserved history record](history/prior_execution.json)
- [Positive-control draft](results/positive_control_draft.md)

## Scope and standing

These are producer-side local mock results from the same assistant that implemented and audited the earlier specimen. Independent review remains outstanding. No certification, knowledge admission, publication authority, production enforcement, or market demand is established. PP remains BLOCKED.

The observer and runtime still share an OS user. Curated quote matching and template drafting do not establish general factual verification or model reasoning quality. No live publisher, authenticated service, model API, or concurrent interprocess authority race was tested. The positive-control criterion remains a structural and traceability proxy; human usefulness remains unassessed.

External service calls and costs were zero. Observer suite wall time was {summary['cost']['suite_wall_seconds']:.6f} seconds. Host, assistant, preparation, and human review costs remain UNKNOWN_NOT_MEASURED. Timings are not a business productivity estimate.

## Replay

Keep this evidence package intact. For a fresh run, copy src/, contract/, and history/ into an empty directory. Run `python3 src/prepare_run.py`, `python3 src/phc_observer.py`, `python3 src/test_scenario_completeness.py`, and `python3 src/build_report.py`. A replay has new timing and manifest identities and is a separate execution. Python standard library only; the included schema validator supports only its declared keyword subset.
'''
    (ROOT/'README.md').write_text(text)
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='evidence_file_index.json')
    index={'index_rule':'ALL_INCLUDED_FILES_EXCEPT_THIS_INDEX','files':{str(p.relative_to(ROOT)):sha(p) for p in files},
           'standing':'BYTE_INTEGRITY_ONLY_NO_INDEPENDENT_ADJUDICATION'}
    (ROOT/'results/evidence_file_index.json').write_text(json.dumps(index,sort_keys=True,indent=2)+'\n')
    archive=ROOT.parent/(ROOT.name+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:z.write(p,str(Path(ROOT.name)/p.relative_to(ROOT)))
    print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),
                      'files_indexed':len(index['files']),'primary_omission_probes_passed':sum(p['passed'] for p in primary),
                      'omission_sweep_passed':sum(p['passed'] for p in omissions)}))

if __name__=='__main__':main()

