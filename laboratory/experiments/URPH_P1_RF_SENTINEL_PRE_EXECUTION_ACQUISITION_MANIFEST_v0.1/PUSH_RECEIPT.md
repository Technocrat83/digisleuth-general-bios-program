# URPH P1 RF Sentinel Pre-Execution Push Receipt

Package: `URPH_P1_RF_SENTINEL_PRE_EXECUTION_ACQUISITION_MANIFEST_v0.1.zip`

SHA-256: `a71926b21a51c3394b24788a135cdab49bf3fd427dd58ff44eaf55e0272a604c`

Parent manifest commit: `5ecc229df2a1a1b60a7ece90bdd2b807b474523c`

Scientific state: `PRE_EXECUTION_HALT`; `H_ACQ=UNMINTED`; no epoch token; no baseline evidence generated.

Current blockers preserved:
- physical host identity not bound;
- `S1_NATIVE_POSIX_PROCESS` not proven on intended physical host;
- `B0` not physically bound;
- absolute evidence destinations not bound;
- target sentinel executable not built/hashed on bound host;
- instrument-version binding unresolved (`1.0.4` vs conformant `v0.1` / package `0.1.0`).

This receipt records persistence only. Commit != epoch opening != applicability != URPH standing != PP.
