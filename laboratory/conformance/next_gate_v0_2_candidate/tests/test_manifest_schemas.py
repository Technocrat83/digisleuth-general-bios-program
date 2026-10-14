"""Known synthetic schema checks. No review, corpus admission or runtime execution."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from datetime import datetime, timezone
from importlib.metadata import version
import json
import platform
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_NAMES = ['corpus_manifest.schema.json', 'pending_admission_ledger.schema.json',
                'partition_freeze.schema.json']
SCHEMAS = {name: json.loads((ROOT / name).read_text()) for name in SCHEMA_NAMES}
RESULTS = []
for name, schema in SCHEMAS.items():
    Draft202012Validator.check_schema(schema)
    RESULTS.append({'case': 'META_SCHEMA:' + name, 'pass': True})
VALIDATORS = {name: Draft202012Validator(schema) for name, schema in SCHEMAS.items()}
FAMILIES = json.loads((ROOT / 'manifest_admission_contract.json').read_text())['permanent_excluded_families']

def reference(label):
    raw = ('SYNTHETIC_DEVELOPMENT_STUB:' + label).encode()
    return {'locator': 'synthetic://' + label, 'sha256': sha256(raw).hexdigest(), 'size_bytes': len(raw)}

def record(split='train'):
    source_revision = 'snapshot:sha256:' + reference('source')['sha256']
    row = {
        'source_revision': source_revision,
        'reviewed_target': {'artifact': reference('target'), 'independent_review': {
            'review_status': 'ACCEPTED', 'reviewer_identity': 'SYNTHETIC_REVIEWER_UNAUTHENTICATED',
            'receipt': reference('review_receipt'), 'independence_evidence': reference('independence'),
            'authentication_evidence': reference('review_authentication'), 'authentication_status': 'VERIFIED'}},
        'lineage_group': {'group_id': 'SYNTHETIC_DEVELOPMENT_GROUP', 'ancestor_group_ids': [],
                          'origin_families': [], 'derived_from_families': [],
                          'known_development_case_ids': [], 'lineage_complete': True,
                          'verification_receipt': reference('lineage_receipt')},
        'assigned_split': split, 'input': reference('input'), 'invariants_and_rubric': reference('rubric'),
        'provenance': {'source_artifact': reference('source'), 'source_standing': 'SYNTHETIC_DEVELOPMENT_ONLY',
                       'founder_intention_reference': 'SYNTHETIC_PROTOCOL_STUB', 'jurisdiction': 'SYNTHETIC_SCOPE',
                       'epoch': 'SYNTHETIC_EPOCH', 'source_verification_receipt': reference('source_verification'),
                       'prior_admission_dependencies': [], 'admission_dependencies_complete': True},
        'admission': {'disposition': 'ADMITTED', 'receipt': reference('admission_receipt'),
                      'verifier_identity': 'SYNTHETIC_VERIFIER_UNAUTHENTICATED',
                      'authentication_evidence': reference('admission_authentication'),
                      'authentication_status': 'VERIFIED'},
    }
    identity = [source_revision, row['input']['sha256'], row['reviewed_target']['artifact']['sha256'],
                row['lineage_group']['group_id']]
    row['example_id'] = 'ex_' + sha256(json.dumps(identity, separators=(',', ':')).encode()).hexdigest()
    return row

def manifest(row=None):
    return {'manifest_id': 'SYNTHETIC_MANIFEST', 'schema_revision': 'DIGISLEUTH_ADMITTED_CORPUS_MANIFEST_v0.2_candidate',
            'inventory_complete': True, 'source_registry': reference('source_registry'),
            'exclusion_registry': reference('exclusions'), 'admission_policy': reference('policy'),
            'examples': [record() if row is None else row]}

def check(name, value, expected_valid, schema='corpus_manifest.schema.json'):
    errors = list(VALIDATORS[schema].iter_errors(value))
    valid = not errors
    RESULTS.append({'case': name, 'expected_structural_validity': expected_valid,
                    'observed_structural_validity': valid, 'pass': valid == expected_valid,
                    'schema_error_paths': sorted({str(list(e.absolute_path)) for e in errors})})

for split in ['train', 'regression_dev', 'holdout']:
    check('EXACT_SPLIT:' + split, manifest(record(split)), True)
for field in ['example_id', 'source_revision', 'reviewed_target', 'lineage_group', 'assigned_split']:
    row = record(); del row[field]
    check('MISSING_CORE_FIELD:' + field, manifest(row), False)
for legacy in ['TRAIN', 'DEVELOPMENT_VALIDATION', 'QUARANTINE', 'UNASSIGNED', 'dev']:
    row = record(); row['assigned_split'] = legacy
    check('LEGACY_SPLIT_REJECTED:' + legacy, manifest(row), False)
for family in FAMILIES:
    for relation in ['origin_families', 'derived_from_families']:
        for split in ['train', 'regression_dev', 'holdout']:
            row = record(split); row['lineage_group'][relation] = [family]
            check('FAMILY_PARTITION:' + family + ':' + relation + ':' + split,
                  manifest(row), split == 'regression_dev')
for split in ['train', 'regression_dev', 'holdout']:
    row = record(split); row['lineage_group']['known_development_case_ids'] = [FAMILIES[0]]
    check('KNOWN_CASE_PARTITION:' + split, manifest(row), split == 'regression_dev')
    row = record(split); row['lineage_group']['ancestor_group_ids'] = [FAMILIES[0]]
    check('KNOWN_ANCESTOR_PARTITION:' + split, manifest(row), split == 'regression_dev')
row = record(); del row['provenance']
check('PROVENANCE_MISSING', manifest(row), False)
row = record(); row['source_revision'] = 'general-bios-laboratory-v1'
check('MUTABLE_BRANCH_REVISION_REJECTED', manifest(row), False)
row = record(); row['source_revision'] = '03c9580'
check('ABBREVIATED_COMMIT_REJECTED', manifest(row), False)
row = record(); row['example_id'] = 'arbitrary_id'
check('NONDETERMINISTIC_ID_FORMAT_REJECTED', manifest(row), False)
row = record(); row['reviewed_target']['independent_review']['review_status'] = 'PENDING'
check('UNACCEPTED_TARGET_REJECTED', manifest(row), False)
row = record(); del row['reviewed_target']['independent_review']['authentication_evidence']
check('MISSING_REVIEW_AUTHENTICATION_REFERENCE', manifest(row), False)
row = record(); row['reviewed_target']['independent_review']['authentication_status'] = 'NOT_VERIFIED'
check('UNVERIFIED_REVIEW_REJECTED', manifest(row), False)
row = record(); row['lineage_group']['lineage_complete'] = False
check('INCOMPLETE_LINEAGE_REJECTED', manifest(row), False)
row = record(); row['provenance']['admission_dependencies_complete'] = False
check('INCOMPLETE_ADMISSION_DEPENDENCIES_REJECTED', manifest(row), False)
row = record(); row['admission']['disposition'] = 'PENDING_ADMISSION'
check('PENDING_ROW_BARRED_FROM_MANIFEST', manifest(row), False)
value = manifest(); value['examples'] = []
check('EMPTY_MANIFEST_REJECTED', value, False)
value = manifest(); value['examples'].append(deepcopy(value['examples'][0]))
check('IDENTICAL_DUPLICATE_RECORD_REJECTED', value, False)
value = manifest(); value['inventory_complete'] = False
check('INCOMPLETE_INVENTORY_REJECTED', value, False)
value = manifest(); value['examples'][0]['partition'] = 'TRAIN'
check('LEGACY_ALIAS_REJECTED', value, False)

ledger = {'ledger_id': 'SYNTHETIC_INTAKE', 'schema_revision': 'DIGISLEUTH_PENDING_ADMISSION_LEDGER_v0.2_candidate',
          'execution_eligible': False, 'pending_records': [{'intake_id': 'SYNTHETIC_INTAKE_01',
          'raw_record': {'source_revision': 'unresolved'}, 'disposition': 'PENDING_ADMISSION',
          'blocking_obligations': ['SCHEMA_INCOMPLETE', 'PROVENANCE_UNVERIFIED']}]}
check('PARTIAL_RECORD_ALLOWED_ONLY_IN_PENDING_LEDGER', ledger, True, 'pending_admission_ledger.schema.json')
bad = deepcopy(ledger); bad['execution_eligible'] = True
check('PENDING_EXECUTION_ELIGIBILITY_REJECTED', bad, False, 'pending_admission_ledger.schema.json')
bad = deepcopy(ledger); bad['pending_records'][0]['disposition'] = 'ADMITTED'
check('ADMITTED_DISPOSITION_REJECTED_IN_PENDING_LEDGER', bad, False, 'pending_admission_ledger.schema.json')

freeze = {'freeze_id': 'SYNTHETIC_FREEZE', 'schema_revision': 'DIGISLEUTH_PARTITION_FREEZE_v0.2_candidate',
          'signed_payload': {**{key: reference(key) for key in ['manifest', 'split_membership', 'exclusion_registry',
                'independent_target_review_inventory', 'custody_and_access_policy', 'exposure_audit']},
                'signing_profile': 'SYNTHETIC_DETACHED_PROFILE', 'freeze_before_first_exposure': True,
                'split_counts': {'train': 1, 'regression_dev': 1, 'holdout': 1}},
          'signed_payload_sha256': reference('signed_payload')['sha256'],
          'signature': {'algorithm': 'SYNTHETIC_UNAUTHENTICATED_SIGNATURE', 'signer_identity': 'SYNTHETIC_SIGNER',
                'detached_signature': reference('signature'), 'independently_pinned_trust_anchor': reference('trust_anchor'),
                'verification_receipt': reference('signature_verification'), 'verification_status': 'VERIFIED'}}
check('DETACHED_FREEZE_REFERENCE_STRUCTURE', freeze, True, 'partition_freeze.schema.json')
bad = deepcopy(freeze); del bad['signature']
check('DIGEST_WITHOUT_SIGNATURE_REJECTED', bad, False, 'partition_freeze.schema.json')
bad = deepcopy(freeze); del bad['signature']['independently_pinned_trust_anchor']
check('SIGNATURE_WITHOUT_TRUST_ANCHOR_REJECTED', bad, False, 'partition_freeze.schema.json')
bad = deepcopy(freeze); bad['signed_payload']['freeze_before_first_exposure'] = False
check('POST_EXPOSURE_FREEZE_REJECTED', bad, False, 'partition_freeze.schema.json')

failed = [r for r in RESULTS if not r['pass']]
report = {
    'scope': 'SYNTHETIC_DEVELOPMENT_SCHEMA_GUARDS_ONLY',
    'standing': 'CANDIDATE_SPECIFICATION', 'recorded_at': datetime.now(timezone.utc).isoformat(),
    'python': platform.python_version(), 'jsonschema': version('jsonschema'),
    'schemas': {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in SCHEMA_NAMES},
    'test_source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
    'dependency_lock_sha256': sha256((ROOT / 'validation/requirements.lock').read_bytes()).hexdigest(),
    'checks': len(RESULTS), 'passed': len(RESULTS) - len(failed), 'failed': len(failed),
    'records': RESULTS,
    'receipt_authentication': 'NOT_EVALUATED; all accepted/verified examples are synthetic representation stubs',
    'full_admission_checks': 'UNBOUND; schemas do not recompute IDs, authenticate receipts, resolve semantic ancestry or verify custody',
    'actual_corpus_examples_admitted': 0, 'holdout_executions': 0,
    'authority_enforcement': 'NOT_EVALUATED', 'release': 'HOLD',
}
(ROOT / 'evidence/schema_guard_results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['checks', 'passed', 'failed', 'scope', 'actual_corpus_examples_admitted', 'authority_enforcement', 'release']}))
sys.exit(bool(failed))
