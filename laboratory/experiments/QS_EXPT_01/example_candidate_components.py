"""
NON-SCIENTIFIC example components.
These exist only to demonstrate interface conformance.
They do not encode validated Sentinel predicates, JLK logic, or routing competence.
"""
from schemas import Coordinate, JLKLocalization, RoutingProposal, SentinelWitness
from diagnostic_interfaces import JLKKernel, RoutingSelector, SentinelDiscriminator


class AbstainingSentinel(SentinelDiscriminator):
    def discriminate(self, trace):
        return SentinelWitness(
            trial_id=trace.trial_id,
            coordinate_hypothesis=None,
            confidence=None,
            abstain=True,
            rationale_code="NO_VALIDATED_PREDICATE",
        )


class AbstainingJLK(JLKKernel):
    def localize(self, trace, witness):
        return JLKLocalization(
            trial_id=trace.trial_id,
            jurisdiction_hypothesis=None,
            boundary_descriptor={},
            abstain=True,
            rationale_code="NO_VALIDATED_LOCALIZER",
        )


class AbstainingRouter(RoutingSelector):
    def propose(self, trace, witness, localization):
        return RoutingProposal(
            trial_id=trace.trial_id,
            apparatus_id=None,
            abstain=True,
            rationale_code="NO_VALIDATED_ROUTING_RULE",
        )
