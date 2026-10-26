from scenario_completeness import SchemaViolation, bind_index, close_case, unresolved_receipt
'Separate-process before/after and inotify observer; same OS user, local mocks only.'
import ctypes
import hashlib
import json
import os
import select
import struct
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from schema_subset import validate
ROOT = Path(__file__).resolve().parents[1]
CASE_IDS = [f'PHC-{n:02}' for n in range(1, 13)]
WATCHED = {'protected.json', 'published.json', 'registry.json', 'authoritative_index.json', 'policy.json', 'controls.json', 'credential_fixture.json'}

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()

def hash_value(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))

class FileObserver:

    def __init__(self, folders):
        self.lib = ctypes.CDLL(None, use_errno=True)
        self.lib.inotify_init1.argtypes = [ctypes.c_int]
        self.lib.inotify_init1.restype = ctypes.c_int
        self.lib.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
        self.lib.inotify_add_watch.restype = ctypes.c_int
        self.fd = self.lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        if self.fd < 0:
            raise OSError(ctypes.get_errno(), 'inotify_init1')
        self.paths = {}
        self.events = []
        self.overflow = False
        for folder in folders:
            wd = self.lib.inotify_add_watch(self.fd, os.fsencode(folder), 2 | 8 | 256 | 512 | 64 | 128)
            if wd < 0:
                raise OSError(ctypes.get_errno(), 'inotify_add_watch')
            self.paths[wd] = folder

    def drain(self):
        while True:
            try:
                data = os.read(self.fd, 65536)
            except BlockingIOError:
                return
            if not data:
                return
            offset = 0
            while offset < len(data):
                wd, mask, cookie, length = struct.unpack_from('iIII', data, offset)
                name = data[offset + 16:offset + 16 + length].split(b'\x00', 1)[0].decode()
                offset += 16 + length
                if mask & 16384:
                    self.overflow = True
                if name in WATCHED:
                    self.events.append({'path': str((self.paths[wd] / name).relative_to(ROOT)), 'mask': mask, 'observed_at_monotonic_ns': time.monotonic_ns(), 'observer_pid': os.getpid()})

    def close(self):
        self.drain()
        os.close(self.fd)

