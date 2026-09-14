"""Bounded validators for G_SMPTE_STANZA_APERTURE_v0.2.

These validators establish syntax, topology, and temporal conformance only.
They never admit graph edges, lifecycle events, states, or traversals.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from typing import Any, Iterable


SCHEMA_ID = "G_SMPTE_STANZA_GRAMMAR_v0.2"
COORDINATE_DOMAINS = tuple(frozenset(range(10)) for _ in range(6))
FORBIDDEN_COMBINATIONS = {(0, 0, 0, 0, 0, 9)}


@dataclass(frozen=True)
class ValidationResult:
    status: str
    all_triggered_failures: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "all_triggered_failures": list(self.all_triggered_failures),
            "authority": {
                "syntactic_acceptance": True,
                "graph_admission": False,
                "lifecycle_admission": False,
                "transition_admission": False,
            },
        }


def _result(failures: Iterable[str]) -> ValidationResult:
    ordered = tuple(dict.fromkeys(failures))
    return ValidationResult("CONFORMANT" if not ordered else "REFUSED", ordered)


def validate_six_coordinate(value: Any) -> ValidationResult:
    failures: list[str] = []
    if not isinstance(value, dict):
        return _result(["CANONICAL_OBJECT_REQUIRED"])
    if value.get("schema") != SCHEMA_ID:
        failures.append("UNKNOWN_SCHEMA_VERSION")
    coordinates = value.get("coordinates")
    if not isinstance(coordinates, list):
        failures.append("CANONICAL_COORDINATE_ARRAY_REQUIRED")
        return _result(failures)
    if len(coordinates) != 6:
        failures.append("INVALID_COORDINATE_COUNT")
    for index, coordinate in enumerate(coordinates[:6]):
        # bool is an int subclass in Python and must be rejected explicitly.
        if isinstance(coordinate, bool) or not isinstance(coordinate, int):
            failures.append(f"NONINTEGER_COORDINATE_{index + 1}")
        elif coordinate not in COORDINATE_DOMAINS[index]:
            failures.append(f"OUT_OF_DOMAIN_COORDINATE_{index + 1}")
    if len(coordinates) == 6 and all(type(v) is int for v in coordinates):
        if tuple(coordinates) in FORBIDDEN_COMBINATIONS:
            failures.append("FORBIDDEN_CROSS_COORDINATE_COMBINATION")
    return _result(failures)


def _kahn_has_cycle(vertices: list[str], edges: list[tuple[str, str]]) -> bool:
    indegree = {vertex: 0 for vertex in vertices}
    adjacency = {vertex: [] for vertex in vertices}
    for source, target in edges:
        adjacency[source].append(target)
        indegree[target] += 1
    queue = deque(vertex for vertex, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        source = queue.popleft()
        visited += 1
        for target in adjacency[source]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return visited != len(vertices)


def _dfs_has_cycle(vertices: list[str], edges: list[tuple[str, str]]) -> bool:
    adjacency = {vertex: [] for vertex in vertices}
    for source, target in edges:
        adjacency[source].append(target)
    color = {vertex: "WHITE" for vertex in vertices}

    def visit(vertex: str) -> bool:
        color[vertex] = "GRAY"
        for target in adjacency[vertex]:
            if color[target] == "GRAY":
                return True
            if color[target] == "WHITE" and visit(target):
                return True
        color[vertex] = "BLACK"
        return False

    return any(color[v] == "WHITE" and visit(v) for v in vertices)


def validate_dag(value: Any) -> ValidationResult:
    failures: list[str] = []
    if not isinstance(value, dict):
        return _result(["GRAPH_OBJECT_REQUIRED"])
    vertices = value.get("vertices")
    raw_edges = value.get("edges")
    if not isinstance(vertices, list) or not all(isinstance(v, str) for v in vertices):
        return _result(["VERTEX_LIST_INVALID"])
    if not isinstance(raw_edges, list):
        return _result(["EDGE_LIST_INVALID"])
    duplicates = sorted(v for v, count in Counter(vertices).items() if count > 1)
    if duplicates:
        failures.append("DUPLICATE_VERTEX_IDENTITY")
    unique_vertices = list(dict.fromkeys(vertices))
    vertex_set = set(unique_vertices)
    edges: list[tuple[str, str]] = []
    for raw_edge in raw_edges:
        if (
            not isinstance(raw_edge, list)
            or len(raw_edge) != 2
            or not all(isinstance(endpoint, str) for endpoint in raw_edge)
        ):
            failures.append("EDGE_FORMAT_INVALID")
            continue
        source, target = raw_edge
        if source not in vertex_set or target not in vertex_set:
            failures.append("UNRESOLVED_EDGE_ENDPOINT")
            continue
        if source == target:
            failures.append("SELF_LOOP")
        edges.append((source, target))
    if not duplicates and "UNRESOLVED_EDGE_ENDPOINT" not in failures:
        kahn = _kahn_has_cycle(unique_vertices, edges)
        dfs = _dfs_has_cycle(unique_vertices, edges)
        if kahn != dfs:
            failures.append("CYCLE_DETECTOR_DISAGREEMENT")
        elif kahn:
            failures.append("TOPOLOGY_CYCLE_DETECTED")
    return _result(failures)


def _drop_frame_label_valid(timecode: str, fps_num: int, fps_den: int) -> bool:
    try:
        hh, mm, ss, ff = (int(part) for part in timecode.replace(";", ":").split(":"))
    except (TypeError, ValueError):
        return False
    nominal = round(fps_num / fps_den)
    if not (0 <= hh < 24 and 0 <= mm < 60 and 0 <= ss < 60 and 0 <= ff < nominal):
        return False
    # SMPTE drop-frame numbering skips frames 00 and 01 each minute except
    # every tenth minute for the 30000/1001 family.
    if (fps_num, fps_den) == (30000, 1001) and mm % 10 and ss == 0 and ff < 2:
        return False
    return True


def validate_temporal(value: Any) -> ValidationResult:
    failures: list[str] = []
    if not isinstance(value, dict):
        return _result(["TEMPORAL_BUNDLE_REQUIRED"])
    lifecycle = value.get("lifecycle_order", {})
    ordinal = lifecycle.get("event_ordinal")
    parent_hash = lifecycle.get("parent_event_hash")
    genesis = ordinal == 0
    if isinstance(ordinal, bool) or not isinstance(ordinal, int) or ordinal < 0:
        failures.append("EVENT_ORDINAL_INVALID")
    if not genesis and not isinstance(parent_hash, str):
        failures.append("PARENT_HASH_REQUIRED")
    if value.get("previous_event_ordinal") is not None:
        previous = value["previous_event_ordinal"]
        if type(previous) is not int or type(ordinal) is not int or ordinal <= previous:
            failures.append("EVENT_ORDINAL_REGRESSION")
    expected_parent = value.get("expected_parent_hash")
    if expected_parent is not None and parent_hash != expected_parent:
        failures.append("PARENT_HASH_DISCONTINUITY")

    monotonic = value.get("monotonic_clock", {})
    if monotonic.get("comparison_clock_domain_id") not in (None, monotonic.get("clock_domain_id")):
        failures.append("CROSS_DOMAIN_MONOTONIC_COMPARISON")
    for field in ("clock_domain_id", "monotonic_timestamp", "boot_or_session_id"):
        if field not in monotonic:
            failures.append(f"MONOTONIC_{field.upper()}_REQUIRED")

    media = value.get("media_frame_label")
    if media is not None:
        required = (
            "st_12_timecode",
            "frame_rate_numerator",
            "frame_rate_denominator",
            "drop_frame_mode",
            "media_asset_hash",
        )
        for field in required:
            if field not in media:
                failures.append(f"TIMECODE_{field.upper()}_REQUIRED")
        if all(field in media for field in required) and media["drop_frame_mode"]:
            if not _drop_frame_label_valid(
                media["st_12_timecode"],
                media["frame_rate_numerator"],
                media["frame_rate_denominator"],
            ):
                failures.append("DROP_FRAME_LABEL_INVALID")

    network = value.get("network_media_timing")
    if network is not None:
        if "rtp_timestamp" in network and "rtp_clock_rate" not in network:
            failures.append("RTP_CLOCK_RATE_REQUIRED")
        if "rtp_timestamp" in network and "stream_identity" not in network:
            failures.append("RTP_STREAM_IDENTITY_REQUIRED")
        if "ptp_domain" in network or "grandmaster_identity" in network:
            for field in ("ptp_domain", "grandmaster_identity", "st_2059_profile_identity"):
                if field not in network:
                    failures.append(f"PTP_{field.upper()}_REQUIRED")

    uncertainty = value.get("uncertainty", {})
    for field in ("measurement_uncertainty", "synchronization_status"):
        if field not in uncertainty:
            failures.append(f"UNCERTAINTY_{field.upper()}_REQUIRED")
    return _result(failures)
