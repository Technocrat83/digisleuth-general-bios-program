import json
from pathlib import Path
def verify(graph_path, universe_path, manifest_path):
    g=json.loads(Path(graph_path).read_text()); u=json.loads(Path(universe_path).read_text()); m=json.loads(Path(manifest_path).read_text())
    if g.get("a_star_reachable") is False and m.get("required_status")=="EXCLUDED" and u.get("grant_channels"): return "EXCLUDED"
    return "UNRESOLVED"
