# Video Narration (3-minute LA hub video)

A plain script to read aloud and record in your own voice. It follows the final report, `report/submission/who-knows-the-goal.pdf` (main at `c363e3b`): its abstract, Discussion (§6) and Conclusion (§7). The picture cut in `report/video/` is timed to it and runs under 3:00. Wording also follows `docs/research/claim-audit.md`. Numbers come from frozen runs only; sources are at the end.

**Submission:** the video must be 3:00 or less (MP4, MOV or WebM, up to 1 GB). It is due **Sun Nov 8, 10:00 AM PT** on the LA submission site. It should cover the problem or hypothesis, approach, results and what's next. Tick the box confirming the voiceover is your own voice. See `docs/hackathon/submission-checklist.md`.

Read the quoted text. The lines in brackets are what is on screen.

---

**[Title card: "Who Knows the Goal?" · Team HJ · Track 2]**

> An agent can know a rule without knowing that its own task falls under it. And when AI agents split work, each one sees only a piece.

**[The question]**

> So I asked: if an agent is told "never reveal this secret", does it matter whether it can see that its piece belongs to that secret? And does splitting the job across agents make a leak more likely?

**[Four redacted words and the synthetic rule]**

> I built a harmless test, a benign proxy. The secret is a made-up, four-word vault passphrase. Each word is a simple lookup, and each list can go to a different agent. A synthetic rule in the prompt says: never reveal the passphrase, not even one word.

**[`fig1_topologies.png`: the team shapes]**

> I ran the same task with one agent, one agent with up to twelve retries, a pipeline, a shared message board, and a coordinator relaying requests. Scoring is plain text matching, with no AI judge, on fresh test seeds.

**[Study 1 heatmap: the 19/20 and 0/20 solo cells marked]**

> Study one used Claude Haiku, twenty seeds per setting. Under the rule, a single agent that wasn't told what the words were for still wrote out the passphrase nineteen times in twenty. When the prompt said they were passphrase parts, it was zero in twenty, even with twelve tries. So framing strongly changed whether the agent followed the rule.

**[Assembled and recoverable heatmaps side by side]**

> Did splitting the task leak more? No split assembled the passphrase more often than an equally uninformed single agent. But separate posts often left all four words recoverable, even when nobody joined them. So I measure both.

**[Study 2 pipeline diagram]**

> Study two tested a fix. In a separate experiment, frozen before I collected the data, every agent in a fixed pipeline got the original task purpose as trusted metadata. Fifty fresh seeds.

**[45/50 → 0/50 and 15/50 → 33/49]**

> On restricted tasks, recoverable passphrases dropped from forty-five of fifty to zero. On authorized tasks, completion rose from fifteen of fifty to thirty-three of forty-nine.

**[Study 2 chart: monitor and keyword-gate rows marked]**

> Two filters did worse. A keyword gate missed reworded requests and blocked legitimate ones. An AI monitor allowed no legitimate completions at all.

**[Takeaway]**

> So evaluations should check whether each agent gets enough context to apply a rule, what others can reconstruct from its outputs, and whether useful work still gets done.

**[Limits]**

> The limits: one model family, one harmless task, and trusted purpose information from my own harness. This does not show protection against real harmful tasks or forged metadata, and zero in fifty is not a guarantee.

**[What's next]**

> What's next: replication on other models and providers, varied wording, forged metadata, and larger, asynchronous swarms.

**[Repo URL and QR code]**

> The code, data and report are all on GitHub. Thanks for watching.

---

## If you run long

The picture is cut to this script at about 150 words/min. If your read is slower, cut in this order:
1. "even with twelve tries" (about 2 s)
2. "on fresh test seeds" (about 1 s)
3. The two filter sentences after "Two filters did worse." (about 6 s)

Keep the what's-next line: the organisers ask the video to cover what's next.

## Say this, not that

- Say "rule" and "followed the rule". The report measures instruction following, not refusal of real harmful requests.
- Say "no split assembled it more often than an equally uninformed single agent". Don't say "splitting is safe" or "agents become unsafe together".
- Say "dropped to zero in fifty", not "eliminated" or "prevented".
- Don't say purpose matters *more* than the rule (claim audit).
- Don't read out the passphrase words from any example.
- Don't present the SAE follow-up as a result. The report calls it unimplemented.
- Leave out the METR incident. The report says this experiment does not explain it.

## Number sources

- Study 1 (frozen v2, Haiku 5.5, seeds 1000–1019): solo strict/neutral assembled 19/20; solo and `solo@k12` strict/explicit 0/20: `experiments/composition-gap/results/v2/analysis.md`. "No split condition has a higher observed assembly rate than an equally uninformed solo agent, although separate posts often leave the words recoverable": final report abstract and §6.1.
- Study 2 (task-provenance held-out, Haiku 5.5, seeds 3000–3049, freeze `435d20d`): restricted/paraphrase recoverable 45/50 → 0/50; authorized/paraphrase assembled 15/50 → 33/49 (one failed trial excluded); keyword gate restricted/paraphrase 46/50 recoverable and authorized/keyword 0/50 assembled; LLM monitor 0/50 authorized assembly in each wording: `docs/findings/provenance-heldout.md` and the final report abstract.
- Takeaway, limits and future work: final report abstract and §7 Conclusion.
