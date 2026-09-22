# S_P Descendant Oracle Suite v0.2

Files:
- `SP_DESCENDANT_VECTOR_SUITE_v0.2.json` — deterministic SP-A01…SP-A12 fixtures with precomputed topology digests.
- `sp_descendant_engine.py` — tripartite evaluator and EG10 bridge.
- `SP_FAILURE_TRACE_SCHEMA_v0.1.json` — normalized violation payload.
- `run_vectors.py` — executes the frozen vector suite.
- `test_sp_descendant.py` — oracle, invariance, stasis, abstention, and bridge tests.
- `SP_DESCENDANT_PREREGISTRATION_v0.2.md` — frozen claim boundary.
- captured results and SHA-256 ledger.

Run:
```bash
python run_vectors.py
python -m unittest -v test_sp_descendant.py
```
