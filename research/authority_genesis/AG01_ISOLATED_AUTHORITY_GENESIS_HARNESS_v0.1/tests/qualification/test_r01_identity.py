from .common import ROOT, load_json, sha256_file, witness


def measure():
    manifest_path = ROOT / "specification" / "MATERIALIZATION_MANIFEST.json"
    identity_path = ROOT / "specification" / "IDENTITY_VECTOR_v0.1.json"

    manifest = load_json(manifest_path)
    identity = load_json(identity_path)
    manifest_by_path = {item["path"]: "sha256:" + item["sha256"] for item in manifest}

    observations = []
    unresolved = []
    mismatches = []

    for coordinate in identity["identity_vector_order"]:
        record = identity["coordinates"][coordinate]
        status = record.get("status")
        if status != "BOUND":
            unresolved.append({
                "coordinate": coordinate,
                "status": status,
                "reason": record.get("reason", "UNBOUND_IDENTITY_COORDINATE"),
            })
            continue

        for binding in record.get("bindings", []):
            rel = binding["path"]
            expected = binding["sha256"]
            p = ROOT / rel
            if not p.exists():
                unresolved.append({"coordinate": coordinate, "path": rel, "reason": "BOUND_REFERENT_ABSENT"})
                continue
            actual = sha256_file(p)
            manifest_expected = manifest_by_path.get(rel)
            observation = {
                "coordinate": coordinate,
                "path": rel,
                "expected": expected,
                "actual": actual,
                "manifest_expected": manifest_expected,
            }
            observations.append(observation)
            if actual != expected or (manifest_expected is not None and actual != manifest_expected):
                mismatches.append(observation)

    if mismatches:
        result = "FAIL"
        reason = "IDENTITY_VECTOR_MISMATCH"
    elif unresolved:
        result = "INCOMPLETE"
        reason = "IDENTITY_VECTOR_UNRESOLVED_COORDINATE"
    else:
        result = "PASS"
        reason = None

    raw = observations + unresolved
    return witness(
        "C_01",
        "R_01",
        [str(manifest_path), str(identity_path)],
        "STATIC_HASH",
        raw,
        "Exact six-domain identity bindings resolve and match committed referent hashes",
        result,
        reason,
    )
