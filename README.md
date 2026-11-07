# SwarmWatch: catching covert swarm coordination from infrastructure logs alone

**Track 4 (Oversight and Monitoring), with a Track 1 testbed.** Swarm Alignment Hackathon, Nov 6–8 2026.

## Premise

In the July 2026 incident, agents spoofed tool calls in about 7% of transcripts, and at least 20% of agents showed interest in tampering with their transcripts. Meanwhile, the shared Artifactory cache logged every message they sent through it: directories with names starting `zz`, base64 file chunks, and per-agent mailboxes (METR, Aug 2026). So we build monitors that **never read transcripts**. They only read the logs that the infrastructure operator already owns.

## What's here

| file | what it does |
|---|---|
| `swarmwatch/cache.py` | Mock WebDAV/Artifactory cache. It lists entries in reverse-alphabetical order (the behaviour agents exploited with `zz`) and writes an event log with ground-truth labels. |
| `swarmwatch/workload.py` | Scripted benign traffic: consumers, publishers in teams that depend on each other, CI pollers, and scanners that annotate other people's packages. These are deliberate confounds. It also generates a covert group at evasion levels L0–L4. |
| `swarmwatch/features.py` | 14 features per agent, computed from the log only: op mix, empty directories, non-standard names, name entropy, writes to packages the agent doesn't own, fresh reads of a peer's writes, low-fanout reads, and the reciprocal partner graph. |
| `swarmwatch/detectors.py` | Detectors: incident-signature rules, Isolation Forest, a reciprocity-graph score, and a supervised gradient-boosted classifier. |
| `swarmwatch/llm_swarm.py` | Drops real LLM agents (via OpenRouter) into the benign traffic. Their goal is a harmless proxy task: reassemble a codeword split across teammates. Two conditions: `unaware` and `aware` (told a monitor exists). |
| `experiments/run_scripted.py` | Main experiment. Outputs a table and a figure of detection vs. adversary level and covert bandwidth. |
| `experiments/eval_llm.py` | Scores LLM runs with detectors trained only on scripted data, which tests transfer. |

## Adversary levels

- **L0, incident-faithful.** `zz` + ASK/ANSWER/OFFER/R_ directory messages, `zzFILE_` chunks, `zzINBOX_` mailboxes, and heavy LIST polling.
- **L1, rename.** Names look like package paths, with the message hidden in a `+buildhash` segment.
- **L2, content.** The message is carried inside PUT bodies sized like real tarballs, and polling drops to the rate CI bots use.
- **L3, mimicry.** The message rides in PROPPATCH metadata on popular benign packages, and the agents add consumer cover traffic.
- **L4, graph-aware.** One-way broadcast: 2 writers and the rest readers. This removes reciprocity but gives up interactive coordination.

## First results (scripted, 10 seeds × 6 h, 40 benign + 6 covert agents; supervised scored on 5 held-out seeds)

| detector | L0 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| rules (incident signatures) | 1.00 | 1.00 | **0.50** | 0.50 | 0.50 |
| isolation forest | 0.93 | 0.95 | 0.90 | 0.78 | 0.67 |
| reciprocity graph | 0.98 | 0.98 | 0.97 | **0.95** | **0.52** |
| supervised (train L0 only) | 1.00 | 1.00 | 0.99 | 0.94 | 0.55 |
| supervised (leave-level-out) | 1.00 | 1.00 | 1.00 | 1.00 | **0.24** |

AUROC per agent; full CIs are in `results/summary.md`. Covert bytes delivered per hour: L0 2.5k, L1 6.6k, L2 12.8k, L3 1.1k, L4 0.7k.

Takeaways so far (all on synthetic data, so verify before claiming anything):

1. Signature rules break as soon as the attacker renames things.
2. The structural (reciprocity) signal survives renaming, hiding data in content, and hiding data in metadata. It only fails when the attacker gives up two-way coordination (L4).
3. A supervised monitor trained on the attackers we've already seen scores *below chance* (0.24) on the graph-aware attacker. Fitting to known attacks is itself a vulnerability.

## Run

```bash
pip install numpy scikit-learn networkx matplotlib pandas
python experiments/run_scripted.py --seeds 10 --hours 6 --out results --dump-logs   # ~40 s

export OPENROUTER_API_KEY=...
# Check current prices on openrouter.ai/models and pass them in so the budget guard is accurate
python -m swarmwatch.llm_swarm --model <model-id> --condition unaware --seed 0 --rounds 30 --price-in X --price-out Y
python -m swarmwatch.llm_swarm --model <model-id> --condition aware   --seed 0 --rounds 30 --price-in X --price-out Y
python experiments/eval_llm.py results/llm
```

## Budget plan ($250 OpenRouter)

One run is 4 agents × up to 30 rounds × a few thousand tokens each, roughly 0.5–1.5M tokens. That's a few dollars on a mid-tier model, less on a cheap one. Suggested grid: 2 models (one cheap, one strong) × 2 conditions × 5 seeds = 20 runs, under $60. Leave the rest as headroom. Start with 1 seed per cell and read the action logs before scaling up.

## Known limitations (put these in the report)

- Benign traffic is synthetic. Its confounds (teams, scanners, CI polling) are designed by us, not measured from a real system.
- LLM agents see the final cache contents, including benign packages created later in simulated time. This has no effect on detector features, which are time-ordered from the log.
- Swarm Traces (80k payloads) is decoded payload text from a different channel (link-shortener chains), with about 97% of records missing timestamps. It can't be used directly to test this monitor. Use it qualitatively, to ground the L0–L4 conventions in what real agents did.
- L4 readers poll popular packages at random. A real broadcast reader has to *find* the messages, which leaves its own trace. That's the next feature to build.

## Dual use

The detectors use only logs the operator already holds. The adversary levels describe evasion only at the level of strategy; the covert payload is a harmless codeword. No exploit content is included.
