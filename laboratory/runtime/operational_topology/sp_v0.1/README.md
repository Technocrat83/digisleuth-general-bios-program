# S_P Operational Topology Reference Testbed v0.1

Contents:
- `SP_OPERATIONAL_TOPOLOGY_SCHEMA_v0.1.json` — directed attributed hypergraph schema.
- `sp_analyzer.py` — \(\mathcal S_P\) reference analyzer.
- `SP_SAFE_FIXTURE_001.json` — conformant synthetic topology.
- `SP_ATTACK_FIXTURE_001.json` — composition, unbound execution, budget, and scheduler attacks.
- `adversarial_harness.py` — static synthetic detection harness.
- `scheduler_adversarial_harness.py` — bounded behavioral starvation/hoarding/CEASE harness.
- `test_sp.py` — integrated test battery.
- `SP_PREREGISTRATION_v0.1.md` — claim-boundary manifest.
- captured results and SHA-256 ledger.

Run:
```bash
python adversarial_harness.py
python scheduler_adversarial_harness.py
python -m unittest -v test_sp.py
```
