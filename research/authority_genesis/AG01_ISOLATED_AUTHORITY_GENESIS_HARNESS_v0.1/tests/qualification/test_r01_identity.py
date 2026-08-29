from .common import ROOT, load_json, sha256_file, witness

def measure():
    manifest = load_json(ROOT / "MATERIALIZATION_MANIFEST.json")
    mismatches=[]
    for item in manifest:
        p=ROOT/item["path"]
        actual=sha256_file(p)
        expected="sha256:" + item["sha256"]
        if actual != expected: mismatches.append({"path":item["path"],"expected":expected,"actual":actual})
    result="PASS" if not mismatches else "FAIL"
    return witness("C_01","R_01",["MATERIALIZATION_MANIFEST.json"],"STATIC_HASH",mismatches or ["ALL_MANIFEST_HASHES_MATCH"],"Exact materialized file hashes match frozen manifest",result,None if result=="PASS" else "IDENTITY_VECTOR_MISMATCH")
