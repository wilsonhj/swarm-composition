# Swarm Alignment Hackathon 2026 - overview

Sources (both fetched successfully on 2026-11-06):
- AIAF page: https://aialignmentfoundation.org/hackathons/swarm-alignment-2026 (called "AIAF page" below)
- Apart page: https://apartresearch.com/sprints/swarm-alignment-2026 (called "Apart page" below)

Both pages say details are subject to change (AIAF page). Re-check before each deadline.

## Key deadlines

Nov 8 2026 falls after US daylight saving ended (Nov 1), so Pacific Time = PST = UTC-8. AoE = UTC-12. Conversions are my arithmetic; the pages give the PT / AoE times only (Apart page gives PT/UTC pairs for talks that agree with PST = UTC-8).

| Deadline | Pacific (PST) | AoE | UTC |
|---|---|---|---|
| LA hub: 3-minute video | Sun Nov 8, 10:00 AM | Sun Nov 8, 06:00 | Sun Nov 8, 18:00 |
| Global: research report (PDF) | Sun Nov 8 at 23:59 AoE = Mon Nov 9, 03:59 AM | Sun Nov 8, 23:59 | Mon Nov 9, 11:59 |

Other LA times that day (all PT, AIAF page): office opens 9:00 AM; judges' selection + brunch 10-11 AM; top 15 announced 11 AM-12 PM; presentations + live voting 12-3 PM; winners + wrap-up 3-3:45 PM. Each of the top 15 gives a 10-minute presentation.

Source: AIAF page.

## What the event is

Swarm Alignment Hackathon, Nov 6-8 2026. Free to enter. A global (online) sprint that everyone joins, judged after the weekend, plus an opt-in in-person LA hub round with its own live judging and prizes. The same project can be submitted to both rounds. (AIAF page.) The Apart page describes it as online with optional in-person hubs, and lists other local sites (Cape Town, Melbourne, Atlanta, Montreal, Calgary, Toronto, Warwick).

