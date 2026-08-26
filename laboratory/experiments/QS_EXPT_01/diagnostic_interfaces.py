from __future__ import annotations

from abc import ABC, abstractmethod

from schemas import BlindTrace, JLKLocalization, RoutingProposal, SentinelWitness


class SentinelDiscriminator(ABC):
    """Receives blind trace only. No truth record is accepted by this interface."""

    @abstractmethod
    def discriminate(self, trace: BlindTrace) -> SentinelWitness:
        raise NotImplementedError


class JLKKernel(ABC):
    """Localizes from blind trace + sentinel witness. No truth record is accepted."""

    @abstractmethod
    def localize(self, trace: BlindTrace, witness: SentinelWitness) -> JLKLocalization:
        raise NotImplementedError


class RoutingSelector(ABC):
    """Proposes apparatus only. Has no execution method or runtime handle."""

    @abstractmethod
    def propose(self, trace: BlindTrace, witness: SentinelWitness, localization: JLKLocalization) -> RoutingProposal:
        raise NotImplementedError
