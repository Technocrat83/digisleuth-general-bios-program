from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from adjudicator import adjudicate
from diagnostic_interfaces import JLKKernel, RoutingSelector, SentinelDiscriminator
from schemas import BlindTrace, DiagnosticTuple, SealedTruthRecord, TrialAdjudication


@dataclass(frozen=True)
class BlindDiagnosticHarness:
    sentinel: SentinelDiscriminator
    jlk: JLKKernel
    router: RoutingSelector

    def run_blind(self, trace: BlindTrace) -> DiagnosticTuple:
        witness = self.sentinel.discriminate(trace)
        localization = self.jlk.localize(trace, witness)
        proposal = self.router.propose(trace, witness, localization)
        return DiagnosticTuple(witness, localization, proposal)


@dataclass(frozen=True)
class IndependentAdjudicationChamber:
    apparatus_registry: Dict[str, str]

    def score(
        self,
        truth: SealedTruthRecord,
        diagnostic: DiagnosticTuple,
        *,
        taxonomy_distinctness_established_for_trial: bool = True,
        observation_resolution_sufficient: bool = True,
    ) -> TrialAdjudication:
        return adjudicate(
            truth,
            diagnostic,
            self.apparatus_registry,
            taxonomy_distinctness_established_for_trial=taxonomy_distinctness_established_for_trial,
            observation_resolution_sufficient=observation_resolution_sufficient,
        )