Both pages frame it as a response to a reported July 2026 incident in which about 1,200 agents coordinated and about 700 took part in an attack on Hugging Face (attributed to METR's investigation). I did not verify this claim.

## Organisers

- AI Alignment Foundation (AIAF), a 501(c)(3) nonprofit; Apart Research is co-organiser; AE Studio is the partner hosting the LA hub (AIAF page).
- Apart page: "Apart Research and AI Alignment Foundation, in partnership with AE Studio"; Adaption is also listed as a partner.

## LA hub logistics (AIAF page unless noted)

- Venue: AE Studio, Los Angeles. Seats limited. No street address is given on either page.
- LA hub registration: https://aialignmentfoundation.org/hackathons/swarm-alignment-2026/register?join=la
- Apart page: LA participants are automatically entered into the global sprint too.
- Schedule (PT):
  - Fri Nov 6: 9:00-12:30 AIAF Fellowship Demo Day (public); 12:30-1:30 lunch; 1:30-2:30 kickoff; 2:30-3:30 logistics and brief; 3:30-6:00 office open, hacking begins.
  - Sat Nov 7: 9:00 AM-5:00 PM office open.
  - Sun Nov 8: see Key deadlines.
- Apart page also lists online talks (Zoom, RSVP on Luma, recordings on the Schedule tab and Discord), e.g. Fri Nov 6 1:30 PM PT kickoff keynote by Judd Rosenblatt; Sat Nov 7 5:00 AM PT Justin Shenk; Sat 11:00 AM PT Jurgis Kemeklis.

## Teams

Solo or up to five (AIAF page); Apart page says up to 5 recommended, larger allowed, and each person on at most two projects. See judging-and-rules.md.

## Tracks

Participants pick one anchor track; cross-track work is welcome (both pages). Track names differ slightly between pages.

| # | Name (AIAF page) | Apart page name | Focus |
|---|---|---|---|
| 1 | Sandboxes & testbeds | Sandboxes and Testbeds | Reproducible environments for studying agent populations, containment, how well cheap models proxy frontier ones |
| 2 | The science of agent networks | The Science of Agent Networks | How leaders/roles/failures emerge; whether agents that refuse a harmful task will complete it when split across them (AIAF); "task splitting that evades per-agent refusals" (Apart); spread of compromise by network shape |
| 3 | Strengthening agent infrastructure | Strengthening Agent Infrastructure | Identity, reputation, commitments when agents can copy/rename; attacks on protocols such as A2A |
| 4 | Oversight & monitoring | Multi-Agent Oversight and Control | Detecting coordination, collusion, covert channels in real swarm logs; oversight when logs can be edited; partial-view monitors |

Neither page states a per-track "what judges look for"; judging is by common criteria (see judging-and-rules.md). Our project is Track 2; the "split harmful task" prompt on the AIAF page matches the composition-gap study.

## Prizes

Global (cash, both pages agree): 1st $2,000; 2nd $1,000; 3rd $600; 4th $200; 5th $200 (total $4,000). Apart page adds $1,000 in Adaption credits for every member of a winning team, and a referral bonus (if someone you refer wins, you get the same amount; terms at the refer link below).

LA hub (AIAF page): 1st $2,000 + podcast guest spot; 2nd $1,000; 3rd $500; 4th $300; 5th $200 (total $4,000). The page says all 15 presenting teams receive a prize, but lists no amounts for 6th-15th and a "Non-cash prizes" heading with no details. Apart page: LA is "an extra $4,000 pool, plus a local winner".

Non-cash for winners (Apart page): fast-track consideration for the Apart Fellowship (not guaranteed admission), mentor introductions, route to a publishable write-up.

## Compute and credits

- $250 compute credit for in-person LA participants (AIAF page only; not mentioned on the Apart page; remote not mentioned). Nothing on either page about how it is delivered or that it works via OpenRouter - see Unconfirmed.
- $500 Adaption Platform credits plus three months Premium for all participants (Apart page). Claim at https://adaptionlabs.ai/app using the same email as sprint sign-up; onboarding email sent before the event. Tools: AutoScientist, Adaptive Data, Invent-a-Dataset.

## Data and resources (Apart page)

- Swarm Traces: https://swarmtraces.org/ (investigation and redacted dataset of 80,000+ reconstructed attack payloads)
- AI Village dataset: https://huggingface.co/datasets/aidigestorg/ai-village (170,000+ agent messages, 2M+ computer-use turns). The page does not say it is gated.
- Transluce agent activity logs: https://transluce.org/agent-activity
- swarms.wiki: https://swarms.wiki/
- METR/Redwood report: https://metr.org/hugging-face-incident-report-aug-2026.pdf
- OpenAI disclosure: https://openai.com/hugging-face-incident-and-misalignment/
- ControlAI summary: https://blog.controlai.org/p/breaking-openais-rogue-ais-hit-over
- Reading list is on the Apart page / Resources tab (e.g. Multi-Agent Risks from Advanced AI, arXiv 2502.14143).

## Official links

| What | URL | Source |
|---|---|---|
| AIAF event page | https://aialignmentfoundation.org/hackathons/swarm-alignment-2026 | AIAF |
| Apart sprint page | https://apartresearch.com/sprints/swarm-alignment-2026 | Apart |
| Registration (global) | https://aialignmentfoundation.org/hackathons/swarm-alignment-2026/register | AIAF (relative link) |
| Registration (LA hub) | https://aialignmentfoundation.org/hackathons/swarm-alignment-2026/register?join=la | AIAF, Apart |
| Apart submission guidelines | https://apartresearch.com/sprints/swarm-alignment-2026#guidelines | AIAF |
| Report template (Google Doc copy link) | https://docs.google.com/document/d/1_1_27EyZriMlc8n8EBE2YScaeyMjm-8xjR097nmHXAE/copy?usp=sharing | Apart |
| Prize terms | https://apartresearch.com/sprints/prize-terms | Apart |
| Referral | https://apartresearch.com/sprints/swarm-alignment-2026/refer | Apart |
| Apart Fellowship | https://apartresearch.com/fellowships/apart-fellowship | Apart |
| Apart privacy policy | https://apartresearch.com/info/privacy-policy | Apart |
| AE Studio | https://ae.studio | AIAF |
| Contact | sprints@apartresearch.com | Apart |

## Discord

- https://discord.gg/XswWBvugYs - the Sprint Discord, per the Apart page (help desk: tag @Support; team-forming happens here; talk recordings shared here).
- https://discord.gg/THWK7ZumW - NOT found on either page. Context unknown; came from the registration email only.
- Also on the Apart page (for reference, not from our email): Apart general Discord https://discord.gg/dYUWDm7Ben; Adaption Discord https://discord.gg/8hjcFWY8.

## Unconfirmed (from registration email / earlier notes)

- Discord invite https://discord.gg/THWK7ZumW: not on either page.
- "Moltbook" as a suggested dataset: not on either page.
- "AI Village dataset is gated" on Hugging Face: not stated on the page (access not checked).
- "Raw METR incident logs are not public": not stated on either page.
- Using the $250 compute credit via OpenRouter: neither page says how credits are issued or redeemed.
- LA video submission mechanism (where/how to upload): not on either page.
- Whether $250 compute is for LA in-person only: AIAF page says "in-person LA participants" and is silent on others.
