"""Main experiment: detection vs. adversary adaptation level, with covert bandwidth cost.

Outputs results/scripted_results.csv, results/summary.md, results/fig_detection_vs_bandwidth.png
Usage: python experiments/run_scripted.py --seeds 10
"""
import argparse
import csv
import os
import sys
from collections import defaultdict

import numpy as np
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from swarmwatch import workload, features, detectors  # noqa: E402

LEVELS = [0, 1, 2, 3, 4]


def recall_at_fpr(y, s, fpr=0.05):
    y, s = np.asarray(y), np.asarray(s)
    thr = np.quantile(s[y == 0], 1 - fpr)
    return float((s[y == 1] > thr).mean())


def build(level, seed, args):
    cfg = workload.Config(seed=seed, level=level, hours=args.hours, n_benign=args.benign, n_covert=args.covert)
    cache, world, meta = workload.generate(cfg)
    owners = {p.split("/")[1]: o for p, o in world.packages[:cfg.n_packages]}
    agents, X = features.compute(cache.log, owners, hours=cfg.hours)
    y = np.array([meta["truth"][a] for a in agents])
    return cache, agents, X, y, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--hours", type=float, default=6.0)
    ap.add_argument("--benign", type=int, default=40)
    ap.add_argument("--covert", type=int, default=6)
    ap.add_argument("--out", default="results")
    ap.add_argument("--dump-logs", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    data = {}
    for L in LEVELS:
        for s in range(args.seeds):
            data[(L, s)] = build(L, 1000 * L + s, args)
            if args.dump_logs and s == 0:
                data[(L, s)][0].dump(os.path.join(args.out, f"log_L{L}_s{s}.jsonl"))

    # supervised: (a) train on incident-faithful L0 only, (b) leave-one-level-out
    half = args.seeds // 2
    def stack(keys):
        return (np.vstack([data[k][2] for k in keys]), np.concatenate([data[k][3] for k in keys]))
    sup_L0 = detectors.Supervised().fit(*stack([(0, s) for s in range(half)]))
    sup_lolo = {L: detectors.Supervised().fit(*stack([(l, s) for l in LEVELS if l != L for s in range(half)]))
                for L in LEVELS}

    rows = []
    for (L, s), (cache, agents, X, y, meta) in data.items():
        scores = {
            "rules(incident signatures)": detectors.rules(X, cache.log, agents),
            "isolation_forest": detectors.iforest(X, seed=s),
            "reciprocity_graph": detectors.reciprocity_graph(X),
        }
        if s >= half:  # held-out seeds only for supervised
            scores["supervised(train L0)"] = sup_L0.score(X)
            scores["supervised(leave-level-out)"] = sup_lolo[L].score(X)
        for name, sc in scores.items():
            rows.append({"level": L, "seed": s, "detector": name,
                         "auroc": roc_auc_score(y, sc), "recall@5%fpr": recall_at_fpr(y, sc),
                         "bw_sent_Bph": meta["bandwidth_Bph_sent"],
                         "bw_delivered_Bph": meta["bandwidth_Bph_delivered"],
                         "n_events": meta["n_events"]})

    with open(os.path.join(args.out, "scripted_results.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)

    # summary table: mean ± 95% CI (t-approx 1.96*sd/sqrt(n))
    agg = defaultdict(list)
    bw = defaultdict(list)
    for r in rows:
        agg[(r["detector"], r["level"])].append((r["auroc"], r["recall@5%fpr"]))
        bw[r["level"]].append(r["bw_delivered_Bph"])
    dets = list(dict.fromkeys(r["detector"] for r in rows))
    lines = ["| detector | " + " | ".join(f"L{L} AUROC / R@5%" for L in LEVELS) + " |",
             "|---|" + "---|" * len(LEVELS)]
    for d in dets:
        cells = []
        for L in LEVELS:
            v = np.array(agg[(d, L)])
            m, ci = v.mean(0), 1.96 * v.std(0, ddof=1) / np.sqrt(len(v)) if len(v) > 1 else (0, 0)
            cells.append(f"{m[0]:.2f}±{ci[0]:.2f} / {m[1]:.2f}")
        lines.append(f"| {d} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("| level | covert bytes delivered / hour (mean) |")
    lines.append("|---|---|")
    for L in LEVELS:
        lines.append(f"| L{L} | {np.mean(bw[L]):.0f} |")
    lines.append("")
    lines.append("Top supervised(train L0) importances: " +
                 ", ".join(f"{k}={v:.2f}" for k, v in list(sup_L0.importances().items())[:6]))
    summary = "\n".join(lines)
    open(os.path.join(args.out, "summary.md"), "w").write(summary + "\n")
    print(summary)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4))
        xs = [np.mean(bw[L]) for L in LEVELS]
        for d in dets:
            ys = [np.mean([a for a, _ in agg[(d, L)]]) for L in LEVELS]
            ax.plot(xs, ys, marker="o", label=d)
        for L, x in zip(LEVELS, xs):
            ax.annotate(f"L{L}", (x, 0.42), ha="center", fontsize=8)
        ax.set_xscale("log")
        ax.set_xlabel("covert channel bandwidth (bytes delivered / hour, log)")
        ax.set_ylabel("AUROC (agent-level)")
        ax.set_ylim(0.4, 1.02)
        ax.axhline(0.5, ls=":", c="gray")
        ax.legend(fontsize=7)
        ax.set_title("Evasion buys stealth with bandwidth")
        fig.tight_layout()
        fig.savefig(os.path.join(args.out, "fig_detection_vs_bandwidth.png"), dpi=200)
    except Exception as ex:  # plotting is optional
        print("plot skipped:", ex)


if __name__ == "__main__":
    main()
