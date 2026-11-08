# LA hub video (picture edit)

Picture-only cut of the 3-minute LA hub video, timed to `report/video-narration.md`. The voiceover is recorded separately in the presenter's own voice; the LA submission requires this.

| File | Use |
|---|---|
| `swarm-composition-video.mp4` | Clean cut for submission. 1920×1080, 30 fps, H.264, 2:57.0, with a silent stereo AAC track to replace with the voiceover. |
| `swarm-composition-video-guide.mp4` | The same cut with each narration paragraph shown in a yellow bar at the bottom. Play it while recording so you can read to picture. Do not submit it. |
| `narration.srt` | The narration as timed captions. Use them as recording cues, or attach them as subtitles. |
| `make_video.py` | Rebuilds both videos from the narration and `report/figures/`. Run `python3 report/video/make_video.py` (needs Pillow, qrcode and ffmpeg). |

## Timing sheet (about 150 words/min)

| Start | Length | Words | Shot | On screen |
|---|---|---|---|---|
| 0:00.0 | 11.5 s | 27 | title | "Who Knows the Goal?", team, track |
| 0:11.5 | 15.9 s | 38 | question | The two research questions |
| 0:27.4 | 19.1 s | 46 | setup | Four redacted words and the synthetic rule ("benign proxy") |
| 0:46.4 | 16.3 s | 39 | topologies | `fig1_topologies.png` |
| 1:02.7 | 24.3 s | 59 | study1 | Haiku heatmap with the 19/20 and 0/20 cells marked |
| 1:27.0 | 15.5 s | 37 | split | Assembled and recoverable heatmaps; pipeline 2/20 vs 19/20 marked |
| 1:42.4 | 13.5 s | 32 | study2_design | Top of `fig5_provenance_design.png` |
| 1:55.9 | 10.7 s | 25 | study2_numbers | 45/50 → 0/50 and 15/50 → 33/49 |
| 2:06.6 | 9.9 s | 23 | filters | `fig4_provenance_heldout.png` with the monitor and keyword-gate rows marked |
| 2:16.5 | 11.9 s | 28 | takeaway | Three things to evaluate together (report §7) |
| 2:28.3 | 15.1 s | 36 | limits | Five limits |
| 2:43.4 | 7.1 s | 16 | next | Future work from the report |
| 2:50.5 | 6.5 s | 12 | end | Repo URL and QR code |

The total is 2:57.0 (narration of 431 words at about 155 words/min). That leaves 3 seconds under the 3:00 cap. If you need more room, use the cut list in `report/video-narration.md`.

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