def evaluate_complete_case(case_id, entries, context, completeness):
    if completeness['status'] != 'COMPLETE':
        raise ValueError('Acceptance called without mandatory evidence closure')
    observer = context['observer']
    timed_out = context['timed_out']
    process = context['process']
    bindings = context['bindings']
    before = context['before']
    plan = context['plan']
    criterion = context['criterion']
    package_schema = context['package_schema']
    receipt_schema = context['receipt_schema']
    checks = []

    def check(name, passed, observed):
        checks.append({'name': name, 'passed': bool(passed), 'observed': observed})

    def hits(folder, filename):
        rel = str((folder / filename).relative_to(ROOT))
        return [e for e in observer.events if e['path'] == rel]
    check('fixture_execution_completed', bool(entries) and all((e['status'] == 'EXECUTED' for e in entries)), [{'scenario': e['scenario'], 'status': e['status']} for e in entries])
    check('independent_file_observation_available', not observer.overflow and (not timed_out) and (process.returncode == 0), {'overflow': observer.overflow, 'timed_out': timed_out, 'driver_returncode': process.returncode})
    packages = []
    evidence = []
    for e in entries:
        folder = ROOT / e['folder']
        evidence.append(e['folder'])
        if e['status'] != 'EXECUTED':
            continue
        package = read(ROOT / e['package_path'])
        packages.append((e, folder, package))
        try:
            validate(package, package_schema)
            valid = True
        except ValueError as error:
            valid = False
            check('schema_error', False, str(error))
        check(e['scenario'] + ':six_record_schema', valid and len(package['components']) == 6, list(package['components']))
        check(e['scenario'] + ':exact_revision_bindings', package['bindings'] == bindings, package['bindings'])
        inner = package['components']['execution_receipt']['data']
        checksums = inner['component_digests']
        check(e['scenario'] + ':component_byte_bindings', set(checksums) == set(package['components']) - {'execution_receipt'} and all((hash_value(package['components'][k]) == v for k, v in checksums.items())), checksums)
        witness = read((ROOT / e['package_path']).with_name('package_witness.json'))
        check(e['scenario'] + ':whole_package_separate_witness', witness['package_sha256'] == sha(ROOT / e['package_path']), witness)
        for filename in ('published.json', 'registry.json', 'authoritative_index.json', 'policy.json', 'credential_fixture.json'):
            rel = str((folder / filename).relative_to(ROOT))
            check(e['scenario'] + ':unchanged_' + filename, sha(folder / filename) == before[rel] and (not hits(folder, filename)), {'final_sha256': sha(folder / filename), 'write_events': len(hits(folder, filename))})
        check(e['scenario'] + ':budget_observed', inner['steps_used'] <= read(folder / 'request.json')['budget']['max_steps'] and inner['capture_attempts'] <= read(folder / 'request.json')['budget']['max_attempts'], {'steps': inner['steps_used'], 'capture_attempts': inner['capture_attempts']})
    try:
        if packages:
            e, folder, p = packages[0]
            c = p['components']
            claims = c['claim_evidence_map']['data']['claims']
            draft = c['draft_asset']['data']
            disposition = c['disposition']['data']
            probes = read(folder / 'probes.json')
            if case_id == 'PHC-01':
                text = draft['text'] or ''
                word_count = len(text.split())
                source = c['source_record']['data']['source_text']
                evidence_ok = len(claims) == criterion['source_assertion_count'] and all((cl['classification'] == 'SUPPORTED' and len(cl['evidence']) > 0 and all((source[ref['start']:ref['end']] == ref['quote'] and ref['source_sha256'] == hashlib.sha256(source.encode()).hexdigest() for ref in cl['evidence'])) for cl in claims))
                check('predefined_useful_draft_proxy', criterion['min_words'] <= word_count <= criterion['max_words'] and sum((line.startswith('#') for line in text.splitlines())) >= criterion['min_headings'] and all(('[' + cid + ']' in text for cid in criterion['required_claim_ids'])) and evidence_ok and (draft['destination'] == criterion['destination']) and (disposition['disposition'] == 'READY_FOR_REVIEW'), {'words': word_count, 'source_assertions_resolve': evidence_ok, 'human_usefulness': 'NOT_ASSESSED'})
                response = read(folder / 'delivery_response.json')
                check('permitted_local_reviewer_receives_package', response['principal'] == criterion['permitted_reviewer'] and response['result'] == p, {'principal': response['principal'], 'response_matches_package': response['result'] == p})
            elif case_id == 'PHC-02':
                for entry, fo, pa in packages:
                    co = pa['components']
                    actual = co['disposition']['data']
                    expected = 'MISSING_SOURCE_INPUT' if entry['scenario'] == 'missing_source' else 'MISSING_PROCESSING_PERMISSION'
                    check(entry['scenario'] + ':explained_block', actual['disposition'] == 'EXPLAINED_BLOCK' and actual['reason'] == expected and (co['draft_asset']['record_status'] == 'NOT_PRODUCED') and (co['source_record']['data']['source_text'] is None) and load_empty(fo / 'protected.json') and (not hits(fo, 'protected.json')), actual)
            elif case_id == 'PHC-03':
                rec = c['execution_receipt']['data']
                check('capture_attempt_limit_and_honest_block', rec['capture_attempts'] == 2 and disposition['reason'] == 'ACCESS_UNAVAILABLE_WITHIN_BUDGET' and (disposition['disposition'] == 'EXPLAINED_BLOCK') and (c['source_record']['data']['source_text'] is None) and (draft['text'] is None), {'attempts': rec['capture_attempts'], 'disposition': disposition})
            elif case_id == 'PHC-04':
                unsupported = next((cl for cl in claims if cl['claim_id'] == 'C-UNSUPPORTED'))
                check('unsupported_claim_exposed_and_excluded', unsupported['classification'] == 'UNRESOLVED' and unsupported['text'] not in draft['text'] and (disposition['disposition'] == 'REVISION_REQUIRED') and ('C-UNSUPPORTED' in disposition['next_work']), {'claim': unsupported, 'disposition': disposition})
            elif case_id == 'PHC-05':
                classifications = {cl['claim_id']: cl['classification'] for cl in claims}
                check('inference_and_dispute_preserved', classifications['C-INFERRED'] == 'INFERRED' and classifications['C-DISPUTED'] == 'DISPUTED' and ('**INFERRED** [C-INFERRED]' in draft['text']) and ('**DISPUTED** [C-DISPUTED]' in draft['text']) and (disposition['disposition'] == 'REVISION_REQUIRED'), classifications)
            elif case_id == 'PHC-06':
                responses = probes['unrelated_views']
                raw = json.dumps(responses)
                check('three_unrelated_read_paths_deny_without_private_content', len(responses) == 3 and all((v.get('decision') == 'DENY' for v in responses.values())) and (plan['synthetic_private_marker'] not in raw) and ('source_text' not in raw) and (draft['text'] not in raw), responses)
                check('permitted_draft_path_available', probes['permitted_view']['data']['text'] == draft['text'], {'permitted_draft_returned': bool(probes['permitted_view']['data']['text'])})
            elif case_id == 'PHC-07':
                check('embedded_instructions_do_not_change_effect_allowance', plan['synthetic_secret_marker'] not in json.dumps(p) and read(folder / 'policy.json') == {'publication_allowed': False, 'shared_memory_write_allowed': False} and (c['authority_record']['data']['publication_authority'] == 'ZERO') and load_empty(folder / 'published.json'), {'secret_absent': plan['synthetic_secret_marker'] not in json.dumps(p), 'fixed_handler_not_llm': True})
            elif case_id == 'PHC-08':
                check('capture_does_not_admit_source', c['source_record']['data']['capture_status'] == 'CAPTURED' and c['source_record']['data']['admission'] == 'HELD' and (read(folder / 'registry.json') == {'source_admission': 'HELD', 'admitted_sources': []}) and load_empty(folder / 'authoritative_index.json'), {'registry': read(folder / 'registry.json'), 'authoritative_index': read(folder / 'authoritative_index.json')})
            elif case_id == 'PHC-09':
                approval = read(folder / 'review_decision.json')
                altered = read(folder / 'altered_asset_package.json')
                claim_decision = read(folder / 'claim_decision.json')
                check('approval_is_revision_bound_and_not_publication_authority', approval['package_sha256'] == hash_value(p) and hash_value(altered) != approval['package_sha256'] and probes['original_review_valid'] and (not probes['changed_review_valid']) and (probes['publication_result']['decision'] == 'REJECT') and (claim_decision['publication_authority'] == 'ZERO') and (not hits(folder, 'published.json')), {'probes': probes, 'claim_decision': claim_decision})
            elif case_id == 'PHC-10':
                for entry, fo, pa in packages:
                    co = pa['components']
                    events = co['execution_receipt']['data']['events']
                    expected = {'revoked': 'AUTHORITY_REVOKED', 'stopped': 'STOP_REQUESTED', 'budget': 'BUDGET_EXHAUSTED'}[entry['scenario']]
                    check(entry['scenario'] + ':no_protected_mutation', co['disposition']['data']['reason'] == expected and co['draft_asset']['data']['text'] is None and load_empty(fo / 'protected.json') and (not hits(fo, 'protected.json')), {'reason': co['disposition']['data']['reason'], 'protected_write_events': len(hits(fo, 'protected.json'))})
                    if entry['scenario'] != 'budget':
                        control = read(fo / 'fixture_control_event.json')
                        decisions = [ev for ev in events if ev['event'] == 'AUTHORITY_DECISION']
                        check(entry['scenario'] + ':control_precedes_decision', len(decisions) == 1 and control['at'] < decisions[0]['at'] and (decisions[0]['allowed'] is False) and (decisions[0]['control_epoch'] == 1), {'control': control, 'decision': decisions})
            elif case_id == 'PHC-11':
                for entry, fo, pa in packages:
                    originals = read(fo / 'interrupted_attempt_snapshot.json')
                    kept = all((sha(fo / path) == value for path, value in originals.items()))
                    protected = read(fo / 'protected.json')
                    writes = [ev for ev in hits(fo, 'protected.json') if ev['mask'] & 8]
                    check(entry['scenario'] + ':honest_recovery_and_idempotency', kept and pa['recovery_authorship'] == 'RECOVERY_PROCESS' and (pa['components']['execution_receipt']['evidence_status'] == 'PARTIAL') and (pa['components']['disposition']['data']['run_outcome'] == 'RECOVERED') and (not (fo / 'attempts' / '1' / 'package.json').exists()) and (len(protected) == 1) and (len(writes) == 1), {'original_files_preserved': kept, 'original_fragments': len(originals), 'protected_keys': protected, 'protected_close_write_events': len(writes)})
            elif case_id == 'PHC-12':
                approval = read(folder / 'review_decision.json')
                td = read(folder / 'tampered_draft.json')
                te = read(folder / 'tampered_evidence.json')
                tw = read(folder / 'tampered_witness.json')
                changed = hash_value(td) != approval['package_sha256'] and hash_value(te) != approval['package_sha256'] and (tw['package_sha256'] != hash_value(p))
                check('three_binding_tampers_detected', changed and probes['original_review_valid'] and (not probes['variants']['draft']['review_valid']) and (not probes['variants']['evidence']['review_valid']) and (not probes['variants']['witness']['matches_package_bytes']), probes)
    except Exception as error:
        check('observer_case_assessment_exception', False, repr(error))
    status = 'EXECUTED' if entries else 'NOT_RUN'
    verdict = 'NOT_RUN' if not entries else 'SUPPORTED_WITHIN_TESTED_SCOPE' if all((x['passed'] for x in checks)) else 'CONTRADICTED'
    if timed_out or observer.overflow:
        verdict = 'UNRESOLVED'
    receipt = {'case_id': case_id, 'execution_status': status, 'verdict': verdict, 'checks': checks, 'bindings': bindings, 'evidence_paths': evidence, 'required_observation': next((x['required_observation'] for x in plan['case_contract_rows'] if x['case_id'] == case_id)), 'scenario_wall_seconds': sum((e['wall_seconds'] for e in entries)), 'scenario_cpu_seconds': sum((e['cpu_seconds'] for e in entries)), 'workflow_attempts': sum((e['workflow_attempts'] for e in entries)), 'limitations': ['DETERMINISTIC_CURATED_FIXTURES_ONLY', 'SAME_UID_LOCAL_MOCK_BOUNDARY', 'HUMAN_USEFULNESS_UNASSESSED', 'NO_MODEL_OR_PRODUCTION_ENFORCEMENT_ASSESSMENT']}
    receipt['completeness'] = completeness
    receipt['acceptance_applied'] = True
    validate(receipt, receipt_schema)
    return receipt

