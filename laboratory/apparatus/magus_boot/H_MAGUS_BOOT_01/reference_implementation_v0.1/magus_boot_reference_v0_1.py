#!/usr/bin/env python3
"""
MAGUS_BOOT_REFERENCE_IMPLEMENTATION_v0.1

STATUS:
    MATERIALIZED / UNEXECUTED

PURPOSE:
    Pure reference implementation of the five-stage MAGUS foreign-corpus
    boot membrane:

        F -> I -> G -> J -> O

CONSTITUTIONAL BOUNDARIES:
    - This module does not execute host actions.
    - This module does not modify fixture bytes.
    - This module does not repair missing data.
    - This module does not infer missing dependencies or authority.
    - This module does not self-author execution jurisdiction.
    - This module does not contain the frozen expected-outcome oracle.
    - Materialization of this code does not authorize execution.

RESULT DOMAIN:
    Stage standing: 1 | 0 | X
      1 = resolved/conforming
      0 = unresolved/incomplete
      X = contradiction

    Boot state:
      ORIENTED
      ORIENTATION_INCOMPLETE
      CONSTITUTIONAL_CONTRADICTION
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Mapping, Optional, Sequence, Tuple
import hashlib
import json

StageValue = Literal["1", "0", "X"]
BootState = Literal[
    "ORIENTED",
    "ORIENTATION_INCOMPLETE",
    "CONSTITUTIONAL_CONTRADICTION",
]

ALLOWED_STAGE_VALUES = {"1", "0", "X"}
EXECUTION_AUTHORITY_ALWAYS_LATENT = True


@dataclass(frozen=True)
class StageReceipt:
    stage: str
    standing: StageValue
    reasons: Tuple[str, ...] = ()
    evidence_refs: Tuple[str, ...] = ()


@dataclass(frozen=True)
class OrientationManifold:
    field: Optional[str]
    jurisdiction: Optional[str]
    environment: Optional[str]
    state: Optional[str]
    dependencies: Tuple[str, ...]
    admissible_actions: Tuple[str, ...]

    def complete(self) -> bool:
        return all([
            bool(self.field),
            bool(self.jurisdiction),
            bool(self.environment),
            bool(self.state),
            self.dependencies is not None,
            self.admissible_actions is not None,
        ])


@dataclass(frozen=True)
class BootReceipt:
    corpus_root: str
    substance: StageReceipt
    identity: StageReceipt
    topology: StageReceipt
    governance: StageReceipt
    orientation: StageReceipt
    outcome: BootState
    v_magus: int
    j_ex: str = "LATENT"

    def vector(self) -> Tuple[StageValue, StageValue, StageValue, StageValue, StageValue]:
        return (
            self.substance.standing,
            self.identity.standing,
            self.topology.standing,
            self.governance.standing,
            self.orientation.standing,
        )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def load_json_readonly(path: Path) -> Any:
    with path.open("rb") as f:
        raw = f.read()
    return json.loads(raw.decode("utf-8"))


def safe_relpaths(root: Path) -> Tuple[str, ...]:
    """
    Enumerate paths without executing or importing corpus contents.
    Symlinks are reported as paths and never followed here.
    """
    paths: List[str] = []
    for p in sorted(root.rglob("*")):
        try:
            rel = p.relative_to(root).as_posix()
        except ValueError:
            continue
        paths.append(rel)
    return tuple(paths)


def classify_path(relpath: str) -> str:
    """
    Syntactic/structural classification only.
    Unknown forms remain UNKNOWN; no semantic fallback is permitted.
    """
    p = relpath.lower()
    name = Path(relpath).name.lower()

    if relpath.startswith(".digisleuth/"):
        return "CONSTITUTIVE"
    if "schema" in p or p.endswith(".schema.json"):
        return "SCHEMA"
    if "state" in p or name.endswith(".jsonl"):
        return "STATE"
    if "manifest" in p or "lineage" in p or "merkle" in p:
        return "LINEAGE"
    if p.endswith((".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".wasm", ".bin")):
        return "RUNTIME"
    if p.endswith((".md", ".txt", ".json", ".yaml", ".yml", ".toml")):
        return "DECLARED_DATA"
    return "UNKNOWN"


def stage_F_substance_partition(corpus_root: Path) -> StageReceipt:
    if not corpus_root.exists() or not corpus_root.is_dir():
        return StageReceipt("F", "0", ("CORPUS_ROOT_ABSENT",))

    relpaths = safe_relpaths(corpus_root)
    if not relpaths:
        return StageReceipt("F", "0", ("CORPUS_EMPTY",))

    unknown = tuple(p for p in relpaths if Path(corpus_root / p).is_file() and classify_path(p) == "UNKNOWN")
    reasons: List[str] = []
    if unknown:
        reasons.append("UNCLASSIFIED_MATTER_PRESENT")

    # The partition stage can still be structurally present while unresolved
    # matter exists; unresolved matter must not be silently reclassified.
    standing: StageValue = "0" if unknown else "1"
    return StageReceipt("F", standing, tuple(reasons), relpaths)


def _manifest_candidates(corpus_root: Path) -> Tuple[Path, ...]:
    names = (
        ".digisleuth/root_manifest.json",
        ".digisleuth/manifest.json",
        "manifests/root_manifest.json",
        "root_manifest.json",
    )
    return tuple(corpus_root / n for n in names if (corpus_root / n).is_file())


def _verify_declared_file_hashes(corpus_root: Path, manifest: Mapping[str, Any]) -> StageReceipt:
    entries = manifest.get("files")
    if not isinstance(entries, list):
        return StageReceipt("I", "0", ("IDENTITY_FILE_TABLE_MISSING",))

    refs: List[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            return StageReceipt("I", "X", ("MALFORMED_IDENTITY_ENTRY",))
        rel = entry.get("path")
        declared = entry.get("sha256")
        if not isinstance(rel, str) or not isinstance(declared, str):
            return StageReceipt("I", "X", ("MALFORMED_IDENTITY_ENTRY",))

        target = corpus_root / rel
        refs.append(rel)
        if not target.is_file():
            return StageReceipt("I", "0", ("DECLARED_FILE_ABSENT",), tuple(refs))

        observed = sha256_file(target)
        if observed.lower() != declared.lower():
            return StageReceipt("I", "X", ("DIGEST_MISMATCH",), tuple(refs))

    parent = manifest.get("parent_manifest")
    if parent is not None:
        if not isinstance(parent, dict):
            return StageReceipt("I", "X", ("MALFORMED_PARENT_POINTER",), tuple(refs))
        parent_path = parent.get("path")
        parent_hash = parent.get("sha256")
        if not isinstance(parent_path, str) or not isinstance(parent_hash, str):
            return StageReceipt("I", "X", ("MALFORMED_PARENT_POINTER",), tuple(refs))
        pp = corpus_root / parent_path
        refs.append(parent_path)
        if not pp.is_file():
            return StageReceipt("I", "0", ("PARENT_MANIFEST_ABSENT",), tuple(refs))
        if sha256_file(pp).lower() != parent_hash.lower():
            return StageReceipt("I", "X", ("PARENT_POINTER_DIVERGENCE",), tuple(refs))

    return StageReceipt("I", "1", (), tuple(refs))


def stage_I_identity_verification(corpus_root: Path) -> StageReceipt:
    manifests = _manifest_candidates(corpus_root)
    if not manifests:
        return StageReceipt("I", "0", ("ROOT_MANIFEST_MISSING",))

    # More than one root identity surface is not automatically contradictory.
    # The implementation chooses the first canonical location in the frozen
    # search order and reports the selected path.
    manifest_path = manifests[0]
    try:
        manifest = load_json_readonly(manifest_path)
    except Exception:
        return StageReceipt("I", "X", ("ROOT_MANIFEST_UNREADABLE_OR_INVALID_JSON",), (manifest_path.name,))

    if not isinstance(manifest, dict):
        return StageReceipt("I", "X", ("ROOT_MANIFEST_NOT_OBJECT",), (manifest_path.name,))

    receipt = _verify_declared_file_hashes(corpus_root, manifest)
    return StageReceipt(
        "I",
        receipt.standing,
        receipt.reasons,
        (manifest_path.relative_to(corpus_root).as_posix(),) + receipt.evidence_refs,
    )


def _topology_candidates(corpus_root: Path) -> Tuple[Path, ...]:
    names = (
        ".digisleuth/topology.json",
        "topology/dependencies.json",
        "topology/graph.json",
    )
    return tuple(corpus_root / n for n in names if (corpus_root / n).is_file())


def stage_G_topology_mapping(corpus_root: Path) -> StageReceipt:
    candidates = _topology_candidates(corpus_root)
    if not candidates:
        return StageReceipt("G", "0", ("TOPOLOGY_DECLARATION_MISSING",))

    path = candidates[0]
    try:
        doc = load_json_readonly(path)
    except Exception:
        return StageReceipt("G", "X", ("TOPOLOGY_UNREADABLE_OR_INVALID_JSON",), (path.relative_to(corpus_root).as_posix(),))

    if not isinstance(doc, dict):
        return StageReceipt("G", "X", ("TOPOLOGY_NOT_OBJECT",), (path.relative_to(corpus_root).as_posix(),))

    nodes = doc.get("nodes")
    edges = doc.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return StageReceipt("G", "0", ("TOPOLOGY_NODES_OR_EDGES_MISSING",), (path.relative_to(corpus_root).as_posix(),))

    node_ids = set()
    for n in nodes:
        if isinstance(n, str):
            node_ids.add(n)
        elif isinstance(n, dict) and isinstance(n.get("id"), str):
            node_ids.add(n["id"])
        else:
            return StageReceipt("G", "X", ("MALFORMED_NODE_DECLARATION",), (path.relative_to(corpus_root).as_posix(),))

    missing: List[str] = []
    for e in edges:
        if not isinstance(e, dict):
            return StageReceipt("G", "X", ("MALFORMED_EDGE_DECLARATION",), (path.relative_to(corpus_root).as_posix(),))
        src, dst = e.get("from"), e.get("to")
        if not isinstance(src, str) or not isinstance(dst, str):
            return StageReceipt("G", "X", ("MALFORMED_EDGE_ENDPOINT",), (path.relative_to(corpus_root).as_posix(),))
        if src not in node_ids:
            missing.append(src)
        if dst not in node_ids:
            missing.append(dst)

    if missing:
        return StageReceipt(
            "G",
            "0",
            ("MISSING_DECLARED_DEPENDENCY",),
            tuple(sorted(set(missing))),
        )

    return StageReceipt("G", "1", (), (path.relative_to(corpus_root).as_posix(),))


def _governance_candidates(corpus_root: Path) -> Tuple[Path, ...]:
    names = (
        ".digisleuth/authority_lease.json",
        ".digisleuth/governance.json",
        "manifests/authority_lease.json",
        "governance/authority_lease.json",
    )
    return tuple(corpus_root / n for n in names if (corpus_root / n).is_file())


def _kernel_anchor_candidates(corpus_root: Path) -> Tuple[Path, ...]:
    names = (
        ".digisleuth/kernel_anchor.json",
        "manifests/kernel_anchor.json",
        "governance/kernel_anchor.json",
    )
    return tuple(corpus_root / n for n in names if (corpus_root / n).is_file())


def stage_J_governance_binding(corpus_root: Path) -> StageReceipt:
    anchors = _kernel_anchor_candidates(corpus_root)
    leases = _governance_candidates(corpus_root)

    if not anchors or not leases:
        return StageReceipt("J", "0", ("KERNEL_ANCHOR_OR_AUTHORITY_LEASE_MISSING",))

    anchor_path, lease_path = anchors[0], leases[0]

    try:
        anchor = load_json_readonly(anchor_path)
        lease = load_json_readonly(lease_path)
    except Exception:
        return StageReceipt(
            "J", "X",
            ("GOVERNANCE_ARTIFACT_UNREADABLE_OR_INVALID_JSON",),
            (anchor_path.relative_to(corpus_root).as_posix(),
             lease_path.relative_to(corpus_root).as_posix()),
        )

    if not isinstance(anchor, dict) or not isinstance(lease, dict):
        return StageReceipt("J", "X", ("GOVERNANCE_ARTIFACT_NOT_OBJECT",))

    # Explicit local sovereignty is constitutionally contradictory.
    sovereignty_flags = (
        lease.get("self_sovereign"),
        lease.get("local_sovereignty"),
        lease.get("may_expand_own_authority"),
        lease.get("habitat_authority_source"),
    )
    if any(v is True for v in sovereignty_flags[:3]) or sovereignty_flags[3] == "local":
        return StageReceipt(
            "J", "X",
            ("LOCAL_SOVEREIGNTY_ASSERTION",),
            (lease_path.relative_to(corpus_root).as_posix(),),
        )

    expected_anchor = lease.get("kernel_anchor_sha256")
    actual_anchor = anchor.get("kernel_sha256") or anchor.get("sha256")
    if not isinstance(expected_anchor, str) or not isinstance(actual_anchor, str):
        return StageReceipt("J", "0", ("KERNEL_ANCHOR_BINDING_INCOMPLETE",))

    if expected_anchor.lower() != actual_anchor.lower():
        return StageReceipt("J", "X", ("UPSTREAM_KERNEL_ANCHOR_MISMATCH",))

    # Reference implementation intentionally does not invent cryptographic
    # verification semantics. A lease must explicitly identify a verification
    # method and expose a boolean verification result produced by the frozen
    # fixture's declared mechanism. Missing verification remains unresolved.
    method = lease.get("signature_method")
    verified = lease.get("signature_verified")
    if not isinstance(method, str) or verified is not True:
        return StageReceipt("J", "0", ("AUTHORITY_LEASE_NOT_VERIFIED",))

    return StageReceipt(
        "J", "1", (),
        (anchor_path.relative_to(corpus_root).as_posix(),
         lease_path.relative_to(corpus_root).as_posix()),
    )


def _orientation_candidates(corpus_root: Path) -> Tuple[Path, ...]:
    names = (
        ".digisleuth/orientation.json",
        "state/orientation.json",
        "manifests/orientation.json",
    )
    return tuple(corpus_root / n for n in names if (corpus_root / n).is_file())


def stage_O_orientation_assembly(
    corpus_root: Path,
    upstream: Sequence[StageReceipt],
) -> StageReceipt:
    # Any unresolved or contradictory prerequisite prevents orientation
    # from being represented as complete.
    if any(r.standing != "1" for r in upstream):
        return StageReceipt("O", "0", ("UPSTREAM_ORIENTATION_PREREQUISITE_UNRESOLVED",))

    candidates = _orientation_candidates(corpus_root)
    if not candidates:
        return StageReceipt("O", "0", ("ORIENTATION_MANIFEST_MISSING",))

    path = candidates[0]
    try:
        doc = load_json_readonly(path)
    except Exception:
        return StageReceipt("O", "X", ("ORIENTATION_MANIFEST_INVALID",))

    if not isinstance(doc, dict):
        return StageReceipt("O", "X", ("ORIENTATION_MANIFEST_NOT_OBJECT",))

    deps = doc.get("dependencies")
    actions = doc.get("admissible_actions")

    if deps is None:
        deps_tuple: Tuple[str, ...] = ()
    elif isinstance(deps, list) and all(isinstance(x, str) for x in deps):
        deps_tuple = tuple(deps)
    else:
        return StageReceipt("O", "X", ("ORIENTATION_DEPENDENCIES_MALFORMED",))

    if actions is None:
        actions_tuple: Tuple[str, ...] = ()
    elif isinstance(actions, list) and all(isinstance(x, str) for x in actions):
        actions_tuple = tuple(actions)
    else:
        return StageReceipt("O", "X", ("ORIENTATION_ACTIONS_MALFORMED",))

    manifold = OrientationManifold(
        field=doc.get("field") if isinstance(doc.get("field"), str) else None,
        jurisdiction=doc.get("jurisdiction") if isinstance(doc.get("jurisdiction"), str) else None,
        environment=doc.get("environment") if isinstance(doc.get("environment"), str) else None,
        state=doc.get("state") if isinstance(doc.get("state"), str) else None,
        dependencies=deps_tuple,
        admissible_actions=actions_tuple,
    )

    if not manifold.complete():
        return StageReceipt("O", "0", ("ORIENTATION_COORDINATE_INCOMPLETE",))

    return StageReceipt("O", "1", (), (path.relative_to(corpus_root).as_posix(),))


def adjudicate_vector(vector: Sequence[StageValue]) -> Tuple[BootState, int]:
    """
    Frozen algebraic evaluator:
        X precedence > 0 > 1

    This is the codomain reducer only. It contains no per-fixture expected
    outcomes and no fixture identities.
    """
    if any(v not in ALLOWED_STAGE_VALUES for v in vector):
        raise ValueError("Invalid stage standing outside {1,0,X}")
    if "X" in vector:
        return "CONSTITUTIONAL_CONTRADICTION", 0
    if "0" in vector:
        return "ORIENTATION_INCOMPLETE", 0
    return "ORIENTED", 1


def boot_corpus(corpus_root: Path) -> BootReceipt:
    """
    Pure read-only boot evaluation.

    No writes are performed.
    No repair is attempted.
    No execution authority is emitted.
    """
    corpus_root = corpus_root.resolve()

    f = stage_F_substance_partition(corpus_root)
    i = stage_I_identity_verification(corpus_root)
    g = stage_G_topology_mapping(corpus_root)
    j = stage_J_governance_binding(corpus_root)
    o = stage_O_orientation_assembly(corpus_root, (f, i, g, j))

    vector = (f.standing, i.standing, g.standing, j.standing, o.standing)
    outcome, v_magus = adjudicate_vector(vector)

    return BootReceipt(
        corpus_root=str(corpus_root),
        substance=f,
        identity=i,
        topology=g,
        governance=j,
        orientation=o,
        outcome=outcome,
        v_magus=v_magus,
        j_ex="LATENT",
    )


def receipt_to_dict(receipt: BootReceipt) -> Dict[str, Any]:
    def sr(x: StageReceipt) -> Dict[str, Any]:
        return {
            "stage": x.stage,
            "standing": x.standing,
            "reasons": list(x.reasons),
            "evidence_refs": list(x.evidence_refs),
        }

    return {
        "corpus_root": receipt.corpus_root,
        "vector": list(receipt.vector()),
        "outcome": receipt.outcome,
        "V_MAGUS": receipt.v_magus,
        "J_EX": receipt.j_ex,
        "stages": {
            "F": sr(receipt.substance),
            "I": sr(receipt.identity),
            "G": sr(receipt.topology),
            "J": sr(receipt.governance),
            "O": sr(receipt.orientation),
        },
    }


if __name__ == "__main__":
    raise SystemExit(
        "MAGUS_BOOT_REFERENCE_IMPLEMENTATION_v0.1 is MATERIALIZED_UNEXECUTED. "
        "No CLI execution surface is authorized in this artifact."
    )
