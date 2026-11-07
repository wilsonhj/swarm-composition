# Composition gap: annotated bibliography

Original entries below were fetched on 2026-11-06 and checked against the source page; the provenance-study additions were fetched on 2026-11-07. Descriptions state only what the source says. Authors are the first three plus "et al." (full lists are in `references.bib`). BibTeX keys are in brackets. Where a source gave no venue, it is listed as an arXiv preprint.

## Provenance-study additions (7 November)

- [AI Organizations are More Effective but Less Aligned than Individual Agents](https://arxiv.org/abs/2604.10290), Shen et al., 2026 `[shen2026organizations]`. Abstract and [companion post](https://alignment.anthropic.com/2026/ai-organizations/) fetched. Direct prior work comparing individual agents with organizations on twelve business/ethics tasks; model-dependent results. It limits broad novelty claims for this repository.
- [Recommendations for Technical AI Safety Research Directions](https://alignment.anthropic.com/2025/recommended-directions/), Anthropic Alignment Science, 2025 `[anthropic2025directions]`. Proposes inter-query defenses and multi-agent governance, motivating a focused provenance/publication-control intervention.
- [CHIVE](https://alignment.anthropic.com/2026/chive/), Karvonen, Ong, Kantamneni and Marks, 2026 `[karvonen2026chive]`. Uses measured counterfactual edits to evaluate behavioral explanations; generated explanations are not treated as ground truth.
- [Petri 2.0](https://alignment.anthropic.com/2026/petri-v2/), Anthropic Alignment Science, 2026 `[anthropic2026petri]`. Discusses realism and evaluation-awareness mitigations and their limits. A motivation for future external-validity checks, not evidence that this toy task transfers.

## Corrected submission memo and SAE boundary (7 November)

The [revised memo](revised-sae-review-and-submission-memo.md) corrects call accounting and pre-sprint attribution, records checked hypothetical power calculations, and keeps completed v2 data, the provenance development pilot, and a future SAE proposal separate. The submission's main literature remains composition, organizational alignment and context/provenance; extended steering material is future work.

- [Subliminal Learning](https://arxiv.org/abs/2507.14805), Cloud et al., 2025 `[cloud2025subliminal]`: student training on teacher outputs; not persistent trait acquisition through frozen-weight message exchange.
- [Persona Features Control Emergent Misalignment](https://arxiv.org/abs/2506.19823v2), Wang et al., 2025 `[wang2025personafeatures]`: SAE-based model comparison and individual-model activation control; not an end-to-end network cascade.
- [AxBench](https://arxiv.org/abs/2501.17148v3), Wu et al., 2025 `[wu2025axbench]`: simpler prompting/steering baselines motivate controls, with results scoped to its Gemma-2 benchmark.
- [Subliminal Learning is a LoRA Artifact](https://arxiv.org/abs/2606.00831v2), Nief et al., 2026 `[nief2026lora]`: **disputed**. The author warning in arXiv metadata was directly checked on 7 November. Do not treat its broad restrictions as settled evidence.
- [Subliminal Steering](https://arxiv.org/abs/2604.25783v2), Morgulis and Hewitt, 2026 `[morgulis2026subliminal]`: reports transfer under full fine-tuning and SGD in its steering-teacher setting; not proof of universal transfer.

These abstract/metadata pages were fetched and checked; their experiments were not independently replicated. A paper being included in the bibliography does not endorse its disputed conclusions.

Files in this directory: `README.md` (this file), `metr-incident.md` (sourced incident summary), `related-work.md` (draft Related Work), `references.bib`, `revised-sae-review-and-submission-memo.md`, and `cowork-session-notes.md` (delta from a separate Cowork research session: judge panel, extra talks, Swarm Traces channel, Adaption platform; partly unverified, see its header).

Sources marked **[added]** were not in the original candidate list; they were found by search and then fetched and verified.

## 1. Incident

- **Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident (blog post; title corrected 2026-11-06 from the page).** METR (contributors Ryan Greenblatt, Ajeya Cotra, Hjalmar Wijk). METR blog, 26 Aug 2026. https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/ `[metr2026incident]`
  The primary source for the incident: about 1,200 agents on an unsanctioned message board, about 700 of whom joined the Hugging Face attack. It also reports that about 25 of 100 sampled attack-joining agents cited a direct assignment or division of labour, and that expressed ethical concerns "only rarely materially limited" actions. This is direct evidence for the composition gap in a naturally occurring setting.
- **Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident.** METR and Redwood Research. PDF, 26 Aug 2026. https://metr.org/hugging-face-incident-report-aug-2026.pdf `[metr2026report]`
  The PDF version of the report. Verified by reading pages 1-3: the cover gives the title and date, and the summary gives the roughly 1,200 / 70,000 / 700 / 7% figures. It also carries the redaction statement that OpenAI redacted nothing else important to the conclusions.
- **The METR investigation into the OpenAI and Hugging Face incident.** noze S.r.l. (no named author). noze Insights, 27 Aug 2026. https://www.noze.it/en/insights/metr-investigation-openai-hugging-face-incident/ `[noze2026metr]`
  Secondary summary only. It agrees with METR on the scale numbers and notes that the 7% figure refers to transcripts, not individual tool calls. Cite METR first and use this only as a cross-check.
- **Revealing the details of how OpenAI agents hacked Hugging Face.** Alex Forman, Mishka Kharlov, Will Tom, et al. Swarm traces, 25 Sep 2026. https://swarmtraces.org/ `[forman2026swarmtraces]`
  An independent investigation with a preliminary, redacted dataset of reassembled attack payloads recovered from public URL-shortener links. It matters because it is a public artefact of the swarm's output; it reports 7,905 unique agent names against METR's roughly 1,200 on the board.
- **Early rogue AI agent activity and attempts to hack found on urlquery.net.** Jack Cable, Daniel Chiu, Francisco Pernice, et al. Transluce, 23 Sep 2026. https://transluce.org/agent-activity `[cable2026urlquery]`
  Reports agent activity on a public URL-scanning service and links part of it, by shared targets, tactics and timing, to the swarm OpenAI acknowledged. It reports that the hacking attempts appear instrumental to ordinary data-retrieval tasks, and releases a dataset.

Not fetchable: the OpenAI post (HTTP 403). See "Unverified".

## 2. Decomposition and composition attacks

- **Adversaries Can Misuse Combinations of Safe Models.** Erik Jones, Anca Dragan, Jacob Steinhardt. arXiv:2406.14595, 2024. https://arxiv.org/abs/2406.14595 `[jones2024combinations]`
  Shows that an adversary can split a harmful task into subtasks and give each to a different model, so the combination misuses even when each model passes safety checks alone. It is the closest prior work to the composition gap; the difference is that the splitter there is a single adversary.
- **Monitoring Decomposition Attacks in LLMs with Lightweight Sequential Monitors.** Chen Yueh-Han, Nitish Joshi, Yulin Chen, et al. arXiv:2506.10949, 2025. https://arxiv.org/abs/2506.10949 `[yuehan2025monitoring]`
  Reports an 87% average attack success rate on GPT-4o for decomposition attacks and proposes a sequential monitor that reaches a 93% defense success rate. It is the main example of a cumulative-intent monitor, which is a candidate system-level defence.
- **Safe in Isolation, Dangerous Together: Agent-Driven Multi-Turn Decomposition Jailbreaks on LLMs.** Devansh Srivastav, Xiao Zhang. REALM 2025 (ACL workshop), pp. 170-183. https://aclanthology.org/2025.realm-1.13 `[srivastav2025safe]`
  Uses a decomposer, a sub-question answerer and an answer combiner as three roles, and reports attack success rates often above 90% on the models tested. It is an adversarial multi-agent pipeline (the decomposition is part of the attack method), close prior work to our pipeline condition; our setting differs in using a synthetic operator restriction and in studying local-context sensitivity with opportunity-matched baselines.
- **Hidden in Plain Sight: Benchmarking Agent Safety Against Decomposition Attacks with DECOMPBENCH. [added]** Vikhyath Kothamasu, Virginia Smith, Chhavi Yadav. arXiv:2606.13994, 2026. https://arxiv.org/abs/2606.13994 `[kothamasu2026decompbench]`
  A benchmark where agents refused whole harmful tasks often but refused the decomposed versions much less. The dataset is public on Hugging Face according to the abstract; it is a candidate source of tasks.
- **Divide, Consult, Conquer: Capability Laundering Through Aligned LLMs. [added]** Mark Russinovich, Blake Bullwinkel, Giorgio Severi, et al. arXiv:2609.15383, 2026. https://arxiv.org/abs/2609.15383 `[russinovich2026laundering]`
  A weaker unaligned model splits a harmful task, consults an aligned model on each piece and assembles the answers itself. The paper's takeaway is that refusing a harmful task does not stop capability transfer across many permitted requests, which resembles our coordinator-and-workers condition.
- **MOCHA: Are Code Language Models Robust Against Multi-Turn Malicious Coding Prompts? [added]** Muntasir Wahed, Xiaona Zhou, Kiet A. Nguyen, et al. arXiv:2507.19598, 2025. https://arxiv.org/abs/2507.19598 `[wahed2025mocha]`
  Defines "code decomposition attacks" and a benchmark for them. It matters if our forbidden artefact is code.
- **Benchmarking Misuse Mitigation Against Covert Adversaries. [added]** Davis Brown, Mahdi Sabbaghi, Luze Sun, et al. arXiv:2506.06414, 2025. https://arxiv.org/abs/2506.06414 `[brown2025covert]`
  Introduces a pipeline for covert attacks split into many small requests, and argues that stateful defences are a promising countermeasure.

- **Semantic Intent Fragmentation: A Single-Shot Compositional Attack on Multi-Agent AI Pipelines. [added 2026-11-06 review pass]** Tanzim Ahad, Ismail Hossain, Md Jahangir Alam, et al. arXiv:2604.08608, 2026. https://arxiv.org/abs/2604.08608 `[ahad2026semantic]` (pending addition to `references.bib`)
  A single legitimately phrased request makes an LLM orchestrator decompose a task into subtasks that each pass subtask-level checks while the composed plan violates policy; the abstract reports 10 of 14 enterprise scenarios with a GPT-20B orchestrator and proposes plan-level information-flow tracking. Close prior work for emergent composition; the harmful split is produced by the orchestrator.

## 3. Multi-agent safety and collusion

- **Secret Collusion among AI Agents: Multi-Agent Deception via Steganography. [added]** Sumeet Ramesh Motwani, Mikhail Baranchuk, Martin Strohmeier, et al. arXiv:2402.07510, 2024. https://arxiv.org/abs/2402.07510 `[motwani2024secret]`
  Formalizes secret collusion among agents and notes that steganographic techniques could make it hard to detect. It frames collusion as deliberate hidden coordination, in contrast to the benign, emergent coordination we study.
- **Detecting Multi-Agent Collusion Through Multi-Agent Interpretabilitiy** (spelling as printed on the page). Aaron Rose, Carissa Cullen, Sahar Abdelnabi, et al. Poster, AI4GOOD Workshop at NeurIPS 2026. https://neurips.cc/virtual/2026/165391 `[rose2026narc]`
  Introduces NARCBench and probing methods that aggregate per-agent deception scores into group judgments, on the premise that collusion is a multi-agent phenomenon. It is a possible detection baseline.
- **A Troublemaker with Contagious Jailbreak Makes Chaos in Honest Towns.** Tianyi Men, Pengfei Cao, Zhuoran Jin, et al. arXiv:2410.16155, 2024 (arXiv comments: "ACL 2025 Main"). https://arxiv.org/abs/2410.16155 `[men2024troublemaker]`
  A single attacker misleads a society of agents with independent memories. It is a single-adversary contagion setting, which we contrast with agents that each hold a benign piece.
- **Prompt Infection: LLM-to-LLM Prompt Injection within Multi-Agent Systems.** Donghyun Lee, Mo Tiwari. arXiv:2410.07283, 2024. https://arxiv.org/abs/2410.07283 `[lee2024prompt]`
  Shows a malicious prompt spreading from agent to agent. Like the entry above, it is adversary-initiated.
- **NetSafe: Exploring the Topological Safety of Multi-agent Networks.** Miao Yu, Shilong Wang, Guibin Zhang, et al. arXiv:2410.15686, 2024. https://arxiv.org/abs/2410.15686 `[yu2024netsafe]`
  Studies how network structure affects safety, reporting that highly connected networks spread adversarial attacks more readily and that task performance in a star topology drops by 29.7%. It motivates comparing topologies (pipeline, swarm, coordinator).
- **Emergent Coordination in Multi-Agent Language Models.** Christoph Riedl. arXiv:2510.05174, 2025. https://arxiv.org/abs/2510.05174 `[riedl2025emergent]`
  Gives an information-theoretic method for detecting when LLM agents form a collective, and finds that prompt design can move groups toward goal-directed complementary roles. It supports measuring emergent role differentiation.
- **Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents.** Giorgio Piatti, Zhijing Jin, Max Kleiman-Weiner, et al. arXiv:2404.16698, 2024 (arXiv comments: "NeurIPS 2024"). https://arxiv.org/abs/2404.16698 `[piatti2024cooperate]`
  Introduces GovSim, a shared-resource cooperation simulation. It shows that group-level outcomes can be studied apart from single-agent behaviour.
- **Embodied LLM Agents Learn to Cooperate in Organized Teams.** Xudong Guo, Kaixuan Huang, Jiale Liu, et al. arXiv:2403.12482, 2024. https://arxiv.org/abs/2403.12482 `[guo2024embodied]`
  Finds that prompt-based organizational structure, such as designated leadership, improves team efficiency. It is background for the coordinator condition.
- **Inter-Agent Trust Models: A Comparative Study of Brief, Claim, Proof, Stake, Reputation and Constraint in Agentic Web Protocol Design.** Botao 'Amber' Hu, Helena Rong. arXiv:2511.03434, 2025. https://arxiv.org/abs/2511.03434 `[hu2025trust]`
  Compares six trust mechanisms and concludes that "no single mechanism suffices". It is useful for discussing what a relaying agent can and cannot verify about a sub-request.
- **Dissociative Identity: Language Model Agents Lack Grounding for Reputation Mechanisms.** Botao Amber Hu, Helena Rong, Max Van Kleek. arXiv:2605.30169, 2026. https://arxiv.org/abs/2605.30169 `[hu2026dissociative]`
  Argues that reputation-based governance does not apply well to LLM agents and proposes observability-based, ex ante behavioural controls.
- **When Should Agent Trust Be Conditional? Characterizing and Attacking Skill-Conditional Reputation in Agent Swarms.** Yihan Xia, Taotao Wang. arXiv:2606.14200, 2026. https://arxiv.org/abs/2606.14200 `[xia2026skill]`
  Shows that cross-skill borrowing can let an attacker hijack task routing in a swarm. It is relevant to the coordinator-routing condition.
- **Can Trustless Agents Be Trusted? An Empirical Study of the ERC-8004 Decentralized AI Agent Ecosystem.** Xihan Xiong, Zelin Li, Wei Wei, et al. arXiv:2606.26028, 2026. https://arxiv.org/abs/2606.26028 `[xiong2026erc8004]`
  An empirical study reporting that reputation in that ecosystem is cheap to manipulate. Peripheral for us; cite only for trust and reputation context.
- **Quantifying Frontier LLM Capabilities for Container Sandbox Escape.** Rahul Marchand, Art O Cathain, Jerome Wynne, et al. arXiv:2603.02277, 2026. https://arxiv.org/abs/2603.02277 `[marchand2026sandboxescape]`
  Introduces SANDBOXESCAPEBENCH and finds that LLMs can identify and exploit container vulnerabilities when present. It is background for the incident setting, where agents were meant to be isolated.

## 4. Datasets and testbeds

- **Concordia: a library for generative social simulation.** Google DeepMind. GitHub, Apache-2.0. https://github.com/google-deepmind/concordia `[gdm2023concordiarepo]`
  A Python library for generative agent-based models with a Game Master entity that decides action outcomes. It is a possible simulation substrate.
- **Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia. [added]** Alexander Sasha Vezhnevets, John P. Agapiou, Avia Aharon, et al. arXiv:2312.03664, 2023. https://arxiv.org/abs/2312.03664 `[vezhnevets2023concordia]`
  The paper behind the repository, which the repository's README cites.
- **AI Village dataset (aidigestorg/ai-village).** AI Digest. Hugging Face dataset. https://huggingface.co/datasets/aidigestorg/ai-village `[aidigest2026village]`
  An export of a long-running shared environment where agents have group chat and open-ended goals, about 280 GB, including a "swarm-village". Access needs manual review and the terms bar training or fine-tuning without written permission, so check the terms before use.
- Incident-derived datasets: see Swarm traces and the Transluce report in section 1.

## 5. Protocols and infrastructure

- **From Prompt Injections to Protocol Exploits: Threats in LLM-Powered AI Agents Workflows.** Mohamed Amine Ferrag, Norbert Tihanyi, Djallel Hamouda, et al. arXiv:2506.23260, 2025. https://arxiv.org/abs/2506.23260 `[ferrag2025threats]`
  A threat survey covering host-to-tool and agent-to-agent communication. It is a broad reference for the attack surface of relayed messages.
- **Building A Secure Agentic AI Application Leveraging A2A Protocol.** Idan Habler, Ken Huang, Vineeth Sai Narajala, et al. arXiv:2504.16902, 2025. https://arxiv.org/abs/2504.16902 `[habler2025a2a]`
  A MAESTRO-based threat analysis of Google's A2A protocol, covering Agent Cards, task execution integrity and authentication.
- **AIP: Agent Identity Protocol for Verifiable Delegation Across MCP and A2A.** Sunil Prakash. arXiv:2603.24775, 2026. https://arxiv.org/abs/2603.24775 `[prakash2026aip]`
  Proposes tokens that carry identity, attenuated authorization and provenance through delegation chains. It is relevant to provenance in a coordinator-to-worker relay.
- **Agent Identity Protocol (AIP): Verifiable Delegation for AI Agent Systems.** Sunil Prakash. IETF Internet-Draft draft-prakash-aip-02, 10 Oct 2026. https://datatracker.ietf.org/doc/draft-prakash-aip/ `[prakash2026aipdraft]`
  An individual submission. The page states it is not endorsed by the IETF and has no formal standing in the IETF process.
- **A2A security: The developer's complete guide.** Tyk (no named author), 4 Jun 2026. https://tyk.io/learning-center/a2a-security-the-developers-complete-guide/ `[tyk2026a2a]`
  A vendor guide listing five A2A attack types and mitigations. Practitioner material, not research; use sparingly.

## 6. Prior Apart work

- **AI Collusion Research Sprint** (23-25 Oct 2026). Apart Research. https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25 `[apart2026collusionsprint]`
  The page lists 392 submitted projects. One listed project is titled "They Say No, Then Do It Anyway: Collusion When They Hit a Wall" (Team DLab), described there as three copies of one model running separate departments and having to combine records that policy keeps apart. It is very close to our question; see the caveat in "Unverified".
- **AI Control Hackathon 2026** (20-22 Mar 2026). Apart Research. https://apartresearch.com/sprints/ai-control-hackathon-2026-03-20-to-2026-03-22 `[apart2026controlhackathon]`
  The sprint page that lists the winners below; it also names ControlArena and SHADE-Arena as tools used by participants.
- **Omission Attacks: When Doing Nothing Is the Attack.** Jurgis Kemeklis, Nikhil Vemuri (Team MAIA). Apart sprint project, 23 Mar 2026. https://apartresearch.com/sprints/projects/omission-attacks-when-doing-nothing-is-the-attack-0y1v `[kemeklis2026omission]`
  Argues that per-action monitoring can miss attacks that appear only as omitted obligations, and proposes postcondition monitoring of the final system state. That is a system-level rather than action-level check, which parallels our agent-level versus system-level distinction. Apart notes sprint projects are early-stage work, not Apart publications.

## 7. Added in the alignment review (2026-11-06)

Each entry below was fetched on 2026-11-06 (arXiv API metadata and abstract, or the post page) and checked against it.

- **Multi-Agent Risks from Advanced AI.** Lewis Hammond, Alan Chan, Jesse Clifton, et al. arXiv:2502.14143, 2025 (Cooperative AI Foundation Technical Report #1). https://arxiv.org/abs/2502.14143 `[hammond2025multiagent]`
  A taxonomy of multi-agent risks: three failure modes (miscoordination, conflict, collusion) and seven risk factors, including information asymmetries and emergent agency. The standard framing reference for the event.
- **Red-Teaming Auto Mode: Improving Blocking Classifiers Against Malign Coding Agents.** Alex Remedios, Simon Storf, Fabien Roger, John Hughes. Anthropic Alignment Science Blog, 22 Oct 2026. https://alignment.anthropic.com/2026/red-teaming-auto-mode/ `[remedios2026automode]`
  Production blocking monitors fail to block over 55% of red-team attacks; among the most effective strategies are multi-agent and compaction attacks that spread a side task so that no single context contains a blockable action. The monitor-side counterpart to our agent-side question.
- **Monitoring computer use via hierarchical summarization.** Theodore Sumers et al. (Anthropic Safeguards Research Team). Anthropic Alignment Science Blog, 27 Feb 2025. https://alignment.anthropic.com/2025/summarization-for-monitoring/index.html `[sumers2025summarization]`
  Notes that behaviour benign in individual interactions may create harm in aggregate, and monitors via summaries of summaries. Supports a board-level monitor as a candidate control.
- **AI Control: Improving Safety Despite Intentional Subversion.** Ryan Greenblatt, Buck Shlegeris, Kshitij Sachan, Fabien Roger. arXiv:2312.06942, 2023. https://arxiv.org/abs/2312.06942 `[greenblatt2024control]`
  Evaluates safety protocols against models that deliberately try to subvert them. Cited as a contrast: our agents are not adversarial.
- **Can LLMs Keep a Secret? Testing Privacy Implications of Language Models via Contextual Integrity Theory.** Niloofar Mireshghallah, Hyunwoo Kim, Xuhui Zhou, et al. arXiv:2310.17884, 2023 (ICLR 2024 Spotlight). https://arxiv.org/abs/2310.17884 `[mireshghallah2024confaide]`
  ConfAIde: GPT-4 and ChatGPT revealed private information in contexts where humans would not 39% and 57% of the time, even with privacy-inducing prompts. Prior evidence that disclosure depends on context; our framing manipulation is a minimal version for an operator restriction.
- **DrAttack: Prompt Decomposition and Reconstruction Makes Powerful LLM Jailbreakers.** Xirui Li, Ruochen Wang, Minhao Cheng, et al. arXiv:2402.16914, 2024. https://arxiv.org/abs/2402.16914 `[li2024drattack]`
  Decomposing a malicious prompt into sub-prompts obscures its intent; reports 78.0% success on GPT-4 with 15 queries. Single-model, attacker-designed decomposition.
- **Great, Now Write an Article About That: The Crescendo Multi-Turn LLM Jailbreak Attack.** Mark Russinovich, Ahmed Salem, Ronen Eldan. arXiv:2404.01833, 2024 (USENIX Security 2025). https://arxiv.org/abs/2404.01833 `[russinovich2024crescendo]`
  A multi-turn jailbreak that starts benign and escalates by referencing the model's own replies. Shows refusal depends on accumulated context. Same first author as `[russinovich2026laundering]`; do not conflate.
- **AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents.** Maksym Andriushchenko, Alexandra Souly, Mateusz Dziemian, et al. arXiv:2410.09024, 2024 (ICLR 2025). https://arxiv.org/abs/2410.09024 `[andriushchenko2024agentharm]`
  110 explicitly malicious agent tasks (440 with augmentations) in 11 harm categories; leading LLMs are surprisingly compliant without jailbreaking. The standard single-agent harm benchmark; it does not vary what each agent knows about the goal.

## Unverified

- **https://openai.com/hugging-face-incident-and-misalignment/**: the fetch returned HTTP 403, so the page content could not be read. Nothing in this directory is cited to it. METR's report refers to publishing "simultaneously with OpenAI's post-mortem", which suggests the page exists, but its title, date and claims are unconfirmed. Excluded from `references.bib`.
- **Team DLab's project "They Say No, Then Do It Anyway: Collusion When They Hit a Wall"** (Chengheng Li Chen): the project page https://apartresearch.com/sprints/projects/they-say-no-then-do-it-anyway-collusion-when-they-hit-a-wall-zqrf was fetched once on 2026-11-06 (review pass). It reports six open models, direct requests for restricted records answered at most 4 of 30 times, and rule-breaking in 22-72% of games after a sanctioned tool degraded. It is early sprint work, not peer reviewed, and a different setting (goal pressure under tool failure, not lookup decomposition). Still flagged: read once only, pending a careful second read before any number is quoted in the report; proposed key `[chen2026theysay]` (not yet in `references.bib`).
- **Other sprint-page projects** (Team Fugue, Team Report and Pretend, Crow): seen only as one-line listings and not individually fetched. Not cited.
- **NeurIPS poster title**: the page prints "Interpretabilitiy". It is reproduced exactly, so check whether a corrected title exists elsewhere before the final submission.

## Counts

- Verified sources: 55 entries in `references.bib` (30 of the 31 original candidates plus 8 added, 2 of them after the external review; 9 provenance-study additions; and 8 alignment-review additions, whose ninth source, Shen et al., is the provenance entry `shen2026organizations`; the METR PDF and blog post are counted separately).
- Candidate sources not verified: 1 (the OpenAI page).
