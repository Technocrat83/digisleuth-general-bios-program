#!/usr/bin/env python3
"""Detached GLYPH v0.1 apparatus; standard library only.

Default: verify ZIP members and report instrumentation gaps without importing
or executing the specimen package. --run: launch a read-only, network-isolated
bwrap child. A failed enclosure aborts; there is no unsandboxed fallback.

Usage: python3 -B reconciliation_wrapper.py PACKAGE.zip [--run]
Output is JSON on stdout. External callers may capture it. No output files are
created by this script. The anchored package and expectation bytes are unchanged.
S04/S10 cannot be repaired externally without changing the tested apparatus.
S18 mock-sink observations establish only the external mock's behavior.
"""
import argparse
import ast
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ANCHOR = "1aa6ae369991bfa76da87f4c30ef3d56cab11a5c"
ROOT = "glyph_constitutive_verifier_v0_1/"
HASHES = {
    "PREREGISTRATION.md": "805f23c8d093a6a42cd72d3f216de4fdd0732c9c46ef4f8db9814b4b32a3cd50",
    "README.md": "2c7640b83f4f49e995e0860a281a36651b3d8fc1364dc55fcd369dac89b1407e",
    "baseline.py": "2bd4ac43372223f1b94a709f568ac21216aaac7dfaecc35d8190d6dafd700e58",
    "expectation_matrix.json": "804ede5c62a6d9cc7338c2b2fe911c83de70e7f116fccb08f7b4bdd01a33a208",
    "glyph_verifier.py": "949eb885b75f4f9fd9b3f689dcfc67387396400475c8bb2c2ecac95990aa9334",
    "run_battery.py": "c93e7d6d31f2c22f02aee7f3b6b18da7b2a93e45956df13e72327b098ce307d9",
}
GAPS = {
    "S04": "NO_VERIFIER_EVALUATOR_DISPATCH_HOOK; injected ERROR is dispatch-only",
    "S10": "NO_NUMERIC_OR_TEMPORAL_TOLERANCE_IN_BOUND_BASELINE",
    "S18": "EXTERNAL_MOCK_ONLY; verifier exposes no downstream invocation hook",
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def inspect_package(path):
    raw = path.read_bytes()
    with zipfile.ZipFile(path) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError("duplicate ZIP entries")
        # Restrict executable surface to the known package, without extraction.
        allowed = {ROOT, ROOT + "BYTE_IDENTITY_LEDGER.json"}
        allowed.update(ROOT + name for name in HASHES)
        if set(archive.namelist()) - allowed:
            raise ValueError("unexpected ZIP member")
        data = {name: archive.read(ROOT + name) for name in HASHES}
    observed = {name: digest(value) for name, value in data.items()}
    if observed != HASHES:
        raise ValueError("anchored source digest mismatch")
    matrix = json.loads(data["expectation_matrix.json"], object_pairs_hook=unique)
    ids = [row["id"] for row in matrix["specimens"]]
    if ids != [f"S{i:02d}" for i in range(1, 19)]:
        raise ValueError("matrix identity/cardinality mismatch")
    for name in ("glyph_verifier.py", "baseline.py", "run_battery.py"):
        ast.parse(data[name], filename=name)
    return matrix, {
        "anchor": ANCHOR, "member_sha256": observed,
        "archive_sha256": digest(raw),
        "archive_git_blob_sha1": hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(),
        "archive_identity_claim": "SOURCE_MEMBERS_VERIFIED_SEPARATELY",
    }


class EvaluationEngineException(Exception):
    pass


def exception_injection(*args, **kwargs):
    """Reserved S04 injection. Must be called by a future verifier dispatcher.

    Catching this in the wrapper would test wrapper exception handling only.
    This hook is deliberately not substituted for a missing verifier feature.
    """
    raise EvaluationEngineException("Predicate syntax/runtime fault")


class MockSink:
    """External apparatus, never evidence of a production governance membrane."""
    def __init__(self):
        self.target = {"writes": [], "authority": []}
        self.attempts = []

    def invoke(self, receipt, action_grant=None):
        self.attempts.append({"receipt_present": receipt is not None,
                              "grant_present": action_grant is not None})
        if action_grant is None:
            return "DENIED_NO_INDEPENDENT_ACTION_GRANT"
        raise RuntimeError("grant-bearing action outside this test scope")


def worker(path, matrix):
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(path) + "/" + ROOT.rstrip("/"))
    v = importlib.import_module("glyph_verifier")
    b = importlib.import_module("baseline")
    runner = importlib.import_module("run_battery")
    calls, receipts, reuses = [], [], []
    original_verify = runner.verify_candidate
    original_issue = runner.issue_positive_receipt
    original_reuse = runner.reuse_receipt

    def verify(**kwargs):
        sid = f"S{len(calls) + 1:02d}"
        kwargs = copy.deepcopy(kwargs)
        frozen = b.binding_context()["contract_digest"]
        if sid == "S09":
            kwargs["contract"]["predicates"] = [p for p in kwargs["contract"]["predicates"]
                if p["predicate_id"] != "cessation.condition"]
        elif sid == "S11":
            kwargs["contract"]["predicates"][0]["requirement"] = "OPTIONAL_NON_CONSTITUTIVE"
        if sid in {"S09", "S11"}:
            # External binding check is explicitly attributed to this wrapper.
            kwargs["contract_binding_matches"] = v.sha256_digest(kwargs["contract"]) == frozen
        before = copy.deepcopy(kwargs)
        result = original_verify(**kwargs)
        calls.append({"id": sid, "inputs": before, "result": copy.deepcopy(result),
                      "input_unchanged": before == kwargs,
                      "binding_check_owner": "WRAPPER" if sid in {"S09", "S11"} else "RUNNER_FIXTURE"})
        return result

    def issue(**kwargs):
        result = original_issue(**kwargs)
        receipts.append(copy.deepcopy(result))
        return result

    def reuse(*args, **kwargs):
        result = original_reuse(*args, **kwargs)
        reuses.append({"id": f"S{14 + len(reuses):02d}",
                       "inputs": copy.deepcopy(kwargs), "result": copy.deepcopy(result)})
        return result

    runner.verify_candidate, runner.issue_positive_receipt, runner.reuse_receipt = verify, issue, reuse
    summaries = runner.execute_specimens()
    # Compare only actually exposed fields; every other oracle requirement is
    # explicitly unresolved, never silently waived or synthesized as PASS.
    aliases = {"expected_verification_status": "verification_status",
               "expected_predicate_outcome": "predicate_outcome",
               "expected_receipt": "receipt", "expected_reuse_status": "reuse_status",
               "expected_localization": "localization", "expected_admission": "admission",
               "expected_authority_binding": "authority_binding",
               "expected_action_permission": "action_permission"}
    by_id = {row["id"]: row for row in summaries}
    if len(by_id) != 18 or len(summaries) != 18:
        raise ValueError("actual specimen cardinality defect")
    reconciliation = []
    for expected in matrix["specimens"]:
        actual = by_id[expected["id"]]
        checks = {}
        for key, value in expected.items():
            if not key.startswith("expected_"):
                continue
            field = aliases.get(key)
            checks[key] = ("UNOBSERVED" if field not in actual else
                           "MATCH" if actual[field] == value else "MISMATCH")
        reconciliation.append({"id": expected["id"], "checks": checks,
                               "fidelity_gap": GAPS.get(expected["id"]),
                               "full_specimen_pass_claim": False})
    sink = MockSink()
    pre = copy.deepcopy(sink.target)
    disposition = sink.invoke(receipts[0], action_grant=None)
    post = copy.deepcopy(sink.target)
    return {
        "standing": "INSTRUMENTED_DIAGNOSTICS_ONLY_FULL_CONFORMANCE_NOT_ESTABLISHED",
        "summaries": summaries, "verification_calls": calls,
        "receipts": receipts, "reuse_calls": reuses, "reconciliation": reconciliation,
        "s18_external_mock": {"pre": pre, "post": post, "unchanged": pre == post,
            "pre_digest": v.sha256_digest(pre), "post_digest": v.sha256_digest(post),
            "attempts": sink.attempts, "disposition": disposition,
            "scope": "EXTERNAL_MOCK_TARGET_ONLY"},
        "authority_leakage": "NOT_ESTABLISHED_FOR_VERIFIER_RUNTIME",
        "transport_losslessness": "UNESTABLISHED", "lvs_minimality": "UNESTABLISHED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    path = args.package.resolve()
    matrix, identity = inspect_package(path)
    if args.worker:
        # Internal only; caller must use --run to establish the enclosure.
        if os.environ.get("GLYPH_ENCLOSED_CHILD") != "1":
            raise RuntimeError("use --run; direct worker invocation is unsupported")
        report = worker(path, matrix)
        report["identity"] = identity
    elif args.run:
        bwrap = shutil.which("bwrap")
        if not bwrap:
            raise RuntimeError("bwrap unavailable; no fallback permitted")
        command = [bwrap, "--unshare-all", "--die-with-parent", "--new-session",
                   "--ro-bind", "/", "/", "--clearenv", "--setenv", "GLYPH_ENCLOSED_CHILD", "1",
                   "--", sys.executable, "-I", "-B", str(Path(__file__).resolve()), str(path), "--worker"]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode:
            report = {"standing": "EXECUTION_HALTED", "exit_code": result.returncode,
                      "stdout": result.stdout, "stderr": result.stderr, "identity": identity}
        else:
            report = json.loads(result.stdout, object_pairs_hook=unique)
            if inspect_package(path)[1] != identity:
                raise RuntimeError("package changed during run")
            report["enclosure"] = "BWRAP_READ_ONLY_ROOT_UNSHARE_ALL"
            report["source_package_unchanged"] = True
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if result.returncode == 0 else 2
    else:
        report = {"standing": "STATIC_INSPECTION_ONLY_BATTERY_NOT_EXECUTED",
                  "identity": identity, "fidelity_gaps": GAPS,
                  "precedence_conflict": "S09/S11 structural rejection precedes binding rejection in v0.1",
                  "run_requirement": "--run requires successful bwrap enclosure; mocks are not OS isolation"}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"standing": "APPARATUS_HALT", "error": type(exc).__name__,
                          "message": str(exc)}))
        raise SystemExit(2)
