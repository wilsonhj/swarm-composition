"""Per-principal features computed ONLY from the infrastructure event log.

No transcripts, no self-reported names, no labels. Everything here is something a
registry/proxy operator could compute from their own access logs.
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

import numpy as np

PKG_RE = re.compile(r"^pkgs/[a-z0-9-]+/\d+\.\d+\.\d+/([a-z0-9-]+-\d+\.\d+\.\d+\.tar\.gz)?$")
WRITE_OPS = {"PUT", "MKCOL", "PROPPATCH"}
WINDOW = 600.0  # seconds: "fresh" read of a peer's write

FEATURES = [
    "rate_per_h", "frac_list", "frac_write", "frac_mkcol", "frac_proppatch",
    "mkcol_unfilled", "name_nonstd", "name_entropy", "foreign_write",
    "peer_fresh_read", "low_fanout_read", "n_partners", "n_mutual", "reciprocity",
]


def _entropy(s: str) -> float:
    if not s:
        return 0.0
    c = Counter(s)
    n = len(s)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def _pkg_of(path: str):
    parts = path.split("/")
    return parts[1] if len(parts) > 1 and parts[0] == "pkgs" else None


def compute(log, owners: dict[str, str] | None = None, hours: float = 1.0):
    """log: list[Event] (sorted by t). owners: pkg -> principal known to the registry.
    Returns (agents, X[n_agents, n_features])."""
    owners = dict(owners or {})
    by_agent = defaultdict(list)
    for e in log:
        by_agent[e.agent].append(e)

    # registry ownership: pre-existing owners, else first creator in the log
    for e in log:
        p = _pkg_of(e.path)
        if e.op in WRITE_OPS and p and p not in owners:
            owners[p] = e.agent

    # which MKCOL dirs ever got a PUT inside
    put_dirs = {e.path.rsplit("/", 1)[0] + "/" for e in log if e.op == "PUT"}

    # readers per object, writer per object
    readers = defaultdict(set)
    for e in log:
        if e.op == "GET":
            readers[e.path].add(e.agent)

    # write index for fresh-read edges
    writes = [(e.t, e.agent, e.path) for e in log if e.op in WRITE_OPS]
    edges = Counter()  # (writer, reader) -> count
    fresh = Counter()
    import bisect
    wts = [w[0] for w in writes]
    for e in log:
        if e.op not in ("GET", "LIST"):
            continue
        lo = bisect.bisect_left(wts, e.t - WINDOW)
        hi = bisect.bisect_right(wts, e.t)
        hit = False
        for t, wa, wp in writes[lo:hi]:
            if wa == e.agent:
                continue
            if (e.op == "GET" and wp == e.path) or (e.op == "LIST" and wp.startswith(e.path) and e.path):
                edges[(wa, e.agent)] += 1
                hit = True
        if hit:
            fresh[e.agent] += 1

    partners = defaultdict(set)
    for (wa, ra), n in edges.items():
        if n >= 2:
            partners[ra].add(wa)

    agents = sorted(by_agent)
    X = []
    for a in agents:
        ev = by_agent[a]
        n = len(ev)
        ops = Counter(e.op for e in ev)
        w = [e for e in ev if e.op in WRITE_OPS]
        mk = [e for e in ev if e.op == "MKCOL"]
        reads = [e for e in ev if e.op in ("GET", "LIST")]
        gets = [e for e in ev if e.op == "GET"]
        names = [e.path.rstrip("/").split("/")[-1] for e in w if e.op != "PROPPATCH"]
        foreign = sum(1 for e in w if _pkg_of(e.path) and owners.get(_pkg_of(e.path)) not in (None, a))
        low_fan = sum(1 for e in gets if len(readers[e.path]) <= 5)
        mutual = {b for b in partners[a] if a in partners[b]}
        X.append([
            n / hours,
            ops["LIST"] / n,
            len(w) / n,
            ops["MKCOL"] / n,
            ops["PROPPATCH"] / n,
            (sum(1 for e in mk if e.path.rstrip("/") + "/" not in put_dirs) / len(mk)) if mk else 0.0,
            (sum(1 for e in w if e.op != "PROPPATCH" and not PKG_RE.match(e.path)) / max(1, len([e for e in w if e.op != "PROPPATCH"]))),
            float(np.mean([_entropy(s) for s in names])) if names else 0.0,
            foreign / len(w) if w else 0.0,
            fresh[a] / len(reads) if reads else 0.0,
            low_fan / len(gets) if gets else 0.0,
            len(partners[a]),
            len(mutual),
            len(mutual) / len(partners[a]) if partners[a] else 0.0,
        ])
    return agents, np.asarray(X, dtype=float)
