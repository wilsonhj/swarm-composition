# LA hub video (picture edit)

Picture-only cut of the 3-minute LA hub video, timed to `report/video-narration.md`. The voiceover is recorded separately in the presenter's own voice; the LA submission requires this.

| File | Use |
|---|---|
| `swarm-composition-video.mp4` | Clean cut for submission. 1920×1080, 30 fps, H.264, 2:53.3, with a silent stereo AAC track to replace with the voiceover. |
| `swarm-composition-video-guide.mp4` | The same cut with each narration paragraph shown in a yellow bar at the bottom. Play it while recording so you can read to picture. Do not submit it. |
| `narration.srt` | The narration as timed captions. Use them as recording cues, or attach them as subtitles. |
| `make_video.py` | Rebuilds both videos from the narration and `report/figures/`. Run `python3 report/video/make_video.py` (needs Pillow, qrcode and ffmpeg). |

## Timing sheet (about 150 words/min)

| Start | Length | Words | Shot | On screen |
|---|---|---|---|---|
| 0:00.0 | 7.1 s | 16 | title | "Who Knows the Goal?", team, track |
| 0:07.1 | 16.3 s | 39 | question | The two research questions |
| 0:23.4 | 20.3 s | 49 | setup | Four redacted words and the synthetic rule ("benign proxy") |
| 0:43.7 | 18.3 s | 44 | topologies | `fig1_topologies.png` |
| 1:02.0 | 24.3 s | 59 | study1 | Haiku heatmap with the 19/20 and 0/20 cells marked |
| 1:26.3 | 15.9 s | 38 | split | Heatmap with the relay 1/20 cell marked: no significant gap |
| 1:42.2 | 13.5 s | 32 | study2_design | Top of `fig5_provenance_design.png` |
| 1:55.7 | 10.7 s | 25 | study2_numbers | 45/50 → 0/50 and 15/50 → 33/49 |
| 2:06.4 | 9.5 s | 22 | filters | `fig4_provenance_heldout.png` with the monitor and keyword-gate rows marked |
| 2:15.9 | 11.9 s | 28 | takeaway | "Compliance tracked what each agent was told about the goal." |
| 2:27.8 | 12.3 s | 29 | limits | Four limits |
| 2:40.1 | 6.7 s | 15 | next | What's next (the organisers ask for it) |
| 2:46.8 | 6.5 s | 12 | end | Repo URL and QR code |

The total is 2:53.3. That leaves about 7 seconds under the 3:00 cap.

## Adding the voiceover

1. Record while the guide video plays, reading each paragraph while its shot is on screen. Save the recording as `voiceover.wav` (or `.m4a`), starting at 0:00.
2. Replace the silent track with your recording. The picture is not re-encoded:

```bash
ffmpeg -i report/video/swarm-composition-video.mp4 -i voiceover.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest report/video/swarm-composition-final.mp4
```

If your read runs slower than the picture, re-time it in any editor: the end card can hold longer, as long as the total stays under 3:00. You can also cut the lines listed under "If you run long" in `report/video-narration.md`.

## Content checks

- Every on-screen number matches `report/video-narration.md` and its sources: `experiments/composition-gap/results/v2/analysis.md` and `docs/findings/provenance-heldout.md`. The figures are the committed ones in `report/figures/`.
- The passphrase words are never shown, only redacted blocks.
- The wording follows `docs/research/claim-audit.md`: no significant gap is claimed for splitting, there is no "purpose matters more than the rule", and zero in fifty is described as not a guarantee.
