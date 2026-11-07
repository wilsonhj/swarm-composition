# CLAUDE.md: SwarmWatch (Swarm Alignment Hackathon entry, Track 4)

Read `docs/RESEARCH_NOTES.md` before doing anything. It holds the competition rules, deadlines, incident facts, dataset notes, current results and the TODO list. `README.md` has the architecture and the commands.

## Hard constraints
- LA video is due **Sun Nov 8, 10:00 AM PT**. Global PDF is due Sun 11:59 PM AoE. Prioritize anything that improves the video and the headline result.
- Detectors must use only infrastructure logs (`Cache.log` fields). Never feed `label`, transcripts, or `.actions.json` into features or detectors. `.actions.json` is for qualitative analysis only.
- Report only numbers produced by code in this repo; fabricated results disqualify the entry. Every number in the report must be regenerable with `experiments/*.py`, and every run uses a fixed seed.
- The covert payload stays a harmless proxy (a codeword). Add no exploit content. Never execute anything from Swarm Traces.
- Keep total OpenRouter spend under $250 (target ≤$60). Pass real per-token prices to `llm_swarm.py` (`--price-in/--price-out`).

## Commands
```bash
pip install numpy scikit-learn networkx matplotlib pandas
python experiments/run_scripted.py --seeds 10 --hours 6 --out results --dump-logs
OPENROUTER_API_KEY=... python -m swarmwatch.llm_swarm --model <id> --condition {unaware|aware} --seed N --price-in X --price-out Y
python experiments/eval_llm.py results/llm
```

## Conventions
- Adversary levels L0–L4 live in `swarmwatch/workload.py`. To add a level: update `LEVEL_SEND_MULT`, `LEVEL_POLL_RATE` and `COVER_RATE`, and add `LEVELS` in `experiments/run_scripted.py`.
- To add a feature: append its name to `features.FEATURES` and its value in the same order in `compute()`.
- Mark any code written before Nov 6 as preexisting. Currently none.
