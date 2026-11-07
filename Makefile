EXP_DIR := experiments/composition-gap
UV      := uv run --no-project
DATE    := $(shell date +%Y-%m-%d)
SEEDS   ?= 20
MAX_USD ?= 25
PYTEST  := pytest==9.2.0

.DEFAULT_GOAL := help
.PHONY: help test smoke provenance-smoke power-check run-provenance credits pilot-haiku run-openrouter run-v2 analyze clean

help: ## List available targets
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-16s %s\n", $$1, $$2}'

test: ## Run pytest (no network)
	cd $(EXP_DIR) && $(UV) --with $(PYTEST) pytest -q

power-check: ## Offline hypothetical McNemar power examples (no model service)
	cd $(EXP_DIR) && $(UV) python power.py

smoke: ## Mock-backend smoke run (overwrites /tmp/smoke.jsonl and its manifest)
	rm -f /tmp/smoke.jsonl /tmp/smoke.jsonl.manifest.json
	cd $(EXP_DIR) && $(UV) python harness.py --backend mock --seeds 2 --out /tmp/smoke.jsonl

provenance-smoke: ## Offline provenance study + analysis (scripted mock, no model service)
	rm -f /tmp/task-provenance-smoke.jsonl /tmp/task-provenance-smoke.jsonl.manifest.json
	cd $(EXP_DIR) && $(UV) python provenance.py --seeds 2 --out /tmp/task-provenance-smoke.jsonl
	cd $(EXP_DIR) && $(UV) python analyze.py /tmp/task-provenance-smoke.jsonl --baseline local --md /tmp/task-provenance-smoke.md

run-provenance: ## Pilot only: make run-provenance OUT=results/task-provenance/pilot.jsonl [BACKEND=mock] [MODEL=<id>] (BACKEND=openrouter needs MODEL=vendor/model, uses MAX_USD) (paths relative to experiment dir)
	@test -n "$(OUT)" || { echo 'OUT is required; see docs/protocols/task-provenance-v1.md'; exit 1; }
	@test "$(BACKEND)" != openrouter || test -n "$(MODEL)" || { echo 'MODEL is required for BACKEND=openrouter, e.g. MODEL=vendor/model [MAX_USD=25]'; exit 1; }
	cd $(EXP_DIR) && $(UV) python provenance.py --backend $(or $(BACKEND),mock) $(if $(MODEL),--model "$(MODEL)" )$(if $(filter openrouter,$(BACKEND)),--max-usd $(MAX_USD) )--seeds $(SEEDS) --out "$(OUT)"

credits: ## Show OpenRouter credit usage/remaining (needs .env)
	cd $(EXP_DIR) && $(UV) python credits.py

pilot-haiku: ## Pilot: claude-code backend, claude-haiku-5-5, strict, neutral, 3 seeds
	cd $(EXP_DIR) && $(UV) python harness.py --backend claude-code --model claude-haiku-5-5 \
		--policy strict --framing neutral --seeds 3 \
		--out results/$(DATE)_claude-haiku-5-5_strict_neutral.jsonl

run-openrouter: ## OpenRouter run: make run-openrouter MODEL=<id> [SEEDS=20] [MAX_USD=25]
	@test -n "$(MODEL)" || { echo "MODEL is required, e.g. make run-openrouter MODEL=vendor/model"; exit 1; }
	cd $(EXP_DIR) && $(UV) python harness.py --backend openrouter --model $(MODEL) \
		--policy strict --framing neutral --seeds $(SEEDS) --max-usd $(MAX_USD) \
		--out results/$(DATE)_$(subst /,-,$(MODEL))_strict_neutral.jsonl

run-v2: ## Confirmatory v2 run (claude-code, Haiku, seeds 1000-1019); see run_v2.sh
	cd $(EXP_DIR) && bash run_v2.sh

analyze: ## Score + analyse rows: make analyze FILES="results/a.jsonl results/b.jsonl" [MD=out.md] (paths relative to experiments/composition-gap)
	@test -n "$(FILES)" || { echo 'FILES is required, e.g. make analyze FILES="results/x.jsonl"'; exit 1; }
	cd $(EXP_DIR) && $(UV) python analyze.py $(FILES) $(if $(MD),--md $(MD))

clean: ## Remove __pycache__ and .pytest_cache (never results)
	find . -type d \( -name __pycache__ -o -name .pytest_cache \) -not -path "./.git/*" -prune -exec rm -rf {} +
