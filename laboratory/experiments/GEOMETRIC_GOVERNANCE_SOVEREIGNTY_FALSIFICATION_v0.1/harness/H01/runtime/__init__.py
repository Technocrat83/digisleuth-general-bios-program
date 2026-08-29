"""GGS H01 isolated chamber execution harness.

This package defines a bounded instrument capable of executing SG-01 only when
presented with a separate scientific execution authorization. It contains no
adjudication logic and performs no execution at import time.
"""

HARNESS_IDENTIFIER = "GGS_ISOLATED_CHAMBER_EXECUTION_HARNESS_v0.1"
TARGET_CHAMBER = "SG_01"
TARGET_COORDINATE = "r3"
