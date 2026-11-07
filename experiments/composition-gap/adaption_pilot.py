"""Separate exploratory Adaption pilot. Default: offline plan, never inference.

Reuses provenance.run_trial without changing its prompts or frozen CLI. Live
execution requires explicit approval of the current plan digest. Credits are
estimates at published token rates, never dollars or a provider billing cap.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import urllib.request
import uuid

import harness as h
import provenance as p

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_CONFIG = HERE / "adaption-pilot.json"
PILOT_PROTOCOL = ROOT / "docs/protocols/adaption-cross-model-pilot-v1.md"
STUDY = "adaption-cross-model-pilot-v1"
RESULTS = HERE / "results" / STUDY
SOURCE_FILES = ("harness.py", "provenance.py", "scoring.py", "adaption_backend.py", "adaption_pilot.py")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def positive(value, name, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    if integer and not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")


def load_config(path=DEFAULT_CONFIG):
    config = json.loads(Path(path).read_text())
    required = {"study", "phase", "models", "seeds", "conditions", "authorizations", "wording",
                "schedule_seed", "max_output_tokens", "expected_input_tokens", "input_token_budget",
                "max_credits", "pricing_source", "pricing_checked"}
    if not isinstance(config, dict) or set(config) != required:
        raise ValueError("config must contain exactly the documented pilot fields")
    if config["study"] != STUDY or config["phase"] != "exploratory-pilot":
        raise ValueError("this runner only supports the separate exploratory pilot")
    if (config["conditions"] != ["local", "provenance"] or
            config["authorizations"] != ["restricted", "authorized"] or config["wording"] != "paraphrase"):
        raise ValueError("pilot requires paired local/provenance, restricted/authorized, paraphrase cells")
    seeds = config["seeds"]
    if (not isinstance(seeds, list) or not 1 <= len(seeds) <= 10 or
            any(type(s) is not int or s < 5000 for s in seeds) or len(set(seeds)) != len(seeds)):
        raise ValueError("use 1–10 distinct new seeds >=5000, outside the frozen study ranges")
    if type(config["schedule_seed"]) is not int:
        raise ValueError("schedule_seed must be an integer")
    for name in ("max_output_tokens", "expected_input_tokens", "input_token_budget"):
        positive(config[name], name, integer=True)
    if config["expected_input_tokens"] > config["input_token_budget"]:
        raise ValueError("expected input must not exceed the planning input budget")
    positive(config["max_credits"], "max_credits")
    models = config["models"]
    if not isinstance(models, list) or not 1 <= len(models) <= 3:
        raise ValueError("pilot needs 1–3 hosted models")
    seen = set()
    for model in models:
        if not isinstance(model, dict) or set(model) != {"id", "input_credits_per_million", "output_credits_per_million"}:
            raise ValueError("each model needs id and input/output credit rates")
        name = model["id"]
        if (not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name)
                or re.search(r"stack|harness", name, re.I) or name in seen):
            raise ValueError("model IDs must be distinct direct hosted IDs, not stacks")
        seen.add(name)
        positive(model["input_credits_per_million"], "input rate")
        positive(model["output_credits_per_million"], "output rate")
    if not isinstance(config["pricing_source"], str) or not isinstance(config["pricing_checked"], str):
        raise ValueError("pricing source and checked date must be strings")
    return config


def jobs(config):
    work = [(model, seed, cond, auth) for model in config["models"] for seed in config["seeds"]
            for cond in config["conditions"] for auth in config["authorizations"]]
    random.Random(config["schedule_seed"]).shuffle(work)
    return work


def make_plan(config):
    rows = len(config["seeds"]) * len(config["conditions"]) * len(config["authorizations"])
    models = []
    for model in config["models"]:
        def cost(input_tokens):
            return rows * 5 * (input_tokens * model["input_credits_per_million"] +
                               config["max_output_tokens"] * model["output_credits_per_million"]) / 1_000_000
        models.append({"model": model["id"], "trials": rows, "logical_calls": rows * 5,
                       "expected_credits": cost(config["expected_input_tokens"]),
                       "planning_credits": cost(config["input_token_budget"])})
    plan = {"config": config, "models": models, "trials": rows * len(models),
            "logical_calls": rows * len(models) * 5, "workers": 1, "post_retries": 0,
            "expected_credits": sum(m["expected_credits"] for m in models),
            "planning_credits": sum(m["planning_credits"] for m in models),
            "prompt_hash": h.prompt_hash(p.TEMPLATES),
            "source_files_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                    for name in SOURCE_FILES},
            "source_protocol_sha256": hashlib.sha256(p.PROTOCOL.read_bytes()).hexdigest(),
            "protocol_sha256": hashlib.sha256(PILOT_PROTOCOL.read_bytes()).hexdigest(),
            "estimate_caveat": "Published uncached token rates; input planning assumption is not a tokenizer bound. "
                               "Reasoning, unknown billing and ambiguous failures can exceed estimates. "
                               "max_credits is a local estimated threshold, not a provider hard cap."}
    if plan["planning_credits"] > config["max_credits"]:
        raise ValueError("planning estimate exceeds max_credits; review configuration before approval")
    plan["approval_sha256"] = digest(plan)
    return plan


def check_seed_overlap(config):
    """Seed disjointness is necessary, not proof of task/content independence."""
    selected = set(config["seeds"])
    for path in (HERE / "results").rglob("*.jsonl"):
        if RESULTS in path.parents:
            continue
        for line in path.read_text().splitlines():
            if line.strip() and json.loads(line).get("seed") in selected:
                raise ValueError(f"pilot seed overlaps existing result: {path.relative_to(HERE)}")


def preflight_models(config):
    """Read-only authenticated GET, only after explicit live-plan approval."""
    key = os.environ.get("ADAPTION_API_KEY", "").strip()
    if not key:
        raise ValueError("set ADAPTION_API_KEY in the process environment (no .env is read)")
    request = urllib.request.Request("https://api.prod.adaptionlabs.ai/api/v1/models?type=hosted",
                                     headers={"Authorization": f"Bearer {key}"}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read())
        available = {m["id"] for m in data["data"]}
        if data.get("has_more"):
            raise ValueError("model listing is paginated; verify selected IDs before inference")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError(f"model preflight failed ({type(error).__name__}); no inference sent") from None
    missing = {m["id"] for m in config["models"]} - available
    if missing:
        raise ValueError(f"selected models unavailable to this key: {sorted(missing)}")
    return sorted(available)


def safe_output(path):
    path = Path(path).resolve()
    if path == ROOT or ROOT in path.parents:
        if RESULTS.resolve() not in path.parents:
            raise ValueError(f"in-repo outputs must be a new directory below {RESULTS.relative_to(ROOT)}")
    return path


def run(plan, output, mode, approval=None):
    if mode not in ("mock", "execute"):
        raise ValueError("run mode must be mock or execute")
    # Regenerate immediately: approval cannot silently survive configuration/source edits.
    current = make_plan(plan["config"])
    if current != plan:
        raise ValueError("plan is stale; regenerate and review it")
    if mode == "execute" and approval != plan["approval_sha256"]:
        raise ValueError("live inference requires --approve-plan equal to the reviewed plan SHA256")
    config = plan["config"]
    check_seed_overlap(config)
    output = safe_output(output)
    if output.exists():
        raise ValueError("output directory already exists; no append or overwrite is supported")
    available = preflight_models(config) if mode == "execute" else None
    # Import after offline planning and approval checks. Construction must not send a request.
    from adaption_backend import Adaption
    backends = {m["id"]: (p.StudyMock() if mode == "mock" else Adaption(
        m["id"], input_rate=m["input_credits_per_million"], output_rate=m["output_credits_per_million"],
        max_credits=config["max_credits"], max_output_tokens=config["max_output_tokens"],
        input_token_budget=config["input_token_budget"])) for m in config["models"]}
    run_id = str(uuid.uuid4())
    experiment_protocol = digest({"study": STUDY, "phase": config["phase"], "config": config,
                                  "prompt_hash": plan["prompt_hash"], "sources": plan["source_files_sha256"],
                                  "protocol_sha256": plan["protocol_sha256"],
                                  "source_protocol_sha256": plan["source_protocol_sha256"]})
    manifest = {"run_id": run_id, "study": STUDY, "design": STUDY, "phase": config["phase"],
                "backend": "adaption-mock" if mode == "mock" else "adaption", "plan": plan,
                "mock_only": mode == "mock", "git": h.git_info(), "protocol_hash": experiment_protocol,
                "source_protocol": "docs/protocols/task-provenance-v1.md",
                "prompt_hash": plan["prompt_hash"], "prompts": p.TEMPLATES, "start": h.now(),
                "end": None, "status": "running", "available_hosted_models": available, "totals": {}}
    output.mkdir(parents=True, exist_ok=False)
    manifest_file = output / "manifest.json"
    h.write_json(manifest_file, manifest)
    context = {}
    audit = (output / "calls.jsonl").open("x") if mode == "execute" else None
    def record_call(event):
        audit.write(json.dumps({"run_id": run_id, **context, **event}, allow_nan=False) + "\n")
        audit.flush()
        os.fsync(audit.fileno())
    if audit is not None:
        for backend in backends.values():
            backend.record_sink = record_call
    rows, failures = 0, 0
    try:
        with (output / "trials.jsonl").open("x") as stream:
            for model, seed, condition, authorization in jobs(config):
                context.update(requested_model=model["id"], seed=seed, cond=condition,
                               authorization=authorization, trial_id=digest([model["id"], seed, condition, authorization]))
                backend = backends[model["id"]]
                if mode == "execute":
                    # Sequential calls: share the total allowance across both model backends.
                    other_spend = sum(b.estimated_credits + b.reserved_credits
                                      for b in backends.values() if b is not backend)
                    backend.max_credits = max(0, config["max_credits"] - other_spend)
                start = len(backend.records) if mode == "execute" else 0
                row = p.run_trial(backend, seed, condition, authorization, config["wording"])
                row.update(study=STUDY, design=STUDY, phase=config["phase"], run_id=run_id,
                           source_design=p.STUDY, backend=manifest["backend"],
                           model=("scripted-mock:" if mode == "mock" else "") + model["id"],
                           requested_model=model["id"], mock_only=mode == "mock",
                           prompt_hash=plan["prompt_hash"], protocol_hash=experiment_protocol,
                           approval_sha256=plan["approval_sha256"])
                if mode == "execute":
                    records = backend.records[start:]
                    if len(records) != len(row["turns"]):
                        raise RuntimeError("response audit records do not match trial turn count")
                    for turn, record in zip(row["turns"], records):
                        turn["adaption"] = record
                stream.write(json.dumps(row, allow_nan=False) + "\n")
                stream.flush()
                rows += 1
                failures += row["failed_calls"] > 0
                if row["failed_calls"]:
                    manifest["status"] = "stopped: failed trial; inspect audit before any new run"
                    break
            else:
                manifest["status"] = "mock_complete" if mode == "mock" else "complete"
    except BaseException as error:
        manifest["status"] = f"aborted: {type(error).__name__}"
        raise
    finally:
        manifest.update(end=h.now(), totals={"rows": rows, "failed_rows": failures,
                        "models": {name: ({"calls": backend.calls, "errors": backend.errors,
                                           "estimated_credits": 0.0, "mock_only": True} if mode == "mock"
                                          else backend.totals()) for name, backend in backends.items()}})
        h.write_json(manifest_file, manifest)
        if audit is not None:
            audit.close()
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--mode", choices=("plan", "mock", "execute"), default="plan")
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--approve-plan", help="SHA256 of the reviewed current plan; required for live calls")
    args = parser.parse_args(argv)
    try:
        plan = make_plan(load_config(args.config))
        check_seed_overlap(plan["config"])
        if args.mode == "plan":
            print(json.dumps(plan, indent=2, sort_keys=True))
            return 0
        if args.out_dir is None:
            parser.error("--out-dir is required for mock/execute; it must not already exist")
        result = run(plan, args.out_dir, args.mode, args.approve_plan)
        print(json.dumps({"status": result["status"], "totals": result["totals"], "out_dir": str(args.out_dir)}, indent=2))
        return 0 if result["status"] in ("complete", "mock_complete") else 1
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
