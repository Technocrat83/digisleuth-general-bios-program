"""Synthetic boundary tests, not real theorem or production-enforcement evidence."""
import base64
import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from workflow import (GATES, VERSION, canonical, compile_bundle, digest, evaluate,
                      plan_digest, read_json)


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.temp.name)
        def git(*args):
            return subprocess.check_output(['git', '-C', str(cls.repo), *args],
                                           stderr=subprocess.DEVNULL, text=True).strip()
        git('init')
        git('remote', 'add', 'origin', 'https://github.com/example/synthetic-fixture.git')
        (cls.repo / 'plan.txt').write_text('Synthetic proof, protocol and budget fixture.\n')
        git('add', 'plan.txt')
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
            'commit', '-m', 'Synthetic preregistered plan')
        cls.commit = git('rev-parse', 'HEAD')
        (cls.repo / 'outcome.txt').write_text('Synthetic transformation outcome fixture.\n')
        git('add', 'outcome.txt')
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
            'commit', '-m', 'Synthetic result after plan')
        cls.outcome_commit = git('rev-parse', 'HEAD')
        cls.ua = cls.repo / 'raw-ua-fixture.json'
        cls.ua.write_text('{"synthetic":true,"not_a_real_UA_export":true}\n')
        cls.keys = {stage: Ed25519PrivateKey.generate() for stage in GATES}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        source = lambda identity, name: {'source_id': identity, 'file_path': name,
            'blob_sha256': hashlib.sha256((self.repo / name).read_bytes()).hexdigest(),
            'line_start': 1, 'line_end': 1}
        proposition = 'Synthetic identity map preserves the fixture value.'
        self.payload = {'schema_version': VERSION, 'run_id': 'TEST_RUN',
            'implementation_sha256': hashlib.sha256(Path(__file__).with_name('workflow.py').read_bytes()).hexdigest(),
            'transformation_id': 'SYNTHETIC_TRANSFORM', 'producer_id': 'producer',
            'scope': 'SYNTHETIC_TEST_ONLY', 'source_repository': 'example/synthetic-fixture',
            'source_commit': self.commit, 'scope_paths': ['plan.txt'],
            'sources': [source('PLAN', 'plan.txt')], 'outcome_commit': self.outcome_commit,
            'outcome_sources': [source('OUTCOME', 'outcome.txt')],
            'ua': {'raw_export_sha256': hashlib.sha256(self.ua.read_bytes()).hexdigest(),
                   'producer_revision': '1' * 40, 'source_commit': self.commit,
                   'scope_sha256': digest(['plan.txt'])},
            'theorem': {'theorem_id': 'SYNTHETIC_ONLY', 'proposition': proposition,
                'proposition_sha256': hashlib.sha256(proposition.encode()).hexdigest(),
                'assumptions': ['Synthetic identity fixture only'], 'representation_domain': 'One fixture',
                'jurisdiction': 'TEST_ONLY', 'derivation_ref': 'PLAN', 'applicability_ref': 'PLAN',
                'provenance_ref': 'PLAN', 'abstention_ref': 'PLAN', 'falsification_protocol_ref': 'PLAN',
                'result': 'SATISFIED', 'obligations': {k: 'SATISFIED' for k in
                    ['derivation', 'applicability', 'provenance', 'abstention']},
                'unresolved_contradictions': 0, 'limitation': 'Not a real BIOS theorem ratification'},
            'trial': {'preregistration_ref': 'PLAN', 'outcome_evidence_ref': 'OUTCOME',
                'criteria': ['Synthetic fixture criterion declared before outcome'],
                'observation_scope': 'Synthetic positive control', 'market_demand': 'NOT_ESTABLISHED'},
            'nodes': [{'object_id': 'A', 'object_class': 'STATE', 'title': 'Input', 'evidence_refs': ['PLAN']},
                      {'object_id': 'B', 'object_class': 'TRANSFORMATION', 'title': 'Identity', 'evidence_refs': ['PLAN']}],
            'relations': [{'relation_id': 'R1', 'subject': 'A', 'object': 'B', 'relation_type': 'precedes',
                'scope': 'SYNTHETIC_TEST_ONLY', 'evidence_refs': ['PLAN'], 'certainty': 'DECLARED_IN_SOURCE',
                'schema_version': VERSION, 'authority_id': 'GRAPH_ADMISSION', 'admission_status': 'CANDIDATE'}],
            'claims': [{'claim_id': 'C1', 'text': 'The synthetic identity fixture preserved its value.',
                'classification': 'SUPPORTED', 'evidence_refs': ['OUTCOME'], 'rationale': 'Fixture only',
                'limitation': 'No real execution, theorem or market claim'}],
            'destination': 'Substack:DigiProse', 'audience': 'test-reviewer',
            'preparation_budget_ref': 'PLAN', 'ceased': False}
        self.root = {'snapshot_id': 'EPHEMERAL_TEST_TRUST_ONLY', 'valid_from': '2026-01-01T00:00:00Z',
            'valid_until': '2027-01-01T00:00:00Z', 'keys': {}, 'revoked_receipts': []}
        for stage, role in GATES.items():
            self.root['keys'][stage] = {'principal_id': 'principal-' + stage, 'roles': [role],
                'public_key_base64': base64.b64encode(self.keys[stage].public_key().public_bytes(
                    Encoding.Raw, PublicFormat.Raw)).decode()}
        self.packet = {'payload': self.payload, 'receipts': []}
        self.sign_all()

    def sign_all(self):
        self.packet['receipts'] = []
        for stage in GATES:
            body = {'receipt_id': 'TEST-' + stage, 'stage': stage, 'run_id': self.payload['run_id'],
                'transformation_id': self.payload['transformation_id'],
                'payload_sha256': plan_digest(self.payload) if stage in list(GATES)[:5] else digest(self.payload),
                'decision': 'PASS', 'principal_id': self.root['keys'][stage]['principal_id'],
                'authority_id': stage, 'scope': self.payload['scope'], 'destination': self.payload['destination'],
                'issued_at': '2026-10-01T00:00:00Z', 'expires_at': '2026-12-01T00:00:00Z'}
            signature = self.keys[stage].sign(canonical(body))
            self.packet['receipts'].append({'body': body, 'signature_base64': base64.b64encode(signature).decode()})

    def run_packet(self, **kwargs):
        return evaluate(self.packet, self.root, self.repo, self.ua,
                        now=datetime(2026, 10, 28, tzinfo=timezone.utc), **kwargs)

    def assert_held(self):
        result = self.run_packet()
        self.assertFalse(result['editorial_eligible'], result)
        self.assertTrue(result['blockers'])
        return result

    def test_positive_control_and_six_editorial_records(self):
        result = self.run_packet()
        self.assertTrue(result['editorial_eligible'], result)
        files = compile_bundle(self.packet, result)
        self.assertEqual(len(json.loads(files['biospub/handoff.json'])['components']), 6)
        self.assertEqual(len(json.loads(files['Execution_Graph.canvas'])['edges']), 1)
        self.assertFalse(result['external_publication_authority'])
        self.assertFalse(result['real_execution_performed'])
        plan = json.loads(files['projection_plan.json'])
        self.assertEqual(plan['plan_sha256'], digest(plan['plan']))
        self.assertIsNone(plan['plan']['kernel_projection_grant'])
        for target in plan['plan']['targets']:
            content = files[target['relative_path']].encode()
            self.assertEqual(target['sha256'], hashlib.sha256(content).hexdigest())
            self.assertEqual(target['size_bytes'], len(content))
        for line in files['SHA256SUMS'].splitlines():
            expected, name = line.split('  ', 1)
            self.assertEqual(expected, hashlib.sha256(files[name].encode()).hexdigest())

    def test_tampered_signature(self):
        self.packet['receipts'][0]['signature_base64'] = base64.b64encode(bytes(64)).decode()
        self.assert_held()

    def test_payload_change_invalidates_decisions(self):
        self.payload['claims'][0]['text'] = 'Changed after review'
        self.assert_held()

    def test_plan_changes_invalidate_earlier_decisions(self):
        self.payload['trial']['criteria'].append('Post-hoc target')
        self.assert_held()

    def test_plan_digest_does_not_require_future_outcome(self):
        before = plan_digest(self.payload)
        self.payload['claims'][0]['text'] = 'A later reviewed draft'
        self.payload['trial']['market_demand'] = 'OBSERVED_WITHIN_DECLARED_TRIAL'
        self.assertEqual(before, plan_digest(self.payload))
        self.sign_all()
        self.assertTrue(self.run_packet()['editorial_eligible'])

    def test_missing_graph_admission(self):
        self.packet['receipts'] = [r for r in self.packet['receipts'] if r['body']['stage'] != 'GRAPH_ADMISSION']
        self.assertFalse(self.assert_held()['projection_eligible'])

    def test_missing_product_qualification_retains_only_graph(self):
        self.packet['receipts'] = [r for r in self.packet['receipts'] if r['body']['stage'] != 'PRODUCT_QUALIFICATION']
        self.assertTrue(self.assert_held()['projection_eligible'])

    def test_revoked_receipt(self):
        self.root['revoked_receipts'] = ['TEST-GRAPH_ADMISSION']
        self.assert_held()

    def test_expired_trust_snapshot(self):
        self.root['valid_until'] = '2026-10-01T00:00:00Z'
        self.assert_held()

    def test_expired_receipt(self):
        self.packet['receipts'][0]['body']['expires_at'] = '2026-10-02T00:00:00Z'
        self.assert_held()

    def test_wrong_authority_role(self):
        self.root['keys']['GRAPH_ADMISSION']['roles'] = ['observer']
        self.assert_held()

    def test_implementation_swap(self):
        self.payload['implementation_sha256'] = '0' * 64
        self.sign_all()
        self.assert_held()

    def test_producer_self_adjudication(self):
        self.root['keys']['GRAPH_ADMISSION']['principal_id'] = 'producer'
        self.sign_all()
        self.assert_held()

    def test_independence_cannot_collapse(self):
        self.root['keys']['TRANSFORMATION_WITNESS']['principal_id'] = self.root['keys']['EXECUTION_AUTHORIZATION']['principal_id']
        self.sign_all()
        self.assert_held()

    def test_unresolved_theorem_despite_signed_pass(self):
        self.payload['theorem']['obligations']['abstention'] = 'UNRESOLVED'
        self.sign_all()
        self.assert_held()

    def test_unresolved_contradiction(self):
        self.payload['theorem']['unresolved_contradictions'] = 1
        self.sign_all()
        self.assert_held()

    def test_source_digest_mismatch(self):
        self.payload['sources'][0]['blob_sha256'] = '0' * 64
        self.sign_all()
        self.assert_held()

    def test_ua_digest_mismatch(self):
        self.payload['ua']['raw_export_sha256'] = '0' * 64
        self.sign_all()
        self.assert_held()

    def test_dangling_relation(self):
        self.payload['relations'][0]['object'] = 'MISSING'
        self.sign_all()
        self.assert_held()

    def test_unmapped_constitutional_predicate(self):
        self.payload['relations'][0]['relation_type'] = 'related'
        self.sign_all()
        self.assert_held()

    def test_cease(self):
        self.payload['ceased'] = True
        self.sign_all()
        self.assert_held()

    def test_unresolved_claim_is_not_drafted(self):
        self.payload['claims'][0]['classification'] = 'UNRESOLVED'
        self.sign_all()
        self.assert_held()

    def test_missing_packet_stages_no_earned_edges(self):
        result = evaluate({}, {})
        files = compile_bundle({}, result)
        self.assertEqual(json.loads(files['Execution_Graph.canvas'])['edges'], [])
        self.assertNotIn('biospub/handoff.json', files)

    def test_duplicate_json_keys_rejected(self):
        path = self.repo / 'duplicate.json'
        path.write_text('{"scope":1,"scope":2}')
        with self.assertRaises(ValueError):
            read_json(path)

    def test_graph_cannot_depend_on_future_outcome_bytes(self):
        self.payload['nodes'][0]['evidence_refs'] = ['OUTCOME']
        self.sign_all()
        self.assert_held()

    def test_unknown_field_cannot_inject_authority(self):
        self.payload['publish_now'] = True
        self.assert_held()

    def test_wrong_destination_receipt(self):
        self.packet['receipts'][-1]['body']['destination'] = 'Another destination'
        self.assert_held()

    def test_missing_preregistration(self):
        self.payload['trial']['preregistration_ref'] = 'ABSENT'
        self.sign_all()
        self.assert_held()

    def test_hold_cli_returns_two_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / 'packet.json').write_text('{}')
            (path / 'trust.json').write_text('{}')
            command = ['python', str(Path(__file__).with_name('workflow.py')),
                '--packet', str(path / 'packet.json'), '--trust-snapshot', str(path / 'trust.json'),
                '--staging-output', str(path / 'staging')]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 2)
            original = (path / 'staging' / 'report.json').read_bytes()
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(original, (path / 'staging' / 'report.json').read_bytes())

    def test_cli_rejects_detected_active_vault(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / '.obsidian').mkdir()
            (path / 'packet.json').write_text('{}')
            (path / 'trust.json').write_text('{}')
            result = subprocess.run(['python', str(Path(__file__).with_name('workflow.py')),
                '--packet', str(path / 'packet.json'), '--trust-snapshot', str(path / 'trust.json'),
                '--staging-output', str(path / 'staging')], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((path / 'staging').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
