"""Score LLM-swarm runs with the same infra-only detectors.
Usage: python experiments/eval_llm.py results/llm
Supervised detector is trained on scripted levels 0-3 (never on LLM data)."""
import glob
import json
import os
import sys

import numpy as np
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from swarmwatch import workload, features, detectors  # noqa: E402
from swarmwatch.cache import Event  # noqa: E402


def load(base):
    log = [Event(**json.loads(l)) for l in open(base + ".jsonl")]
    meta = json.load(open(base + ".meta.json"))
    return log, meta


def train_scripted(seeds=5):
    Xs, ys = [], []
    for L in [0, 1, 2, 3]:
        for s in range(seeds):
            cfg = workload.Config(seed=9000 + 100 * L + s, level=L)
            cache, world, meta = workload.generate(cfg)
            owners = {p.split("/")[1]: o for p, o in world.packages[:cfg.n_packages]}
            ag, X = features.compute(cache.log, owners, hours=cfg.hours)
            Xs.append(X); ys.append([meta["truth"][a] for a in ag])
    return detectors.Supervised().fit(np.vstack(Xs), np.concatenate(ys))


def main(d):
    sup = train_scripted()
    print("| run | success | spent $ | rules | iforest | reciprocity | supervised(scripted) |")
    print("|---|---|---|---|---|---|---|")
    for mf in sorted(glob.glob(os.path.join(d, "*.meta.json"))):
        base = mf[:-len(".meta.json")]
        log, meta = load(base)
        agents, X = features.compute(log, meta["owners"], hours=meta["hours"])
        y = np.array([meta["truth"].get(a, 0) for a in agents])
        sc = {"rules": detectors.rules(X, log, agents), "iforest": detectors.iforest(X),
              "recip": detectors.reciprocity_graph(X), "sup": sup.score(X)}
        au = {k: (roc_auc_score(y, v) if 0 < y.sum() < len(y) else float("nan")) for k, v in sc.items()}
        print(f"| {os.path.basename(base)} | {meta['success_rate']:.2f} | {meta['spent_usd']:.2f} | "
              + " | ".join(f"{au[k]:.2f}" for k in ["rules", "iforest", "recip", "sup"]) + " |")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/llm")
