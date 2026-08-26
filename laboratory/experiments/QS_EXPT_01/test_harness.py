from fixture_factory import PerturbationFixture, materialize_fixture
from example_candidate_components import AbstainingJLK, AbstainingRouter, AbstainingSentinel
from harness import BlindDiagnosticHarness, IndependentAdjudicationChamber
from schemas import AdjudicationLabel, Coordinate


def test_truth_is_not_required_by_blind_harness():
    fixture = PerturbationFixture(
        trial_id="T001",
        perturbation_id="P_CANON_001",
        coordinate=Coordinate.CANON,
        jurisdiction_target="J_CANON",
        runtime_input={"opaque": True},
        observable_trace={"latency_ms": 12.5, "error_code": "E7"},
    )
    truth, trace = materialize_fixture(fixture)

    harness = BlindDiagnosticHarness(AbstainingSentinel(), AbstainingJLK(), AbstainingRouter())
    diagnostic = harness.run_blind(trace)

    assert diagnostic.sentinel.trial_id == truth.trial_id
    assert diagnostic.sentinel.abstain is True


def test_three_axes_score_independently():
    fixture = PerturbationFixture(
        trial_id="T002",
        perturbation_id="P_EXEC_001",
        coordinate=Coordinate.EXECUTION,
        jurisdiction_target="J_EXEC",
        runtime_input={},
        observable_trace={"symptom": "proximal"},
    )
    truth, trace = materialize_fixture(fixture)
    harness = BlindDiagnosticHarness(AbstainingSentinel(), AbstainingJLK(), AbstainingRouter())
    diagnostic = harness.run_blind(trace)

    chamber = IndependentAdjudicationChamber({"J_EXEC": "APP_EXEC_DEEP"})
    result = chamber.score(truth, diagnostic)

    assert result.D_disc.label == AdjudicationLabel.ABSTAIN
    assert result.L_JLK.label == AdjudicationLabel.ABSTAIN
    assert result.R_proposal.label == AdjudicationLabel.ABSTAIN


def test_resolution_failure_is_distinct_from_instrument_failure():
    fixture = PerturbationFixture(
        trial_id="T003",
        perturbation_id="P_INFRA_001",
        coordinate=Coordinate.INFRASTRUCTURE,
        jurisdiction_target="J_INFRA",
        runtime_input={},
        observable_trace={"symptom": "ambiguous"},
    )
    truth, trace = materialize_fixture(fixture)
    harness = BlindDiagnosticHarness(AbstainingSentinel(), AbstainingJLK(), AbstainingRouter())
    diagnostic = harness.run_blind(trace)

    chamber = IndependentAdjudicationChamber({"J_INFRA": "APP_INFRA_DEEP"})
    result = chamber.score(truth, diagnostic, observation_resolution_sufficient=False)

    assert result.failure_locus.value == "RESOLUTION_FAILURE"