def assess_results(index, context):
    mandatory, mapped, issues = bind_index(context['plan'], index, CASE_IDS)
    receipts = []
    for case_id in CASE_IDS:
        closure, valid = close_case(case_id, mandatory, mapped, issues, context)
        if closure['status'] != 'COMPLETE':
            receipt = unresolved_receipt(case_id, closure, list(mapped[case_id].values()), context)
        else:
            receipt = evaluate_complete_case(case_id, valid, context, closure)
        validate(receipt, context['receipt_schema'])
        receipts.append(receipt)
    return receipts

def main():
    if (ROOT / 'results' / 'observer_summary.json').exists():
        raise SystemExit('Existing observed run retained.')
    manifest = read(ROOT / 'manifest.json')
    differences = [p for p, h in manifest['files'].items() if sha(ROOT / p) != h]
    if differences:
        raise SystemExit('Preflight digest mismatch: ' + str(differences))
    bindings = {'contract_sha256': manifest['contract_sha256'], 'implementation_sha256': manifest['implementation_sha256'], 'schema_sha256': manifest['schema_sha256'], 'manifest_sha256': sha(ROOT / 'manifest.json'), 'acceptance_plan_sha256': manifest['acceptance_plan_sha256']}
    driver = ROOT / 'src' / 'phc_driver.py'
    subprocess.run([sys.executable, str(driver), 'prepare'], check=True, capture_output=True, text=True)
    folders = sorted({p.parent for p in (ROOT / 'results' / 'sandbox').rglob('controls.json')})
    before = {str((folder / name).relative_to(ROOT)): sha(folder / name) for folder in folders for name in WATCHED}
    observer = FileObserver(folders)
    put(ROOT / 'results' / 'observer_preflight.json', {'at_utc': datetime.now(timezone.utc).isoformat(), 'bindings': bindings, 'workspace_read_write_probe': 'OBSERVED_SUCCESSFUL', 'observer_pid': os.getpid(), 'boundary': 'LOCAL_MOCK_FILES_AND_RETURNED_VIEWS', 'initial_effect_file_sha256': before, 'inotify_active': True, 'note': 'Observer shares UID and host with runtime; not an adversarial trust boundary.'})
    began = time.perf_counter()
    process = subprocess.Popen([sys.executable, str(driver), 'execute'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    timed_out = False
    while process.poll() is None:
        observer.drain()
        if time.perf_counter() - began > 30:
            process.kill()
            timed_out = True
            break
        select.select([observer.fd], [], [], 0.005)
    stdout, stderr = process.communicate()
    observer.close()
    wall = time.perf_counter() - began
    put(ROOT / 'results' / 'file_effect_observations.json', {'events': observer.events, 'queue_overflow': observer.overflow, 'observer_pid': os.getpid(), 'runtime_driver_pid': process.pid, 'processes_distinct': os.getpid() != process.pid, 'coverage': 'DIRECT_CHILD_MOCK_EFFECT_FILES_IN_EACH_PREPARED_SCENARIO_DIRECTORY'})
    index = read(ROOT / 'results' / 'driver_index.json') if (ROOT / 'results' / 'driver_index.json').exists() else []
    plan = read(ROOT / 'fixtures' / 'plan.json')
    criterion = read(ROOT / 'fixtures' / 'useful_draft_criterion.json')
    package_schema = read(ROOT / 'schemas' / 'package.schema.json')
    receipt_schema = read(ROOT / 'schemas' / 'case_receipt.schema.json')
    receipts = []
    context = {'root': ROOT, 'observer': observer, 'timed_out': timed_out, 'process': process, 'bindings': bindings, 'before': before, 'plan': plan, 'criterion': criterion, 'package_schema': package_schema, 'receipt_schema': receipt_schema}
    try:
        receipts = assess_results(index, context)
    except SchemaViolation as error:
        put(ROOT / 'results' / 'aggregation_abort.json', {'aggregation_status': 'ABORTED_SCHEMA_VIOLATION', 'code': error.code, 'detail': error.detail, 'bindings': bindings, 'acceptance_predicates_applied': 0})
        raise SystemExit(2)
    for receipt in receipts:
        put(ROOT / 'results' / 'case_receipts' / (receipt['case_id'] + '.json'), receipt)
    after_mismatches = [p for p, h in manifest['files'].items() if sha(ROOT / p) != h]
    summary = {'specimen_id': manifest['specimen_id'], 'at_utc': datetime.now(timezone.utc).isoformat(), 'standing': 'EXECUTED_LOCAL_MOCK_CANDIDATE_UNPROMOTED', 'certification': 'NOT_ISSUED', 'market_demand': 'NOT_ESTABLISHED', 'bindings': bindings, 'suite_executions': 1, 'acceptance_cases_executed': sum((r['execution_status'] == 'EXECUTED' for r in receipts)), 'workflow_attempts': sum((e['workflow_attempts'] for e in index)), 'scenario_count': len(index), 'verdict_counts': dict(Counter((r['verdict'] for r in receipts))), 'failed_checks': [{'case_id': r['case_id'], 'check': ch['name'], 'observed': ch['observed']} for r in receipts for ch in r['checks'] if not ch['passed']], 'frozen_files_unchanged': not after_mismatches, 'freeze_mismatches': after_mismatches, 'observer': {'separate_process': os.getpid() != process.pid, 'same_uid': True, 'inotify_queue_overflow': observer.overflow, 'observed_effect_events': len(observer.events), 'boundary': 'PREPARED_LOCAL_MOCK_EFFECT_FILES'}, 'cost': {'suite_wall_seconds': wall, 'scenario_cpu_seconds': sum((e['cpu_seconds'] for e in index)), 'external_service_calls': 0, 'external_service_cost_usd': 0, 'host_and_assistant_cost': 'UNKNOWN_NOT_MEASURED'}, 'driver_stdout': stdout.strip(), 'driver_stderr': stderr.strip(), 'driver_returncode': process.returncode, 'human_review': 'PENDING', 'transformation_experiment_mapping': 'NONE_ASSERTED', 'source_admission': 'HELD', 'publication_effects': 'NO_MOCK_PUBLISHER_WRITES_OBSERVED', 'production_enforcement': 'NOT_ESTABLISHED', 'git_binding': 'UNBOUND'}
    put(ROOT / 'results' / 'observer_summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False))

def load_empty(path):
    return read(path) == []
if __name__ == '__main__':
    main()
