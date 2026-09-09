"""
Validates COMMERCIAL_TRANSLATION_OBJECT_v0.1 against the anti-inflation boundary.
Guarantees: Claim_market <= Capability_demonstrated.
"""

from typing import Dict, Any
import re

FORBIDDEN_TERMS_IN_STATIC = [
    r"\bproduction[\s-]?certified\b",
    r"\bproven\s+incident\s+reduction\b",
    r"\bruntime\s+performance\b",
    r"\bdeployed\s+at\s+scale\b",
    r"\benterprise\s+proven\b",
    r"\bautonomous\s+resolution\b",
]

class AntiInflationBreach(Exception):
    pass

class ConstitutionalBreach(Exception):
    pass

def validate_translation_object(
    translation_obj: Dict[str, Any],
    source_event: Dict[str, Any]
) -> bool:
    if translation_obj["originating_event_id"] != source_event["event_id"]:
        raise ConstitutionalBreach("Event ID mismatch across boundary membrane.")

    if translation_obj["originating_residue_id"] != source_event["originating_residue_id"]:
        raise ConstitutionalBreach("Residue ID mismatch across boundary membrane.")

    if translation_obj["preserved_scientific_standing"] != source_event["exact_scientific_standing"]:
        raise AntiInflationBreach(
            f"Standing mutation detected: translation claims "
            f"'{translation_obj['preserved_scientific_standing']}' but source has "
            f"'{source_event['exact_scientific_standing']}'."
        )

    interrogation = translation_obj.get("interrogation", {})
    market_claim = interrogation.get("Q03_supported_market_claim", "")

    source_standing = source_event["exact_scientific_standing"]
    if source_standing in ["FIXTURE_CONFORMANCE_ONLY", "UNPROVEN_SPECIFICATION"]:
        for pattern in FORBIDDEN_TERMS_IN_STATIC:
            if re.search(pattern, market_claim, re.IGNORECASE):
                raise AntiInflationBreach(
                    f"Claim ceiling violation: static conformance fixture asserts '{pattern}'."
                )

    prohibited = translation_obj.get("prohibited_claims", [])
    if not prohibited:
        raise AntiInflationBreach("Prohibited claims list cannot be empty.")

    q10 = interrogation.get("Q10_next_revenue_facing_maneuver")
    if not q10:
        raise ConstitutionalBreach("Q10 (next revenue-facing maneuver) cannot be omitted.")

    return True