EXP_DIR := experiments/composition-gap
UV      := uv run --no-project
DATE    := $(shell date +%Y-%m-%d)
SEEDS   ?= 20
MAX_USD ?= 25

.DEFAULT_GOAL := help
.PHONY: help test smoke credits pilot-haiku run-openrouter clean

help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-16s %s\n", $$1, $$2}'

test: ## Run pytest (no network)
	cd $(EXP_DIR) && $(UV) --with pytest pytest -q

smoke: ## Mock-backend smoke run (writes /tmp/smoke.jsonl)
	cd $(EXP_DIR) && $(UV) python harness.py --backend mock --seeds 2 --out /tmp/smoke.jsonl

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

clean: ## Remove __pycache__ and .pytest_cache (never results)
	find . -type d \( -name __pycache__ -o -name .pytest_cache \) -not -path "./.git/*" -prune -exec rm -rf {} +
