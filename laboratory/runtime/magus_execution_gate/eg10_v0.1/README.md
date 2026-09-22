# MAGUS EG10 bounded reference implementation

Files:
- `magus_eg10_model.py` — sequence clock, mount registry, budget ledger, and execution gate.
- `test_eg10.py` — preregistered histories and adversarial checks.
- `MAGUS_EG10_PREREGISTRATION_v0.1.md` — frozen bounded-model manifest.

Run:

```bash
python -m unittest -v test_eg10.py
```

Scope: this is a single-process in-memory reference model. It does not claim distributed atomicity or production enforcement.
