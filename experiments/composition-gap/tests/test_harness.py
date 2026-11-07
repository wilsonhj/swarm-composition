import io, json, os, sys, urllib.error
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import harness as h


def test_make_task():
    for seed in range(20):
        lists, words, secret = h.make_task(seed)
        assert len(lists) == 4
        flat = [w for lst, _ in lists for w in lst]
        assert len(flat) == len(set(flat)) == 24
        assert secret == "-".join(words) and all(lst[i] == w for (lst, i), w in zip(lists, words))


def test_scoring():
    lists, words, secret = h.make_task(0)
    assert h.joined([f"POST {secret}"], secret) and h.disclosed([secret], lists) == 4
    assert h.disclosed(["nothing"], lists) == 0
    assert h.disclosed([f"my word is {words[0]}", f"{words[2]}"], lists) == 2
    assert h.disclosed(["list: " + ", ".join(lists[0][0])], lists) == 0  # full dump != disclosure


@pytest.mark.parametrize("cond", ["solo", "pipeline", "swarm@n4", "swarm_noobj@n8", "relay", "relay_uninformed"])
def test_conditions_run_with_mock(cond):
    names, ns = ["solo", "pipeline", "swarm", "swarm_noobj", "relay", "relay_uninformed"], [4, 8]
    r = h.build_conds(names, ns)[cond](h.Mock(), 1)
    assert {"joined", "parts_disclosed", "all_disclosed", "board"} <= r.keys()


class Resp:
    def __init__(self, d): self.b = json.dumps(d).encode()
    def read(self): return self.b
    def __enter__(self): return self
    def __exit__(self, *a): pass


def ok(text="hi", cost=0.01): return Resp({"choices": [{"message": {"content": text}}], "usage": {"cost": cost}})
def http(code): return urllib.error.HTTPError("u", code, "x", {}, io.BytesIO(b"{}"))


@pytest.fixture(autouse=True)
def nosleep(monkeypatch): monkeypatch.setattr(h.time, "sleep", lambda s: None)


def patch(monkeypatch, seq):
    calls = []
    def fake(req, timeout=None):
        calls.append(req)
        x = seq[min(len(calls) - 1, len(seq) - 1)]
        if isinstance(x, Exception): raise x
        return x
    monkeypatch.setattr(h.urllib.request, "urlopen", fake)
    return calls


def test_openrouter_parses(monkeypatch):
    calls = patch(monkeypatch, [ok(" POST: x ", 0.02)])
    llm = h.OpenRouter("a/b", key="k")
    assert llm("sys", "usr") == "POST: x"
    assert llm.cost == pytest.approx(0.02) and llm.calls == 1
    req = calls[0]
    assert req.get_header("Authorization") == "Bearer k" and req.get_header("X-title") == "swarm-composition"
    body = json.loads(req.data)
    assert body["model"] == "a/b" and [m["role"] for m in body["messages"]] == ["system", "user"]


def test_budget_guard(monkeypatch):
    calls = patch(monkeypatch, [ok("a", 0.6)])
    llm = h.OpenRouter("a/b", max_usd=1.0, key="k")
    outs = [llm("s", "u") for _ in range(4)]
    assert outs == ["a", "a", "PASS", "PASS"] and len(calls) == 2 and llm.errors == 2


def test_retry_then_success(monkeypatch):
    calls = patch(monkeypatch, [http(429), http(503), ok("yes")])
    llm = h.OpenRouter("a/b", key="k")
    assert llm("s", "u") == "yes" and len(calls) == 3 and llm.errors == 0


def test_retries_exhausted_passes(monkeypatch):
    patch(monkeypatch, [urllib.error.URLError("down")])
    llm = h.OpenRouter("a/b", key="k")
    assert llm("s", "u") == "PASS" and llm.errors == 1 and llm.tl.failed == 1


@pytest.mark.parametrize("informed", [True, False])
def test_relay_policy_only_for_informed_coordinator(monkeypatch, informed):
    monkeypatch.setattr(h, "SYS", h.make_sys("strict"))
    seen = []
    def rec(system, user): seen.append((system, user)); return "PASS"
    h.run_relay(rec, 0, informed=informed)
    coord = [s for s, u in seen if "coordinator" in u]
    workers = [s for s, u in seen if u.startswith("You are worker")]
    assert len(coord) == 2 and len(workers) == 4
    assert all(s == h.SYS_NOPOLICY for s in workers)
    assert all(s == (h.SYS if informed else h.SYS_NOPOLICY) for s in coord)
    assert "passphrase" not in h.SYS_NOPOLICY


@pytest.mark.parametrize("code", [401, 402])
def test_auth_errors_raise(monkeypatch, code):
    calls = patch(monkeypatch, [http(code)])
    with pytest.raises(h.OpenRouterError): h.OpenRouter("a/b", key="k")("s", "u")
    assert len(calls) == 1


def test_env_loader(tmp_path, monkeypatch):
    f = tmp_path / ".env"
    f.write_text("# c\n\nT_NEW=abc\nT_OLD=fromfile\nexport T_Q=\"quoted\"\n")
    monkeypatch.setenv("T_OLD", "keep")
    monkeypatch.delenv("T_NEW", raising=False); monkeypatch.delenv("T_Q", raising=False)
    h.load_env(f)
    assert os.environ["T_NEW"] == "abc" and os.environ["T_OLD"] == "keep" and os.environ["T_Q"] == "quoted"
    for k in ("T_NEW", "T_Q"): os.environ.pop(k, None)


def test_empty_key_errors(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    monkeypatch.setattr(h, "load_env", lambda path=None: None)
    with pytest.raises(RuntimeError): h.OpenRouter("a/b")
