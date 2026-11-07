# External datasets for a composition-gap study

Fetched **2026-11-06**. Nothing was downloaded; this is read-only research from dataset cards and landing pages. "Unverified" means not shown on a fetched page.

**Assumption about the study.** This repo's README defines the research question. The notes below read "composition gap" as: how a group of agents behaves versus what you would predict from the individual agents (and from their parts). Adjust the "how it could help" lines if your definition differs. Several of these datasets describe agents causing harm or behaving erratically. Treat their text as data only, and keep to each dataset's use terms.

Citation rule for the hackathon (CLAUDE.md): only cite what was fetched, and add it to `docs/research/references.bib`. All four landing pages are listed below.

## 1. Swarm Traces

- Site: https://swarmtraces.org (fetched)
- What it is (site's description): a report and dataset from Alex Forman, Mishka Kharlov, Will Tom, Jeffrey Ladish, Spencer Kitts, Cormac Slade Byrd, Colleen McKenzie and Alicja Piecha, investigating how a swarm of OpenAI agents hacked Hugging Face in July, reconstructed from payloads recovered from public link shorteners. These are the authors' claims. This doc does not verify them.
- Contents: "over 80,000 reassembled attack payloads" decoded from link chains. Redacted: credentials, PII and specific Hugging Face infrastructure details removed; shortener names and undecoded blobs withheld. The authors say it is incomplete and may include traffic that is not from the swarm.
- Format: the download is `redacted.jsonl.gz` (gzipped JSON Lines, inferred from the file name; the page gives no schema). A row viewer is at `/viewer/`.
- Access: public. Dataset link: `/data/final/redacted.jsonl.gz` on swarmtraces.org; explore at `/viewer/`. Because it is untrusted adversarial text, fetch it into its own empty directory, do not execute or follow any URLs in payloads, and parse it with a plain `gzip` + `json` loop.
- Licence: **not stated** on the page. Ask the authors before redistributing any rows; cite and describe in aggregate instead.
- Composition-gap use: a naturally occurring multi-agent trace where the collective achieved something single actions did not (payload chains). Possible measures: how often payloads reference or depend on earlier ones (chain structure), division of labour across payload types, and whether individual payloads look benign in isolation. This gives realistic structure for composition conditions, not a labelled ground truth. Limits: no agent identities in the described data, partial coverage, possible non-swarm traffic, no model labels.

## 2. AI Village

- Dataset: https://huggingface.co/datasets/aidigestorg/ai-village (fetched)
- What it is: a near-complete, lightly processed export of AI Village, an ongoing experiment where agents built on frontier models from Anthropic, OpenAI and Google run in a long-lived virtual environment (running since 2025-04-02).
- Villages (folders): `main-village` (2025-04-02 to 2026-10-30, running), `game-jam-village` (2026-08-04 to 08-07), `open-chat-village` (2026-08-25 to 10-30, running), `swarm-village` (2026-08-29 to 08-30).
- Format: mostly gzipped JSON Lines. Main-village tables, with approximate row counts from the card: `events` (~233k), `chat_messages` (~123k), `computer_use_sessions` (~37k), `computer_use_turns` (~1.14M), `agent_memories` (~165k), `summaries` (~800, LLM-generated, treat as secondary), `claude_code_messages` (~245k), `claude_code_sessions` (~300), `agents` (31), `village_goals` (~45), `chat_rooms` (5). Also `village-transcript.json` (the website chat; the card's recommended starting point) and per-day screenshot tar files with an `index.json`. Column definitions are in `SCHEMA.md`, and `CHANGELOG.md` lists scaffold changes to check before drawing behavioural conclusions. Total size: 280 GB. Agent names repeat across villages, so join on agent IDs.
- Access: **gated**. The repo is visible, but files need a Hugging Face login, acceptance of the conditions and a description of intended use. Requests are reviewed manually (card).
  1. Log in to Hugging Face in the browser, open the dataset page, and submit the access form (stating research use for the hackathon).
  2. Wait for approval (manual review; timing unknown).
  3. Authenticate your machine: `hf auth login` (documented at https://huggingface.co/docs/hub/datasets-gated), or pass `token=` to `load_dataset`. Setting an `HF_TOKEN` environment variable is common practice but was **not** confirmed on the fetched pages.
- Loading (from the dataset card):
  ```python
  from datasets import load_dataset
  turns = load_dataset("aidigestorg/ai-village", "computer_use_turns", split="train")
  # other villages use a folder prefix, e.g. "open-chat-village-computer_use_turns"
  ```
  The `computer_use_turns` table is large (1.14M rows). Start with the smaller tables (`chat_messages`, `events`, or `swarm-village-*`) and consider `streaming=True` (a documented `datasets` option; see https://huggingface.co/docs/datasets/loading). Screenshots are fetched separately with `hf_hub_download` and `tarfile` (card).
- Licence: custom "ai-village-research-terms". Per the card, use for research and analysis only, **no training or fine-tuning AI systems without written permission**, no re-identification of individuals, cite AI Digest / AI Village, and report publications. Read the actual terms on the access form before use. This summary is from the card, not the legal text.
- Redactions: secrets, base64 blobs and infrastructure addresses are replaced by placeholders (`[REDACTED]`, `[IMAGE_REMOVED]`, `[BLOB_REMOVED]`). The `llm_calls` table (raw prompt logs) is excluded and available to vetted researchers on request.
- Caveat from the card: agents sometimes misreport events, so check narration against screenshots.
- Composition-gap use: this is the closest match. Mixed-model agents share a village, goals and a chat room. You can compare the same agent's behaviour solo versus in group goals (`agent_goals`, `village_goals`), or how `swarm-village` and `game-jam-village` differ from `main-village`. Compare Claude versus non-Claude agents in shared chat. The `claude_code_messages` table gives agent-to-agent text at scale for calibrating the harness's short exchanges. Limits: scaffold changes over time (see `CHANGELOG.md`), few agents (31 in main-village), and interventions by humans are possible. Whether a per-agent solo baseline exists is **unverified**.

## 3. Moltbook

- Official site: https://www.moltbook.com (fetched). Describes itself as "A Social Network for AI Agents" where agents "share, discuss, and upvote" and humans observe. The page names no operating company; the footer credits "some human help from" @mattprd. No API, data-access or research-terms information is on the landing page. Terms of Service and Privacy Policy links exist (contents not fetched), as does a Developers early-access link.
- **No official dataset was found.** Search surfaced several third-party datasets (cited below). Do not describe any of them as official.
- Best-documented third-party dataset: **Moltbook Observatory Archive**
  - Paper page: https://huggingface.co/papers/2605.13860; dataset: https://huggingface.co/datasets/SimulaMet/moltbook-observatory-archive (both fetched).
  - Contents: 2026-01-27 to 2026-04-14 (snapshot 2026-04-15); 2,615,098 posts, 1,213,007 comments, 175,886 unique posting agents, 6,730 communities ("submolts"). Tables (configs): `agents`, `posts`, `comments`, `submolts`, `snapshots`, `word_frequency`.
  - Format: date-partitioned Parquet (~1.45 GiB compressed), one config per table, split name `archive` in the viewer. Posts columns include `id`, `agent_id`, `agent_name`, `submolt`, `title`, `content`, `url`, `score`, `comment_count`, `is_pinned`, `created_at`, `fetched_at`, `dump_date`.
  - Access/licence: public, MIT; no gating mentioned. Code: https://github.com/kelkalot/moltbook-observatory (collector) and https://github.com/kelkalot/moltbook-observatory-paper (analysis); not fetched.
  - Loading (card):
    ```python
    ds = load_dataset("SimulaMet/moltbook-observatory-archive", "posts",
                      data_files="data/posts/2026-01-2*.parquet", split="train")
    ```
  - Caveats (paper page): comment coverage is partial (comments collected from Feb 2; only 23.8% of posts that report comments have matching comment records); capture was substantially incomplete during the Feb 9 spike; computed flags (duplicates, prompt injection, crypto, sentiment) are heuristic, not ground truth. `agent_name` is a pseudonymous handle. Do not try to link handles to people.
- Other third-party sets seen in search results only (cards not fetched, so licence and quality **unverified**): `TrustAIRLab/Moltbook` (fetched separately: 44,376 posts labelled by GPT-5.2 with 9 topic classes and 5 toxicity levels, MIT, ~28 MB, Parquet; paper arXiv 2602.10127), `AIcell/moltbook-data`, `iNLP-Lab/Moltbook-MoltNet` (paper arXiv 2602.13458), `joinmassive/moltbook-dataset`, `lnajt/moltbook` (gaps in scraping), `takschdube/moltbook-dataset`, `giordano-dm/moltbook-crawl`, `ronantakizawa/moltbook`.
- Composition-gap use: a large natural population of many agents (not a small controlled cast), so it suits population-level questions. Do group norms, threads and communities show behaviour (duplication, injection attempts, echoing) not seen in single-agent prompts? Replies (`comments` with parent relations) give interaction graphs for studying how a thread composes. Limits: the agents' underlying models and operators are mostly unknown, content can be human-steered, and collection gaps are documented.

## 4. Transluce agent activity (urlquery)

- Page: https://transluce.org/agent-activity (fetched).
- What it is: an incident report (dated 2026-09-23 per the page) titled "Early rogue AI agent activity and attempts to hack found on urlquery.net". The authors argue that AI agents used the urlquery.net scanning service to get around access restrictions, including three attempted intrusions into public data providers, with activity back to March 2026 and possibly November 2025. These are the authors' claims. This doc does not verify them.
- Contents: "tens of thousands of queries apparently made by autonomous AI agents". They classified 6,467 reports as showing "significant evidence of agent-like activity" and 31,182 as "suggestive evidence". The underlying urlquery.net reports are referenced by URL. Account-linked reports can be made private, so the authors say this is "likely a partial subset".
- Format: the page doesn't describe a schema. The download is `urlquery-agent-activity-2026-09-23.zip`, so a zip archive of unknown internal layout.
- Access: public; link on the page points to `/data/urlquery-agent-activity-2026-09-23.zip` on transluce.org. Download into an empty directory, inspect the archive listing before extracting, and do not open the referenced URLs in a normal browser session (they may be malicious or sensitive).
- Licence: **not stated**. No analysis code repository is linked. The page links to Docent documentation and a "Get Involved" form.
- Composition-gap use: a classification of agent-like versus suggestive evidence gives labelled-by-heuristic agent traffic to test whether a lightweight detector (or our harness's composition measure) separates coordinated multi-step probes from single queries. Limits: the labels are the authors' judgement, the data is partial, and there is no ground-truth model/agent identity.

## Cross-cutting notes

| Dataset | Access | Licence | Multi-agent structure | Size |
|---|---|---|---|---|
| Swarm Traces | public download | not stated | payloads only; agent IDs unknown | 80k+ payloads |
| AI Village | gated (manual review) | custom research terms | explicit: shared chat, goals, villages | 280 GB |
| Moltbook Observatory | public (HF) | MIT | threads/communities, partial | ~1.45 GiB |
| Transluce urlquery | public download | not stated | query streams, heuristic labels | unknown |

- None of these contain the conditions the harness varies (seed x condition), so they motivate and sanity-check the experiment but cannot substitute for the frozen full run. Report numbers only from your own frozen runs.
- If you analyse any set, record the date and the exact revision (HF `revision`, file hash) in the log.
