"""Package the observed results without modifying the frozen contract or implementation."""
import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]

def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    summary=read(ROOT/'results'/'observer_summary.json')
    manifest=read(ROOT/'manifest.json')
    criterion=read(ROOT/'fixtures'/'useful_draft_criterion.json')
    receipts=[read(p) for p in sorted((ROOT/'results'/'case_receipts').glob('PHC-*.json'))]
    rows='\n'.join(f"| {r['case_id']} | {r['execution_status']} | {r['verdict']} | {len(r['checks'])} |" for r in receipts)
    schema_rows='\n'.join(f'| `{p}` | `{h}` |' for p,h in manifest['schema_sha256'].items())
    outcomes={}
    for entry in read(ROOT/'results'/'driver_index.json'):
        if entry.get('package_path'):
            value=read(ROOT/entry['package_path'])['components']['disposition']['data']['run_outcome']
            outcomes[value]=outcomes.get(value,0)+1
    best=ROOT/'results'/'sandbox'/'PHC-01'/'positive'/'attempts'/'1'/'package.json'
    draft=read(best)['components']['draft_asset']['data']['text']
    (ROOT/'results'/'positive_control_draft.md').write_text(draft)
    text=f'''---
artifact_id: PHC_PROTOTYPE_EVIDENCE
version: '0.1.1'
date: '{datetime.now(ZoneInfo("America/New_York")).date()}'
standing: EXECUTED_LOCAL_MOCK_CANDIDATE_UNPROMOTED
contract_snapshot: BIOS_PUBLICATION_HARNESS_CONTRACT_v0.1_candidate
source_admission: HELD
certification: NOT_ISSUED
production_enforcement: NOT_ESTABLISHED
market_demand: NOT_ESTABLISHED
git_binding: UNBOUND
---

# Publication harness prototype evidence

Observed **{summary['acceptance_cases_executed']} publication-contract acceptance cases**, using {summary['scenario_count']} fixture scenarios and {summary['workflow_attempts']} runtime attempts in one suite execution. Verdict counts: `{json.dumps(summary['verdict_counts'],sort_keys=True)}`. These are local deterministic specimen findings; certification and production authority are not granted.

The PHC-01 through PHC-12 definitions were extracted from the saved publication harness contract. Its six records are source record, claim-and-evidence map, draft asset, authority record, execution receipt, and disposition. **No equivalence to transformation-experiment envelopes or fixtures is asserted.**

## Start here

- [Positive-control draft](results/positive_control_draft.md)
- [Positive-control six-record package](results/sandbox/PHC-01/positive/attempts/1/package.json)
- [Observer summary](results/observer_summary.json)
- [Acceptance-case receipts](results/case_receipts/)
- [Pre-execution manifest](manifest.json)
- [Contract snapshot](contract/BIOS_PUBLICATION_HARNESS_CONTRACT_v0.1_candidate.md)
- [Frozen source and permission record](inputs/source_record.json)
- [Predefined useful-draft criterion](fixtures/useful_draft_criterion.json)

## Exact bindings

| Artifact | SHA-256 |
|---|---|
| Contract bytes | `{manifest['contract_sha256']}` |
| Implementation path-to-digest map | `{manifest['implementation_sha256']}` |
| Pre-execution manifest bytes | `{summary['bindings']['manifest_sha256']}` |
{schema_rows}

The implementation digest hashes a sorted compact JSON map of source paths to their individual SHA-256 values; those files are listed in the manifest. Package component hashes exclude the execution receipt itself. Each complete package has a separate witness for its entire byte stream. The final evidence index also excludes itself to avoid self-reference.

## Source and useful-draft criterion

The source is a prospective UTF-8 serialization of the user's submitted prototype requirements, with a final newline. It is used under the current task's local preparation scope. Attribution is user-submitted, not independently authenticated; admission remains HELD. Some cases append explicitly synthetic perturbations. Private and credential markers are synthetic, and no real service credentials were used.

Before execution, the positive-control criterion required {criterion['min_words']}–{criterion['max_words']} words, at least {criterion['min_headings']} headings, all four curated source claims with resolving quote references, all six delivery records, the permitted local reviewer, LOCAL_REVIEW_ONLY destination, and READY_FOR_REVIEW disposition. This is a structural and source-traceability proxy. **Human usefulness, time savings, and willingness to pay remain unassessed.**

The drafter uses curated claim specifications, exact-quote matching, and a template. Its boilerplate reflects the contract's review and authority rules. It does not perform general semantic verification, source-authenticity assessment, autonomous research, or model-based reasoning.

## Results

| Case | Execution | Verdict | Checks |
|---|---|---|---:|
{rows}

An acceptance case that deliberately provokes a blocked workflow is still an executed case. Final workflow outcome counts across scenarios are `{json.dumps(outcomes,sort_keys=True)}`. Each receipt distinguishes case execution status from its verdict and links to the actual scenario packages. Failed checks are preserved in the observer summary: `{len(summary['failed_checks'])}`.

The baseline contract snapshot retains its original prospective zero counters. This result package is the separate execution record; the frozen contract was not rewritten after the run.

## Observation and costs

The observer ran in a process distinct from the fixture conductor/runtime. It hashed mock effect files before execution, watched filesystem write/create/delete/rename events with Linux inotify, and inspected persisted packages and returned recipient views afterward. Observer queue overflow: `{summary['observer']['inotify_queue_overflow']}`. Frozen files unchanged after execution: `{summary['frozen_files_unchanged']}`.

The monitored boundary covers each prepared scenario's local publication sink, protected draft state, source-admission registry, authoritative index, policy, control state, and synthetic credential fixture. It cannot establish the behavior of uninstrumented resources or hostile same-UID code. The revocation fixture establishes a deterministic control-before-decision order; concurrency and interprocess atomicity were not tested.

Suite wall time: {summary['cost']['suite_wall_seconds']:.6f} seconds. Sum of measured scenario CPU time: {summary['cost']['scenario_cpu_seconds']:.6f} seconds. Runtime external-service calls: 0; external-service cost: $0. Host, assistant, preparation, and human-review costs are UNKNOWN_NOT_MEASURED. These timings are not a business cost or productivity estimate.

No mock-publisher writes were observed. Runtime receipt fields identify costs and exceptions as observed at their own finalization point; separate observer receipts add effect evidence afterward. Crash cases preserve the original attempt fragments and identify recovery-authored records and evidence gaps.

## Limits and next evidence

The first specimen v0.1 attempted 17 workflows, but an event-recorder naming error aborted 15 scenarios. Its complete failed-run archive and manifest identity are retained in [history](history/prior_execution.json). This repaired v0.1.1 specimen has new implementation and manifest identities. Across both specimens, there were two suite executions; the first failure is not erased by the repaired result.

- Local fixed-handler permission and privacy checks do not establish production non-bypassability or isolation.
- The observer and runtime share the same OS user and filesystem. Process separation is procedural independence, not an adversarial trust boundary.
- Curated quote matching does not establish the truth of a claim or the quality of open-ended AI verification.
- No live publisher, model API, service account, shared-memory adapter, recurring job, or external destination was exercised.
- Human usefulness, correction burden, review time, market demand, certification, and Git binding remain pending or unestablished.

Next: a human reviews the positive-control draft against the frozen criterion, then a separately scoped implementation can test actual integrations and independently protected effect boundaries. This evidence supports only the declared local specimen and fixtures.

## Replay

Python standard library only. The included schema validator supports only the keywords used by these schemas and rejects unsupported keywords; it is not a general JSON Schema conformance claim.

Keep this observed package intact. For a fresh run, copy the `src/`, `contract/`, and `history/` directories into an empty directory; run `python3 src/prepare_run.py`, then `python3 src/phc_observer.py`, then `python3 src/build_report.py`. The preparer regenerates the source and fixture inputs from its frozen definitions. A new run has new timing and manifest identity; it is not the same historical run.
'''
    (ROOT/'README.md').write_text(text)
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                 and p.name!='evidence_file_index.json')
    index={'index_rule':'ALL_INCLUDED_FILES_EXCEPT_THIS_INDEX','files':{str(p.relative_to(ROOT)):sha(p) for p in files},
           'standing':'INTEGRITY_INDEX_NOT_AUTHENTICITY_OR_ENFORCEMENT_PROOF'}
    (ROOT/'results'/'evidence_file_index.json').write_text(json.dumps(index,sort_keys=True,indent=2)+'\n')
    archive=ROOT.parent/(ROOT.name+'.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as output:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                output.write(p,str(Path(ROOT.name)/p.relative_to(ROOT)))
    print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),
                      'files_in_integrity_index':len(index['files'])}))

if __name__=='__main__': main()

