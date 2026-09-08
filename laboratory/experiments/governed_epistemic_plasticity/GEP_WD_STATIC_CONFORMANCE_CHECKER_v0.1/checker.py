from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Mapping, Sequence


class Disposition(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    UNRESOLVED = "UNRESOLVED"


COORDINATES = (
    "rule_identity",
    "rule_version",
    "input_binding",
    "source_cone_binding",
    "assumptions",
    "scope",
    "jurisdiction",
    "epoch",
    "issuer",
    "provenance",
)


@dataclass(frozen=True)
class ValidationPolicy:
    """Frozen semantics supplied upstream of fixtures.

    The checker only compares a warrant against this policy. It does not repair,
    infer lineage, assign standing, admit relations, or mutate topology.
    """

    allowed_rule_ids: Sequence[str]
    allowed_rule_versions: Mapping[str, Sequence[str]]
    known_input_ids: Sequence[str]
    valid_source_cones: Mapping[str, Sequence[str]]
    allowed_scopes: Sequence[str]
    allowed_jurisdictions: Sequence[str]
    allowed_epochs: Sequence[str]
    authorized_issuers: Sequence[str]
    required_provenance_fields: Sequence[str] = (
        "artifact_id",
        "content_hash",
        "replay_ref",
    )


@dataclass(frozen=True)
class CoordinateResult:
    disposition: Disposition
    violations: Sequence[str]


@dataclass(frozen=True)
class VerificationResult:
    warrant_id: str
    result: Disposition
    coordinates: Mapping[str, str]
    violations: Sequence[str]
    repair_authority: bool = False
    admission_authority: bool = False
    epistemic_standing_effect: str = "NONE"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _missing(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _combine(results: Mapping[str, CoordinateResult]) -> Disposition:
    dispositions = {r.disposition for r in results.values()}
    if Disposition.INVALID in dispositions:
        return Disposition.INVALID
    if Disposition.UNRESOLVED in dispositions:
        return Disposition.UNRESOLVED
    return Disposition.VALID


def _one(disposition: Disposition, *violations: str) -> CoordinateResult:
    return CoordinateResult(disposition, tuple(v for v in violations if v))


def verify_warrant(warrant: Mapping[str, Any], policy: ValidationPolicy) -> VerificationResult:
    """Static conformance check for W_D.

    Expected W_D identity vector:
      <I_R, V_R, I_inputs, I_SC, A, S, J, E, I_issuer, P>

    Missing/authentication-unknown data => UNRESOLVED.
    Demonstrated semantic violation => INVALID.
    VALID => structurally/semantically conformant only; never admission.
    """

    results: Dict[str, CoordinateResult] = {}
    warrant_id = str(warrant.get("warrant_id") or "UNIDENTIFIED_WARRANT")

    rule_id = warrant.get("rule_id")
    if _missing(rule_id):
        results["rule_identity"] = _one(Disposition.UNRESOLVED, "RULE_ID_MISSING")
    elif rule_id not in policy.allowed_rule_ids:
        results["rule_identity"] = _one(Disposition.INVALID, "RULE_ID_UNAUTHORIZED")
    else:
        results["rule_identity"] = _one(Disposition.VALID)

    rule_version = warrant.get("rule_version")
    if _missing(rule_version):
        results["rule_version"] = _one(Disposition.UNRESOLVED, "RULE_VERSION_MISSING")
    elif _missing(rule_id) or rule_id not in policy.allowed_rule_versions:
        results["rule_version"] = _one(Disposition.UNRESOLVED, "RULE_VERSION_BINDING_UNRESOLVED")
    elif rule_version not in policy.allowed_rule_versions[rule_id]:
        results["rule_version"] = _one(Disposition.INVALID, "RULE_VERSION_UNAUTHORIZED")
    else:
        results["rule_version"] = _one(Disposition.VALID)

    inputs = warrant.get("input_ids")
    if _missing(inputs):
        results["input_binding"] = _one(Disposition.UNRESOLVED, "INPUT_BINDING_MISSING")
    elif not isinstance(inputs, list) or not all(isinstance(x, str) and x for x in inputs):
        results["input_binding"] = _one(Disposition.INVALID, "INPUT_BINDING_MALFORMED")
    elif len(set(inputs)) != len(inputs):
        results["input_binding"] = _one(Disposition.INVALID, "INPUT_BINDING_DUPLICATE_IDENTITY")
    elif any(x not in policy.known_input_ids for x in inputs):
        results["input_binding"] = _one(Disposition.UNRESOLVED, "INPUT_ID_AUTHENTICATION_UNRESOLVED")
    else:
        results["input_binding"] = _one(Disposition.VALID)

    source_cone_id = warrant.get("source_cone_id")
    if _missing(source_cone_id):
        results["source_cone_binding"] = _one(Disposition.UNRESOLVED, "SOURCE_CONE_ID_MISSING")
    elif source_cone_id not in policy.valid_source_cones:
        results["source_cone_binding"] = _one(Disposition.UNRESOLVED, "SOURCE_CONE_AUTHENTICATION_UNRESOLVED")
    elif not isinstance(inputs, list):
        results["source_cone_binding"] = _one(Disposition.UNRESOLVED, "SOURCE_CONE_INPUT_BINDING_UNRESOLVED")
    elif results["input_binding"].disposition == Disposition.UNRESOLVED:
        results["source_cone_binding"] = _one(Disposition.UNRESOLVED, "SOURCE_CONE_INPUT_AUTHENTICATION_UNRESOLVED")
    elif results["input_binding"].disposition == Disposition.INVALID:
        results["source_cone_binding"] = _one(Disposition.UNRESOLVED, "SOURCE_CONE_INPUT_BINDING_INVALID_UPSTREAM")
    else:
        expected = tuple(policy.valid_source_cones[source_cone_id])
        actual = tuple(inputs)
        if actual != expected:
            results["source_cone_binding"] = _one(Disposition.INVALID, "SOURCE_CONE_BINDING_MISMATCH")
        else:
            results["source_cone_binding"] = _one(Disposition.VALID)

    assumptions = warrant.get("assumptions")
    if assumptions is None:
        results["assumptions"] = _one(Disposition.UNRESOLVED, "ASSUMPTIONS_MISSING")
    elif not isinstance(assumptions, list) or not all(isinstance(x, str) and x for x in assumptions):
        results["assumptions"] = _one(Disposition.INVALID, "ASSUMPTIONS_MALFORMED")
    elif any(x.strip().upper() in {"TBD", "UNKNOWN", "INFER"} for x in assumptions):
        results["assumptions"] = _one(Disposition.UNRESOLVED, "ASSUMPTION_UNRESOLVED")
    else:
        results["assumptions"] = _one(Disposition.VALID)

    scope = warrant.get("scope")
    if _missing(scope):
        results["scope"] = _one(Disposition.UNRESOLVED, "SCOPE_MISSING")
    elif scope not in policy.allowed_scopes:
        results["scope"] = _one(Disposition.INVALID, "SCOPE_EXCEEDED")
    else:
        results["scope"] = _one(Disposition.VALID)

    jurisdiction = warrant.get("jurisdiction")
    if _missing(jurisdiction):
        results["jurisdiction"] = _one(Disposition.UNRESOLVED, "JURISDICTION_MISSING")
    elif jurisdiction not in policy.allowed_jurisdictions:
        results["jurisdiction"] = _one(Disposition.INVALID, "JURISDICTION_MISMATCH")
    else:
        results["jurisdiction"] = _one(Disposition.VALID)

    epoch = warrant.get("epoch")
    if _missing(epoch):
        results["epoch"] = _one(Disposition.UNRESOLVED, "EPOCH_MISSING")
    elif epoch not in policy.allowed_epochs:
        results["epoch"] = _one(Disposition.INVALID, "EPOCH_OUT_OF_BOUNDS")
    else:
        results["epoch"] = _one(Disposition.VALID)

    issuer = warrant.get("issuer_id")
    if _missing(issuer):
        results["issuer"] = _one(Disposition.UNRESOLVED, "ISSUER_MISSING")
    elif issuer not in policy.authorized_issuers:
        results["issuer"] = _one(Disposition.INVALID, "ISSUER_UNAUTHORIZED")
    else:
        results["issuer"] = _one(Disposition.VALID)

    provenance = warrant.get("provenance")
    if _missing(provenance):
        results["provenance"] = _one(Disposition.UNRESOLVED, "PROVENANCE_MISSING")
    elif not isinstance(provenance, dict):
        results["provenance"] = _one(Disposition.INVALID, "PROVENANCE_MALFORMED")
    else:
        missing_fields = [f for f in policy.required_provenance_fields if _missing(provenance.get(f))]
        if missing_fields:
            results["provenance"] = _one(
                Disposition.UNRESOLVED,
                *[f"PROVENANCE_FIELD_MISSING:{f}" for f in missing_fields],
            )
        else:
            results["provenance"] = _one(Disposition.VALID)

    overall = _combine(results)
    violations: List[str] = []
    for coordinate in COORDINATES:
        violations.extend(results[coordinate].violations)

    return VerificationResult(
        warrant_id=warrant_id,
        result=overall,
        coordinates={k: results[k].disposition.value for k in COORDINATES},
        violations=tuple(violations),
        repair_authority=False,
        admission_authority=False,
        epistemic_standing_effect="NONE",
    )
