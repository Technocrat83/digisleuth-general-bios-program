from __future__ import annotations

from typing import Dict

from schemas import (
    AdjudicationLabel,
    AxisAdjudication,
    DiagnosticTuple,
    FailureLocus,
    SealedTruthRecord,
    TrialAdjudication,
)


def _label_from_flags(*, abstain: bool, indeterminate: bool, match: bool, axis: str) -> AxisAdjudication:
    if abstain:
        return AxisAdjudication(AdjudicationLabel.ABSTAIN, f"{axis}: lawful abstention")
    if indeterminate:
        return AxisAdjudication(AdjudicationLabel.INDETERMINATE, f"{axis}: insufficient discriminative information")
    if match:
        return AxisAdjudication(AdjudicationLabel.CORRECT, f"{axis}: aligned with sealed truth")
    return AxisAdjudication(AdjudicationLabel.INCORRECT, f"{axis}: contradicted sealed truth")


def adjudicate(
    truth: SealedTruthRecord,
    diagnostic: DiagnosticTuple,
    apparatus_registry: Dict[str, str],
    *,
    taxonomy_distinctness_established_for_trial: bool = True,
    observation_resolution_sufficient: bool = True,
) -> TrialAdjudication:
    """
    Post-hoc chamber. This is the ONLY component that accepts sealed truth.

    apparatus_registry maps jurisdiction_target -> valid apparatus_id.
    It is used only to score R_proposal independently of JLK correctness.
    """
    s = diagnostic.sentinel
    j = diagnostic.jlk
    r = diagnostic.routing

    D_disc = _label_from_flags(
        abstain=s.abstain,
        indeterminate=s.indeterminate,
        match=s.coordinate_hypothesis == truth.coordinate,
        axis="D_disc",
    )

    L_JLK = _label_from_flags(
        abstain=j.abstain,
        indeterminate=j.indeterminate,
        match=j.jurisdiction_hypothesis == truth.jurisdiction_target,
        axis="L_JLK",
    )

    expected_apparatus = apparatus_registry.get(truth.jurisdiction_target)
    R_proposal = _label_from_flags(
        abstain=r.abstain,
        indeterminate=r.indeterminate,
        match=(expected_apparatus is not None and r.apparatus_id == expected_apparatus),
        axis="R_proposal",
    )

    failure_locus = None
    if not taxonomy_distinctness_established_for_trial:
        failure_locus = FailureLocus.TAXONOMY_FAILURE
    elif not observation_resolution_sufficient:
        failure_locus = FailureLocus.RESOLUTION_FAILURE
    elif any(x.label == AdjudicationLabel.INCORRECT for x in (D_disc, L_JLK, R_proposal)):
        failure_locus = FailureLocus.INSTRUMENT_FAILURE

    return TrialAdjudication(
        trial_id=truth.trial_id,
        D_disc=D_disc,
        L_JLK=L_JLK,
        R_proposal=R_proposal,
        failure_locus=failure_locus,
    )
