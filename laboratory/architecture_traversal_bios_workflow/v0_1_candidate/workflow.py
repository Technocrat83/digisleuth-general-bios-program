"""Offline candidate compiler. Stages files; no execution, activation or publishing."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Annotated, Literal

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pydantic import BaseModel, ConfigDict, Field

VERSION = 'DS_ATBR/0.1-candidate'
Text = Annotated[str, Field(min_length=1)]
SHA = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]
Commit = Annotated[str, Field(pattern=r'^[0-9a-f]{40}$')]
PREDICATES = ('precedes', 'eligible_after', 'requires', 'depends_on',
              'authorizes_definition_of', 'readable_by', 'mutable_by', 'prohibits',
              'cannot_repair', 'cannot_infer', 'blocks', 'jurisdiction_distinct_from',
              'produces', 'attests_to', 'does_not_imply')
GATES = {
    'UA_RECONCILIATION': 'semantic_reviewer',
    'THEOREM_ENTITLEMENT': 'theorem_adjudicator',
    'GRAPH_CERTIFICATION': 'certifier',
    'GRAPH_ADMISSION': 'kernel',
    'EXECUTION_AUTHORIZATION': 'runtime_authorizer',
    'TRANSFORMATION_WITNESS': 'observer',
    'PRODUCT_QUALIFICATION': 'product_reviewer',
    'COMMERCIALIZATION_AUTHORIZATION': 'commercialization_authorizer',
    'EDITORIAL_PREPARATION': 'editorial_authorizer',
    'CLAIM_APPROVAL': 'claim_reviewer',
}


class Closed(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class Source(Closed):
    source_id: Text
    file_path: Text
    blob_sha256: SHA
    line_start: Annotated[int, Field(ge=1)]
    line_end: Annotated[int, Field(ge=1)]


class UABinding(Closed):
    raw_export_sha256: SHA
    producer_revision: Commit
    source_commit: Commit
    scope_sha256: SHA


class Theorem(Closed):
    theorem_id: Text
    proposition: Text
    proposition_sha256: SHA
    assumptions: Annotated[list[Text], Field(min_length=1)]
    representation_domain: Text
    jurisdiction: Text
    derivation_ref: Text
    applicability_ref: Text
    provenance_ref: Text
    abstention_ref: Text
    falsification_protocol_ref: Text
    result: Literal['SATISFIED', 'FAILED', 'UNRESOLVED']
    obligations: dict[str, Literal['SATISFIED', 'FAILED', 'UNRESOLVED']]
    unresolved_contradictions: Annotated[int, Field(ge=0)]
    limitation: Text


class Node(Closed):
    object_id: Annotated[str, Field(pattern=r'^[A-Za-z0-9_-]+$')]
    object_class: Literal['STATE', 'TRANSFORMATION', 'EVIDENCE', 'AUTHORITY_REFERENCE']
    title: Text
    evidence_refs: Annotated[list[Text], Field(min_length=1)]


class Relation(Closed):
    relation_id: Annotated[str, Field(pattern=r'^[A-Za-z0-9_-]+$')]
    subject: Text
    object: Text
    relation_type: Text
    scope: Text
    evidence_refs: Annotated[list[Text], Field(min_length=1)]
    certainty: Literal['DECLARED_IN_SOURCE', 'SYNTACTICALLY_EXTRACTED', 'MODEL_INFERRED']
    schema_version: Literal['DS_ATBR/0.1-candidate']
    authority_id: Text
    admission_status: Literal['CANDIDATE']


class Claim(Closed):
    claim_id: Text
    text: Text
    classification: Literal['SUPPORTED', 'INFERRED', 'DISPUTED', 'UNRESOLVED']
    evidence_refs: Annotated[list[Text], Field(min_length=1)]
    rationale: Text
    limitation: Text


class Trial(Closed):
    preregistration_ref: Text
    outcome_evidence_ref: Text
    criteria: Annotated[list[Text], Field(min_length=1)]
    observation_scope: Text
    market_demand: Literal['NOT_ESTABLISHED', 'OBSERVED_WITHIN_DECLARED_TRIAL']


class Payload(Closed):
    schema_version: Literal['DS_ATBR/0.1-candidate']
    implementation_sha256: SHA
    run_id: Text
    transformation_id: Text
    producer_id: Text
    scope: Text
    source_repository: Text
    source_commit: Commit
    scope_paths: Annotated[list[Text], Field(min_length=1)]
    sources: Annotated[list[Source], Field(min_length=1)]
    outcome_commit: Commit
    outcome_sources: Annotated[list[Source], Field(min_length=1)]
    ua: UABinding
    theorem: Theorem
    trial: Trial
    nodes: Annotated[list[Node], Field(min_length=1)]
    relations: list[Relation]
    claims: Annotated[list[Claim], Field(min_length=1)]
    destination: Literal['Substack:DigiProse']
    audience: Text
    preparation_budget_ref: Text
    ceased: bool


class Decision(Closed):
    receipt_id: Text
    stage: Text
    run_id: Text
    transformation_id: Text
    payload_sha256: SHA
    decision: Literal['PASS', 'FAIL', 'UNRESOLVED']
    principal_id: Text
    authority_id: Text
    scope: Text
    destination: Text
    issued_at: Text
    expires_at: Text


class Receipt(Closed):
    body: Decision
    signature_base64: Text


class Packet(Closed):
    payload: Payload
    receipts: list[Receipt]


class TrustedKey(Closed):
    principal_id: Text
    roles: Annotated[list[Text], Field(min_length=1)]
    public_key_base64: Text


class TrustSnapshot(Closed):
    snapshot_id: Text
    valid_from: Text
    valid_until: Text
    keys: dict[str, TrustedKey]
    revoked_receipts: list[Text]


def canonical(value):
    """Local protocol encoding: sorted UTF-8 JSON, compact separators, no NaN."""
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def plan_digest(payload):
    """Earlier decisions bind the plan; later outcomes cannot alter that plan."""
    value = dict(payload)
    for key in ('outcome_commit', 'outcome_sources', 'claims'):
        value.pop(key)
    value['trial'] = {k: v for k, v in value['trial'].items()
                      if k not in ('outcome_evidence_ref', 'market_demand')}
    return digest(value)


def read_json(path):
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('Duplicate JSON key: ' + key)
            obj[key] = value
        return obj
    def bad_number(value):
        raise ValueError('Non-finite JSON value: ' + value)
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=bad_number)


def timestamp(text):
    value = datetime.fromisoformat(text.replace('Z', '+00:00'))
    if value.tzinfo is None:
        raise ValueError('Timestamp must include timezone')
    return value


def check_sources(p, source_root, ua_export):
    if not source_root or not ua_export:
        raise ValueError('Pinned Git checkout and preserved raw UA export are required')
    repo = Path(source_root).resolve()
    # Never run source-provided code. Read exact objects through Git only.
    origin = subprocess.check_output(['git', '-C', str(repo), 'remote', 'get-url', 'origin'],
                                     text=True).strip()
    expected = p.source_repository
    if origin not in ('https://github.com/' + expected + '.git',
                      'https://github.com/' + expected, 'git@github.com:' + expected + '.git'):
        raise ValueError('Repository origin identity mismatch')
    resolved = subprocess.check_output(['git', '-C', str(repo), 'rev-parse',
                                       p.source_commit + '^{commit}'], text=True).strip()
    if resolved != p.source_commit:
        raise ValueError('Commit mismatch')
    source_ids = [s.source_id for s in p.sources + p.outcome_sources]
    if len(source_ids) != len(set(source_ids)) or len(p.scope_paths) != len(set(p.scope_paths)):
        raise ValueError('Duplicate source IDs or scope paths')
    if set(p.scope_paths) != {s.file_path for s in p.sources}:
        raise ValueError('Scope must enumerate the exact inspected source paths')
    subprocess.check_output(['git', '-C', str(repo), 'rev-parse', p.outcome_commit + '^{commit}'])
    subprocess.check_call(['git', '-C', str(repo), 'merge-base', '--is-ancestor',
                           p.source_commit, p.outcome_commit])
    for source, commit in ([(s, p.source_commit) for s in p.sources] +
                           [(s, p.outcome_commit) for s in p.outcome_sources]):
        path = PurePosixPath(source.file_path)
        if path.is_absolute() or '..' in path.parts or '\\' in source.file_path:
            raise ValueError('Invalid source path')
        content = subprocess.check_output(['git', '-C', str(repo), 'show',
                                           commit + ':' + source.file_path])
        if hashlib.sha256(content).hexdigest() != source.blob_sha256:
            raise ValueError('Source byte digest mismatch: ' + source.source_id)
        if not 1 <= source.line_start <= source.line_end <= len(content.splitlines()):
            raise ValueError('Invalid source line bounds')
    if p.ua.source_commit != p.source_commit or p.ua.scope_sha256 != digest(p.scope_paths):
        raise ValueError('UA source/scope binding mismatch')
    if hashlib.sha256(Path(ua_export).read_bytes()).hexdigest() != p.ua.raw_export_sha256:
        raise ValueError('Raw UA export digest mismatch')
    # UA export is opaque. A separately signed reconciliation attests to mappings,
    # schema compatibility and losses; this compiler does not invent a UA adapter.
    return set(source_ids)


def check_semantics(p, source_ids):
    refs = lambda values: all(v in source_ids for v in values)
    plan_ids = {s.source_id for s in p.sources}
    t = p.theorem
    if hashlib.sha256(t.proposition.encode()).hexdigest() != t.proposition_sha256:
        raise ValueError('Immutable proposition digest mismatch')
    required = {'derivation', 'applicability', 'provenance', 'abstention'}
    if set(t.obligations) != required or any(v != 'SATISFIED' for v in t.obligations.values()):
        raise ValueError('Theorem obligations not satisfied')
    if t.result != 'SATISFIED' or t.unresolved_contradictions:
        raise ValueError('Theorem entitlement unresolved or contradicted')
    if not all(v in plan_ids for v in [t.derivation_ref, t.applicability_ref, t.provenance_ref,
                 t.abstention_ref, t.falsification_protocol_ref,
                 p.trial.preregistration_ref,
                 p.preparation_budget_ref]):
        raise ValueError('Proof, trial, or budget evidence reference does not resolve')
    if p.trial.outcome_evidence_ref not in {s.source_id for s in p.outcome_sources}:
        raise ValueError('Outcome evidence must bind separately captured post-run bytes')
    nodes = [n.object_id for n in p.nodes]
    rels = [r.relation_id for r in p.relations]
    claims = [c.claim_id for c in p.claims]
    if any(len(v) != len(set(v)) for v in [nodes, rels, claims]):
        raise ValueError('Duplicate graph or claim identity')
    for n in p.nodes:
        if not all(v in plan_ids for v in n.evidence_refs):
            raise ValueError('Unresolved node evidence')
    for r in p.relations:
        if r.subject not in nodes or r.object not in nodes or not all(v in plan_ids for v in r.evidence_refs):
            raise ValueError('Dangling relation or evidence')
        if r.relation_type not in PREDICATES or r.scope != p.scope:
            raise ValueError('Unmapped predicate or relation scope')
    if any(not refs(c.evidence_refs) for c in p.claims):
        raise ValueError('Unresolved claim evidence')


def evaluate(packet, trust, source_root=None, ua_export=None, now=None):
    now = now or datetime.now(timezone.utc)
    report = {'schema_version': VERSION, 'disposition': 'EXPLAINED_BLOCK',
              'projection_eligible': False, 'editorial_eligible': False,
              'external_publication_authority': False, 'real_execution_performed': False,
              'gates': {}, 'blockers': []}
    try:
        data = Packet.model_validate(packet)
        p = data.payload
        implementation_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        if p.implementation_sha256 != implementation_sha256:
            raise ValueError('Compiler implementation digest mismatch')
        report.update(run_id=p.run_id, payload_sha256=digest(p.model_dump()),
                      plan_sha256=plan_digest(p.model_dump()), implementation_sha256=implementation_sha256)
        if p.ceased:
            raise ValueError('CEASED: no further compilation')
        ids = check_sources(p, source_root, ua_export)
        check_semantics(p, ids)
        report['metrics'] = {
            'declared_scope_files': len(p.scope_paths),
            'byte_verified_scope_files': len({s.file_path for s in p.sources}),
            'graph_nodes': len(p.nodes), 'graph_relations': len(p.relations),
            'governance_coverage': None,
            'governance_coverage_reason': 'Protected-effect inventory and independent production observations not evaluated',
        }
        root = TrustSnapshot.model_validate(trust)
        if not timestamp(root.valid_from) <= now < timestamp(root.valid_until):
            raise ValueError('Trust/revocation snapshot is stale or not current')
        receipts = {}
        for receipt in data.receipts:
            b = receipt.body
            if b.stage not in GATES or b.stage in receipts:
                raise ValueError('Unknown or duplicate decision stage')
            key = root.keys.get(b.authority_id)
            if not key or GATES[b.stage] not in key.roles or key.principal_id != b.principal_id:
                raise ValueError('Authority identity/role mismatch')
            if b.principal_id == p.producer_id:
                raise ValueError('Producer cannot adjudicate its own packet')
            if b.receipt_id in root.revoked_receipts:
                raise ValueError('Receipt revoked')
            if not timestamp(b.issued_at) <= now < timestamp(b.expires_at):
                raise ValueError('Receipt expired or not yet valid')
            binding = report['plan_sha256'] if b.stage in list(GATES)[:5] else report['payload_sha256']
            expected = (p.run_id, p.transformation_id, binding, p.scope, p.destination)
            actual = (b.run_id, b.transformation_id, b.payload_sha256, b.scope, b.destination)
            if actual != expected:
                raise ValueError('Decision does not bind exact payload/scope/destination')
            public = Ed25519PublicKey.from_public_bytes(base64.b64decode(key.public_key_base64, validate=True))
            public.verify(base64.b64decode(receipt.signature_base64, validate=True), canonical(b.model_dump()))
            receipts[b.stage] = b
        previous = None
        for stage in GATES:
            b = receipts.get(stage)
            passed = b is not None and b.decision == 'PASS'
            if passed and previous and timestamp(b.issued_at) < timestamp(previous.issued_at):
                raise ValueError('Decision order violates workflow precedence')
            report['gates'][stage] = 'PASS' if passed else 'HOLD'
            if not passed:
                report['blockers'].append('Missing or non-PASS decision: ' + stage)
            if b:
                previous = b
        for a, b in [('THEOREM_ENTITLEMENT', 'GRAPH_CERTIFICATION'),
                     ('UA_RECONCILIATION', 'THEOREM_ENTITLEMENT'),
                     ('EXECUTION_AUTHORIZATION', 'TRANSFORMATION_WITNESS')]:
            if a in receipts and b in receipts and receipts[a].principal_id == receipts[b].principal_id:
                raise ValueError('Required independent principals collapse: ' + a + '/' + b)
        # A local offline receipt check is not a production commitment-time revocation check.
        report['projection_eligible'] = all(report['gates'][s] == 'PASS' for s in list(GATES)[:4])
        allowed_claims = [c for c in p.claims if c.classification in ('SUPPORTED', 'INFERRED')]
        report['editorial_eligible'] = all(v == 'PASS' for v in report['gates'].values()) and bool(allowed_claims)
        if not allowed_claims:
            report['blockers'].append('No claim eligible for editorial preparation')
        if report['editorial_eligible']:
            report['disposition'] = 'READY_FOR_REVIEW'
        report['trust_snapshot_id'] = root.snapshot_id
    except Exception as exc:
        report['projection_eligible'] = report['editorial_eligible'] = False
        report['blockers'].append(type(exc).__name__ + ': ' + str(exc))
    return report


def canvas_id(kind, identity):
    return hashlib.sha256((kind + ':' + identity).encode()).hexdigest()[:16]


def compile_bundle(packet, report):
    """Return exact staging bytes. No active manifest, vault or external API access."""
    files = {}
    canvas = {'nodes': [], 'edges': []}
    if report['projection_eligible']:
        p = Packet.model_validate(packet).payload
        for index, n in enumerate(p.nodes):
            name = 'notes/' + n.object_id + '.md'
            files[name] = ('---\nobject_id: ' + n.object_id + '\nstanding: ADMITTED_SOURCE_PROJECTION_CANDIDATE\n'
                           'object_class: ' + n.object_class + '\nauthority: ZERO\n---\n\n# ' + n.title + '\n\n' +
                           'Source payload: `' + report['payload_sha256'] + '`\n\n' +
                           'Source object and evidence:\n```json\n' + json.dumps(n.model_dump(), indent=2) + '\n```\n')
            outgoing = [r for r in p.relations if r.subject == n.object_id]
            if outgoing:
                files[name] += '\n## Admitted-source navigation\n\n' + '\n'.join(
                    '- ' + r.relation_type + ': [[' + r.object + ']] · ' + r.relation_id
                    for r in outgoing) + '\n'
            canvas['nodes'].append({'id': canvas_id('node', n.object_id), 'type': 'file',
                'file': name, 'x': (index % 3) * 440, 'y': (index // 3) * 300,
                'width': 360, 'height': 220})
        for r in p.relations:
            canvas['edges'].append({'id': canvas_id('relation', r.relation_id),
                'fromNode': canvas_id('node', r.subject), 'toNode': canvas_id('node', r.object),
                'toEnd': 'arrow', 'label': r.relation_type})
        files['relations.json'] = json.dumps({'source_records': [r.model_dump() for r in p.relations],
            'projection_basis': 'Externally signed exact-plan GRAPH_ADMISSION',
            'plan_sha256': report['plan_sha256'], 'payload_sha256': report['payload_sha256'],
            'activation_authority': 'NOT_ISSUED'}, indent=2) + '\n'
    else:
        files['notes/HOLD.md'] = ('---\nobject_id: WORKFLOW_HOLD\nstanding: HOLD\nauthority: ZERO\n---\n\n'
            '# Execution graph held\n\nNo admitted execution edges were compiled.\n\n' +
            '\n'.join('- ' + b for b in report['blockers']) + '\n')
        canvas['nodes'].append({'id': canvas_id('node', 'WORKFLOW_HOLD'), 'type': 'file',
            'file': 'notes/HOLD.md', 'x': 0, 'y': 0, 'width': 600, 'height': 380})
    files['Execution_Graph.canvas'] = json.dumps(canvas, indent=2) + '\n'
    files['report.json'] = json.dumps(report, indent=2) + '\n'
    if report['editorial_eligible']:
        p = Packet.model_validate(packet).payload
        claims = [c.model_dump() for c in p.claims if c.classification in ('SUPPORTED', 'INFERRED')]
        draft = '# ' + p.transformation_id + ': a bounded transformation\n\n'
        for c in claims:
            draft += ('**' + c['classification'] + ' · ' + c['claim_id'] + '**\n\n' +
                      c['text'] + '\n\nEvidence: ' + ', '.join(c['evidence_refs']) +
                      '.\n\nLimit: ' + c['limitation'] + '\n\n')
        draft += '## Trial scope\n\n' + p.trial.observation_scope + '\n\nMarket demand: ' + p.trial.market_demand + '\n'
        files['biospub/DigiProse_Draft.md'] = draft
        contents = {
            'source_record': {'source_commit': p.source_commit, 'sources': [s.model_dump() for s in p.sources],
                              'outcome_commit': p.outcome_commit, 'outcome_sources': [s.model_dump() for s in p.outcome_sources]},
            'claim_evidence_map': claims,
            'draft_asset': {'path': 'DigiProse_Draft.md', 'sha256': hashlib.sha256(draft.encode()).hexdigest(),
                            'destination': p.destination, 'audience': p.audience},
            'authority_record': {'verified_preparation_receipts': packet['receipts'],
                                  'external_publication_permission': 'NOT_GRANTED_BY_COMPILER'},
            'execution_receipt': {'kind': 'OFFLINE_COMPILATION', 'report': report,
                                   'transformation_execution_evidence': p.trial.outcome_evidence_ref,
                                   'observed_cost': 'UNAVAILABLE'},
            'disposition': {'value': 'READY_FOR_REVIEW', 'publisher_action': 'NONE',
                             'next': 'BIOSpub editorial review; separate exact-asset destination publication decision'},
        }
        package = {'package_id': p.run_id + ':BIOSPUB', 'package_revision': report['payload_sha256'],
                   'contract_ref': 'BIOS_PUBLICATION_HARNESS_CONTRACT_v0.1_candidate',
                   'implementation_ref': report['implementation_sha256'],
                   'interface_standing': 'CANDIDATE_NOT_BOUND_TO_LIVE_BIOSPUB', 'components': []}
        for kind, content in contents.items():
            package['components'].append({'record_id': p.run_id + ':' + kind, 'run_id': p.run_id,
                'component_type': kind, 'record_status': 'PRESENT', 'evidence_status': 'PARTIAL',
                'visibility_scope': p.audience, 'reason': 'Offline evidence-bound editorial preparation only',
                'content': content})
        files['biospub/handoff.json'] = json.dumps(package, indent=2) + '\n'
    else:
        files['biospub/queue.json'] = json.dumps({'status': 'HELD', 'successful_transformations': [],
            'reason': 'No transformation passed every preparation gate in this run'}, indent=2) + '\n'
    ids = [n['id'] for n in canvas['nodes']] + [e['id'] for e in canvas['edges']]
    if len(ids) != len(set(ids)):
        raise ValueError('Canvas identity collision')
    if report['projection_eligible']:
        targets = [{'relative_path': key, 'operation': 'CREATE_IF_ABSENT',
                    'size_bytes': len(value.encode()), 'sha256': hashlib.sha256(value.encode()).hexdigest()}
                   for key, value in sorted(files.items())
                   if key.startswith('notes/') or key in ('Execution_Graph.canvas', 'relations.json')]
        plan = {'standing': 'SEALED_STAGING_CANDIDATE_NOT_AUTHORIZED_FOR_ACTIVATION',
                'source_plan_sha256': report['plan_sha256'],
                'implementation_sha256': report['implementation_sha256'],
                'destination_vault': 'UNBOUND', 'writer_identity': 'UNBOUND',
                'kernel_projection_grant': None, 'targets': targets,
                'maximum_files': len(targets), 'maximum_bytes': sum(t['size_bytes'] for t in targets),
                'readback_witness': 'NOT_EXECUTED', 'activation_receipt': None}
        files['projection_plan.json'] = json.dumps({'plan': plan, 'plan_sha256': digest(plan)}, indent=2) + '\n'
    files['SHA256SUMS'] = ''.join(hashlib.sha256(value.encode()).hexdigest() + '  ' + key + '\n'
                                for key, value in sorted(files.items()))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', required=True)
    parser.add_argument('--trust-snapshot', required=True)
    parser.add_argument('--source-root')
    parser.add_argument('--ua-export')
    parser.add_argument('--staging-output', required=True,
                        help='New directory outside every active vault; no activation performed')
    args = parser.parse_args()
    packet, trust = read_json(args.packet), read_json(args.trust_snapshot)
    report = evaluate(packet, trust, args.source_root, args.ua_export)
    output = Path(args.staging_output).resolve()
    if any((parent / '.obsidian').exists() for parent in [output, *output.parents]):
        raise ValueError('Staging inside a detected Obsidian vault is prohibited')
    if args.source_root and output.is_relative_to(Path(args.source_root).resolve()):
        raise ValueError('Staging must remain outside the inspected Git checkout')
    output.mkdir(parents=True, exist_ok=False)
    for path, content in compile_bundle(packet, report).items():
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x', encoding='utf-8', newline='') as stream:
            stream.write(content)
    print(json.dumps(report, indent=2))
    return 0 if report['editorial_eligible'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
