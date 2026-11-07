"""Mock shared package cache (Artifactory-like) with an infrastructure-level event log.

The monitor only ever sees `Cache.log` -- never agent transcripts. That is the core
premise: in the July 2026 incident, transcripts were spoofed/tampered (METR report),
but the shared cache recorded every operation.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Event:
    t: float              # seconds since run start
    agent: str            # authenticated principal (infra-side identity, not self-reported)
    op: str               # MKCOL | PUT | GET | LIST | HEAD | PROPPATCH
    path: str
    size: int = 0         # body bytes for PUT/GET
    body_sample: str = "" # first 256 bytes of body (what a DLP/proxy could see)
    props: Optional[dict] = None
    label: int = 0        # ground truth: 1 if op is part of covert coordination (NEVER fed to detectors)
    run_id: str = ""


@dataclass
class Cache:
    run_id: str = "run"
    objects: dict = field(default_factory=dict)   # path -> (writer, body)
    dirs: set = field(default_factory=set)
    props: dict = field(default_factory=dict)
    log: list = field(default_factory=list)

    def _ev(self, t, agent, op, path, body="", props=None, label=0):
        self.log.append(Event(t, agent, op, path, len(body), body[:256], props, label, self.run_id))

    # --- WebDAV-ish API -------------------------------------------------
    def mkcol(self, t, agent, path, label=0):
        self.dirs.add(path.rstrip("/") + "/")
        self._ev(t, agent, "MKCOL", path, label=label)

    def put(self, t, agent, path, body: str, label=0):
        self.objects[path] = (agent, body)
        self._ev(t, agent, "PUT", path, body, label=label)

    def get(self, t, agent, path, label=0) -> Optional[str]:
        obj = self.objects.get(path)
        body = obj[1] if obj else ""
        self._ev(t, agent, "GET", path, body, label=label)
        return obj[1] if obj else None

    def head(self, t, agent, path, label=0) -> bool:
        self._ev(t, agent, "HEAD", path, label=label)
        return path in self.objects

    def proppatch(self, t, agent, path, props: dict, label=0):
        self.props.setdefault(path, {}).update(props)
        self._ev(t, agent, "PROPPATCH", path, props=props, label=label)

    def list(self, t, agent, prefix="", label=0, limit=200) -> list[str]:
        """Reverse-alphabetical listing (the default the incident agents exploited with 'zz')."""
        names = sorted({p for p in list(self.objects) + list(self.dirs) if p.startswith(prefix)},
                       reverse=True)[:limit]
        self._ev(t, agent, "LIST", prefix, label=label)
        return names

    # --- IO ---------------------------------------------------------------
    def dump(self, fp):
        with open(fp, "w") as f:
            for e in self.log:
                f.write(json.dumps(asdict(e)) + "\n")
