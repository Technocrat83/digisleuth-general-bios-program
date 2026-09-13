from __future__ import annotations

from .haptics import HapticDispatcher
from .types import (
    DispatchResult,
    DispatchStanding,
    EstimateStanding,
    FoldState,
    HapticCommand,
    HapticPattern,
    LensDecision,
    OrientationEstimate,
)


LENSES = {
    FoldState.FLAT_UNFOLDED: "DUAL_STANZA_EXPANDED",
    FoldState.TENT_BOOK: "SPLIT_TACTILE_PALETTE",
    FoldState.FOLDED_COMPACT: "COMPRESSED_MONITORING_ORBIT",
}


class FMCALController:
    def __init__(self, dispatcher: HapticDispatcher):
        self.dispatcher = dispatcher
        self._previous_lens: str | None = None

    def select_lens(
        self,
        estimate: OrientationEstimate,
        semantic_digest_before: str,
        semantic_digest_after: str,
        predicate_bundle_before: str,
        predicate_bundle_after: str,
    ) -> LensDecision:
        invariant = (
            bool(semantic_digest_before)
            and semantic_digest_before == semantic_digest_after
            and predicate_bundle_before == predicate_bundle_after
        )
        certified = estimate.standing == EstimateStanding.CERTIFIED and invariant
        lens = LENSES[estimate.fold_state] if certified else LENSES[FoldState.FOLDED_COMPACT]
        changed = certified and self._previous_lens is not None and lens != self._previous_lens
        if certified:
            self._previous_lens = lens
        return LensDecision(
            estimate.event_id,
            lens,
            semantic_digest_before,
            predicate_bundle_before,
            changed,
        )

    def dispatch_for(self, decision: LensDecision) -> tuple[DispatchResult, HapticCommand | None]:
        if not decision.certified_transition:
            return self.dispatcher.issue(decision.event_id, HapticPattern.ZERO_PATTERN)
        return self.dispatcher.issue(decision.event_id, HapticPattern.DOUBLE_PULSE)

