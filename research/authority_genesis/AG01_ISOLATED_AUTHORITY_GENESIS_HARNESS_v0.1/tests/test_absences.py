from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_absences():
    names={p.name for p in ROOT.rglob("*") if p.is_file()}
    for n in ("adjudicator.py","theorem_evaluator.py","authority_classifier.py","EXECUTION_ADMISSION_TOKEN.json"): assert n not in names
