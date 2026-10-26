"""Deterministic local publication specimen. No model, network, or live publisher."""
import copy
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

COMPONENTS = ['source_record', 'claim_evidence_map', 'draft_asset',
              'authority_record', 'execution_receipt', 'disposition']

def digest(data):
    return hashlib.sha256(data).hexdigest()

def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + '\n').encode()

def load(path):
    return json.loads(Path(path).read_text())

def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(encoded(value))

def now():
    return datetime.now(timezone.utc).isoformat()

class InjectedCrash(RuntimeError):
    pass

class Runtime:
    def __init__(self, folder, bindings):
        self.folder = Path(folder)
        self.bindings = bindings
        self.lock = RLock()
        self.events = []
        self.used = 0

    def event(self, name, **fields):
        item = {'sequence': len(self.events)+1, 'at': now(), 'event': name, **fields}
        self.events.append(item)
        with self.trace.open('a') as f: f.write(json.dumps(item, sort_keys=True) + '\n')

    def controlled_commit(self, key):
        # Covers deterministic control-before-decision order, not interprocess races.
        with self.lock:
            controls = load(self.folder/'controls.json')
            self.event('AUTHORITY_DECISION', allowed=not (controls['revoked'] or controls['stop']),
                       control_epoch=controls['epoch'])
            if controls['revoked'] or controls['stop']:
                return 'AUTHORITY_REVOKED' if controls['revoked'] else 'STOP_REQUESTED'
            entries = load(self.folder/'protected.json')
            if key not in entries:
                entries.append(key)
                write(self.folder/'protected.json', entries)
                self.event('PROTECTED_COMMIT', key=key)
            else:
                self.event('IDEMPOTENT_REPLAY', key=key)
            return None

    def read_package(self, package, principal, route='package'):
        if principal not in package['components']['authority_record']['data']['result_audience_ids']:
            return {'decision': 'DENY', 'reason': 'RESULT_AUDIENCE_MISMATCH'}
        if route == 'draft': return package['components']['draft_asset']
        if route == 'source': return package['components']['source_record']
        return package

    def publish(self, package, approval):
        # This workflow has no external publication operation.
        return {'decision': 'REJECT', 'reason': 'PUBLICATION_OUT_OF_SCOPE',
                'review_valid': self.review_valid(package, approval)}

    def approve_for_review(self, package):
        return {'decision_id': package['run_id']+'-review',
                'package_sha256': digest(encoded(package)),
                'asset_sha256': package['components']['draft_asset']['data'].get('asset_sha256'),
                'audience': package['components']['authority_record']['data']['result_audience_ids'],
                'scope': 'EDITORIAL_REVIEW_ONLY'}

    def review_valid(self, package, approval):
        return (approval['package_sha256'] == digest(encoded(package))
                and approval['asset_sha256'] == package['components']['draft_asset']['data'].get('asset_sha256')
                and approval['audience'] == package['components']['authority_record']['data']['result_audience_ids'])

    def run(self, request, attempt=1, crash_at=None, recovery=False):
        self.events, self.used = [], 0
        self.attempt = self.folder/'attempts'/str(attempt)
        self.attempt.mkdir(parents=True, exist_ok=False)
        self.trace = self.attempt/'events.jsonl'
        wall, cpu = time.perf_counter(), time.process_time()
        run_id = request['run_id']
        author = 'RECOVERY_PROCESS' if recovery else 'RUNTIME_PROCESS'
        package = {'run_id': run_id, 'attempt_id': str(attempt), 'bindings': self.bindings,
                   'components': {}, 'recovery_authorship': author,
                   'original_attempts_preserved': recovery}
        def record(name, data, status='PRESENT', reason=None, evidence='OBSERVED'):
            rec = {'record_id': f'{run_id}-{attempt}-{name}', 'run_id': run_id,
                   'component_type': name, 'record_status': status, 'evidence_status': evidence,
                   'visibility_scope': request['audience'], 'missing_fields': [], 'reason': reason,
                   'author': author, 'data': data}
            package['components'][name] = rec
            write(self.attempt/(name+'.json'), rec)
            return rec
        self.event('ATTEMPT_START', attempt=attempt, recovery=recovery)
        auth = {'requester_id': request['requester'], 'executor_id': 'local-deterministic-specimen',
                'credential_principal_id': 'NONE_NO_AUTHENTICATED_SERVICE',
                'reviewer_id': 'founder-reviewer', 'result_audience_ids': request['audience'],
                'processing_authority': request['permission'], 'source_admission': 'HELD',
                'claim_approval': 'NOT_GRANTED', 'publication_authority': 'ZERO',
                'authority_reference': request['authority_reference'], 'policy_revision': 'LOCAL_PREPARE_ONLY_V1',
                'resource': request['run_id'], 'expiry_condition': 'END_OF_THIS_ATTEMPT',
                'effort_budget': request['budget'], 'operation': 'PREPARE_REVIEW_PACKAGE'}
        record('authority_record', auth)
        reason = None
        source = request.get('source')
        source_data = {'capture_status': 'NOT_ATTEMPTED', 'source_text': None,
                       'input_locator': 'CURRENT_USER_MESSAGE_PLUS_LABELED_FIXTURE_OVERLAY_IF_PRESENT',
                       'processing_restrictions': 'LOCAL_PREPARATION_FOR_DECLARED_REVIEWER_ONLY',
                       'attribution': 'USER_SUBMITTED_NOT_INDEPENDENTLY_AUTHENTICATED',
                       'byte_integrity': 'NO_BYTES_CAPTURED', 'access_limits': [],
                       'admission': 'HELD', 'source_sha256': None}
        def step(name):
            if self.used >= request['budget']['max_steps']:
                self.event('BUDGET_EXHAUSTED', step=name, used=self.used)
                return False
            self.used += 1
            self.event('STEP', step_name=name, used=self.used)
            return True
        if source is None: reason = 'MISSING_SOURCE_INPUT'
        elif not request['permission']: reason = 'MISSING_PROCESSING_PERMISSION'
        else:
            for number in range(request['budget']['max_attempts']):
                if not step('CAPTURE'): reason = 'BUDGET_EXHAUSTED'; break
                self.event('CAPTURE_ATTEMPT', number=number+1, result='UNAVAILABLE' if request.get('unavailable') else 'CAPTURED')
                if request.get('unavailable'):
                    source_data['capture_status'] = 'UNAVAILABLE'
                    source_data['access_limits'].append('FIXTURE_ACCESS_FAILURE')
                    continue
                source_data.update(capture_status='CAPTURED', source_text=source,
                                   source_sha256=digest(source.encode()), byte_integrity='DIGEST_BOUND')
                break
            if source_data['capture_status'] != 'CAPTURED' and reason is None: reason = 'ACCESS_UNAVAILABLE_WITHIN_BUDGET'
        record('source_record', source_data, reason=reason,
               evidence='OBSERVED' if source_data['capture_status']=='CAPTURED' else 'PARTIAL')
        if crash_at == 'capture':
            self.event('INJECTED_CRASH', stage='capture'); raise InjectedCrash('capture')
        claims = []
        if reason is None:
            for spec in request['claim_specs']:
                quote = spec['quote']
                start = source.find(quote)
                supported = start >= 0
                classification = 'UNRESOLVED'
                if supported:
                    classification = 'DISPUTED' if spec.get('counter_quote') and spec['counter_quote'] in source else ('INFERRED' if spec.get('inference') else 'SUPPORTED')
                claims.append({'claim_id': spec['claim_id'], 'text': spec['text'],
                               'classification': classification, 'review': 'CANDIDATE',
                               'evidence': [] if not supported else [{'source_sha256': source_data['source_sha256'],
                                   'start': start, 'end': start+len(quote), 'quote': quote}],
                               'reason': 'EXACT_QUOTE_FOUND_IN_CURATED_FIXTURE' if supported else 'SUPPORTING_QUOTE_ABSENT',
                               'inference_reasoning': spec.get('reasoning'),
                               'counterevidence': spec.get('counter_quote') if classification=='DISPUTED' else None})
        record('claim_evidence_map', {'claims': claims,
               'assessment_method': 'CURATED_CLAIM_SPECS_EXACT_QUOTE_MATCHING_NOT_SEMANTIC_VERIFICATION'},
               'PRESENT' if claims else 'NOT_PRODUCED', None if claims else reason)
        draft_data = {'asset_type': 'DBA', 'asset_revision': run_id+'-draft-1', 'text': None,
                      'asset_sha256': None, 'intended_audience': 'BUSINESS_OWNER_REVIEWER',
                      'destination': 'LOCAL_REVIEW_ONLY', 'unresolved_work': []}
        if reason is None:
            if not step('DRAFT'): reason = 'BUDGET_EXHAUSTED'
            else:
                rendered = []
                for c in claims:
                    if c['classification']=='UNRESOLVED':
                        draft_data['unresolved_work'].append(c['claim_id']+': SUPPORT_REQUIRED'); continue
                    rendered.append(f"- **{c['classification']}** [{c['claim_id']}]: {c['text']}")
                if not rendered: reason = 'INSUFFICIENT_EVIDENCE_TO_DRAFT'
                else:
                    draft = ('# Reviewing a publication prototype evidence package\n\n'
                             '## What to inspect\n\n'+'\n'.join(rendered)+'\n\n'
                             '## Review decision\n\n'
                             'This is a proposed draft for review. Inspect the linked source evidence and the outstanding issues before recording a disposition. '
                             'The source record, claim map, authority record, execution receipt, and disposition accompany this draft so the reviewer can inspect the work and its limits. '
                             'Any unsupported assertion is excluded and listed for further review. Editorial review does not grant permission to publish this asset.\n')
                    draft_data.update(text=draft, asset_sha256=digest(draft.encode()))
                    if request.get('control_before_commit'):
                        control = load(self.folder/'controls.json')
                        control.update(epoch=control['epoch']+1,
                                       revoked=request['control_before_commit']=='REVOKE',
                                       stop=request['control_before_commit']=='STOP')
                        write(self.folder/'controls.json', control)
                        self.event('CONTROL_INJECTION', control=request['control_before_commit'], epoch=control['epoch'])
                    reason = self.controlled_commit(run_id+'-draft')
                    if reason: draft_data.update(text=None, asset_sha256=None)
        record('draft_asset', draft_data, 'PRESENT' if draft_data['text'] else 'NOT_PRODUCED', reason)
        if crash_at == 'draft': self.event('INJECTED_CRASH', stage='draft'); raise InjectedCrash('draft')
        unresolved = [c['claim_id'] for c in claims if c['classification']!='SUPPORTED']
        disposition = 'EXPLAINED_BLOCK' if reason else ('REVISION_REQUIRED' if unresolved else 'READY_FOR_REVIEW')
        record('disposition', {'disposition': disposition, 'reason': reason,
               'epistemic_standing': 'UNRESOLVED' if reason or unresolved else 'ASSESSED_WITH_LIMITATIONS',
               'next_work': unresolved or ([reason] if reason else ['FOUNDER_REVIEW_PENDING']),
               'responsible_reviewer': 'founder-reviewer', 'at': now(),
               'run_outcome': 'RECOVERED' if recovery else ('CEASED' if reason in ('AUTHORITY_REVOKED','STOP_REQUESTED','BUDGET_EXHAUSTED') else ('BLOCKED' if reason else 'COMPLETED'))})
        self.event('FINALIZING', disposition=disposition)
        receipt = {'bindings': self.bindings, 'events': self.events.copy(),
                   'exceptions': [reason] if reason else [],
                   'independent_effect_observation': 'PENDING_SEPARATE_OBSERVER_CASE_RECEIPT',
                   'steps_used': self.used, 'capture_attempts': sum(e['event']=='CAPTURE_ATTEMPT' for e in self.events),
                   'cost': {'local_wall_seconds_before_finalization': time.perf_counter()-wall,
                            'local_cpu_seconds_before_finalization': time.process_time()-cpu,
                            'model_calls': 0, 'authenticated_service_calls': 0,
                            'external_service_cost_usd': 0,
                            'host_and_assistant_cost': 'UNKNOWN_NOT_MEASURED'},
                   'evidence_gaps': ['HUMAN_USEFULNESS_UNASSESSED','NO_MODEL_REASONING_TESTED',
                                     'SAME_UID_MOCK_EFFECT_BOUNDARY','NO_CONCURRENT_OR_PRODUCTION_ENFORCEMENT_TEST'],
                   'component_digests': {k: digest(encoded(v)) for k,v in package['components'].items()}}
        if recovery: receipt['evidence_gaps'].append('ORIGINAL_ATTEMPT_INTERRUPTED_RECOVERY_AUTHORED_COMPLETION')
        record('execution_receipt', receipt, evidence='PARTIAL' if recovery else 'OBSERVED')
        if crash_at == 'receipt': self.event('INJECTED_CRASH', stage='receipt'); raise InjectedCrash('receipt')
        write(self.attempt/'package.json', package)
        write(self.attempt/'package_witness.json', {'package_sha256': digest(encoded(package)), 'binding_scope': 'PACKAGE_BYTES_ONLY'})
        return package

