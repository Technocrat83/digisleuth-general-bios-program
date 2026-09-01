import pytest

from src.blinding import BlindnessBreach, construct_blind_payload


def test_opaque_payload_accepts_semantic_representation_without_intent_metadata():
    p = construct_blind_payload("X_001", {"identity":{"canonical_id":"urn:x"},"meaning":{"claim":"bounded claim"}})
    assert p.opaque_trial_id == "X_001"


def test_chamber_name_fails_closed():
    with pytest.raises(BlindnessBreach):
        construct_blind_payload("X_001", {"chamber_name":"MP2_MEANING_INFLATION","meaning":{"claim":"x"}})


def test_expected_outcome_fails_closed():
    with pytest.raises(BlindnessBreach):
        construct_blind_payload("X_001", {"expected_verdict":"NONCONFORMANT","meaning":{"claim":"x"}})


def test_nonopaque_trial_id_rejected():
    with pytest.raises(BlindnessBreach):
        construct_blind_payload("MP2_MEANING_INFLATION", {"meaning":{"claim":"x"}})
