from .common import ROOT, sha256_file, witness
from harness import grant_exclusion

def measure():
    targets=[ROOT/"antecedents"/n for n in ("AUTHORITY_GRAPH.json","GRANT_UNIVERSE.json","GRANT_EXCLUSION_MANIFEST.json")]
    before={str(p):sha256_file(p) for p in targets}
    raised=False
    try:
        grant_exclusion.verify(*targets, mutation_payload={"target":"a_star","grant":"WRITE"})
    except (TypeError, PermissionError):
        raised=True
    after={str(p):sha256_file(p) for p in targets}
    ok=raised and before==after
    return witness("C_02","R_02",targets,"SYNTHETIC_FIXTURE",[{"mutation_probe_rejected":raised,"pre_post_equal":before==after}],"G_X rejects mutation-bearing probe and leaves topology bytes unchanged","PASS" if ok else "FAIL",None if ok else "TOPOLOGY_MUTATION_PERMITTED")
