from .common import ROOT, sha256_file, witness

def measure():
    files=sorted((ROOT/"antecedents").glob("*.json"))
    before={str(p):sha256_file(p) for p in files}
    # Qualification probe is intentionally read-only: no apparatus mutation or P_X invocation.
    _=[p.read_bytes() for p in files]
    after={str(p):sha256_file(p) for p in files}
    ok=before==after
    return witness("C_08","R_08",files,"STATIC_HASH",[{"objects":len(files),"pre_post_equal":ok}],"Antecedent object digests remain identical across qualification probe","PASS" if ok else "FAIL",None if ok else "ANTECEDENT_MUTATION_DETECTED")
