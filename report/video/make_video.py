"""Build the 3-minute LA hub video (picture only) from report/video-narration.md.

Each narration paragraph gets one shot. Shot length comes from the paragraph's
word count at PACE words/second plus a short pause, so the narrator can read
to picture. Outputs (in report/video/):

  swarm-composition-video.mp4        clean cut, silent audio track, for submission
  swarm-composition-video-guide.mp4  same cut with the narration burned in as a prompter
  narration.srt                      captions / recording cues
  frames/                            the rendered stills (not committed)

Usage: python3 report/video/make_video.py   (needs Pillow, qrcode, ffmpeg)
Numbers on screen are copied from frozen-run sources listed in video-narration.md.
"""
import os, re, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont
import qrcode

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "report", "video")
FR = os.path.join(OUT, "frames")
FIG = os.path.join(ROOT, "report", "figures")
W, H, FPS = 1920, 1080, 30
PACE = 2.5        # words per second (~150 wpm)
PAUSE = 0.7       # seconds of breathing room per paragraph
XF = 0.5          # crossfade length
MAX_TOTAL = 177.0 # hard cap is 180 s
REPO = "github.com/wilsonhj/swarm-composition"

BG, PANEL, INK, MUTED = (14, 26, 36), (255, 255, 255), (236, 242, 245), (150, 168, 180)
ACCENT, LEAK, SAFE, MARK = (99, 181, 189), (226, 128, 95), (109, 194, 141), (255, 196, 0)
FONT_DIR = "/usr/share/fonts/opentype/inter/"
def F(name, size): return ImageFont.truetype(FONT_DIR + name, size)
DISP, BOLD, SEMI, REG = "InterDisplay-Bold.otf", "Inter-Bold.otf", "Inter-SemiBold.otf", "Inter-Regular.otf"


def narration():
    text = open(os.path.join(ROOT, "report", "video-narration.md"), encoding="utf-8").read()
    paras, cur = [], []
    for line in text.splitlines():
        if line.startswith(">"):
            body = line[1:].strip()
            if body:
                cur.append(body)
            elif cur:
                paras.append(" ".join(cur)); cur = []
        elif cur:
            paras.append(" ".join(cur)); cur = []
    if cur:
        paras.append(" ".join(cur))
    return paras


# ---------- drawing helpers ----------
def canvas():
    im = Image.new("RGB", (W, H), BG)
    return im, ImageDraw.Draw(im)

def wrap(d, xy, text, font, fill, width_px, spacing=14):
    words, lines, line = text.split(), [], ""
    for w in words:
        t = (line + " " + w).strip()
        if d.textlength(t, font=font) <= width_px:
            line = t
        else:
            lines.append(line); line = w
    lines.append(line)
    x, y = xy
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += font.size + spacing
    return y

def eyebrow(d, text, y=90, color=ACCENT):
    d.text((120, y), text.upper(), font=F(SEMI, 30), fill=color)

def footer(d, text="Benign proxy · synthetic rule · numbers from frozen runs"):
    d.text((120, H - 70), text, font=F(REG, 24), fill=MUTED)

def paste_fig(im, path, box, crop=None, marks=(), pad=24):
    """Place a figure on a white rounded panel inside box=(x0,y0,x1,y1); marks are
    rectangles in the figure's original pixel coordinates."""
    fig = Image.open(path).convert("RGB")
    dd = ImageDraw.Draw(fig)
    for (x0, y0, x1, y1, col) in marks:
        dd.rounded_rectangle((x0, y0, x1, y1), radius=14, outline=col, width=10)
    if crop:
        fig = fig.crop(crop)
    bx0, by0, bx1, by1 = box
    s = min((bx1 - bx0 - 2 * pad) / fig.width, (by1 - by0 - 2 * pad) / fig.height)
    fig = fig.resize((int(fig.width * s), int(fig.height * s)), Image.LANCZOS)
    pw, ph = fig.width + 2 * pad, fig.height + 2 * pad
    px, py = bx0 + (bx1 - bx0 - pw) // 2, by0 + (by1 - by0 - ph) // 2
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((px, py, px + pw, py + ph), radius=22, fill=PANEL)
    im.paste(fig, (px + pad, py + pad))


# ---------- shots (one per narration paragraph) ----------
def s_title():
    im, d = canvas()
    eyebrow(d, "Swarm Alignment Hackathon 2026 · LA hub · Track 2", y=300)
    d.text((120, 360), "Who Knows the Goal?", font=F(DISP, 120), fill=INK)
    wrap(d, (120, 520), "Local context, task purpose and restricted assembly when work is split across AI agents",
         F(REG, 44), MUTED, 1500)
    d.text((120, 760), "Hirokazu James Wilson · Team HJ", font=F(SEMI, 36), fill=INK)
    return im

def s_question():
    im, d = canvas()
    eyebrow(d, "The question")
    wrap(d, (120, 200), "An agent is told: “never reveal this secret.”", F(DISP, 64), INK, 1680)
    y = wrap(d, (120, 380), "1.  Does it matter whether the agent can see that its small piece belongs to the secret?",
             F(SEMI, 48), INK, 1600)
    wrap(d, (120, y + 40), "2.  Does splitting the job across agents make a leak more likely?", F(SEMI, 48), INK, 1600)
    footer(d, "Safety tests usually check one agent at a time. Real agents increasingly work in teams.")
    return im

def s_setup():
    im, d = canvas()
    eyebrow(d, "A harmless test")
    d.text((120, 170), "A made-up, four-word vault passphrase", font=F(DISP, 60), fill=INK)
    for i in range(4):
        x = 120 + i * 430
        d.rounded_rectangle((x, 300, x + 390, 470), radius=18, outline=MUTED, width=3)
        d.text((x + 30, 320), f"list {i + 1} → word {i + 1}", font=F(REG, 30), fill=MUTED)
        d.text((x + 30, 375), "■■■■■■", font=F(BOLD, 52), fill=INK)
    d.rounded_rectangle((120, 560, 1800, 720), radius=18, fill=(30, 46, 60))
    d.text((160, 585), "SYNTHETIC RULE IN THE PROMPT", font=F(SEMI, 26), fill=LEAK)
    d.text((160, 630), "“Never reveal the vault passphrase, not even one word.”", font=F(SEMI, 46), fill=INK)
    wrap(d, (120, 790), "Each word is a simple lookup in a short list. Each list can go to a different agent. "
         "Scoring is plain text matching, with no AI judge.", F(REG, 36), MUTED, 1680)
    return im

def s_topologies():
    im, d = canvas()
    eyebrow(d, "Same task, different team shapes", y=50)
    paste_fig(im, os.path.join(FIG, "fig1_topologies.png"), (90, 100, 1830, 1000))
    footer(d, "Solo with up to 12 retries matches the call budget of the larger teams · fresh test seeds · every run logged")
    return im

def s_study1():
    im, d = canvas()
    eyebrow(d, "Study 1 · Claude Haiku · 20 seeds per setting · strict rule")
    # Haiku 'assembled' panel; marks in original pixels: solo strict/neutral, solo strict/explicit, solo@k12 strict/explicit
    marks = [(773, 236, 935, 324, LEAK), (944, 236, 1106, 324, SAFE), (944, 429, 1106, 517, SAFE)]
    paste_fig(im, os.path.join(FIG, "fig2_v2_heatmap.png"), (80, 150, 1080, 1010),
              crop=(30, 60, 1165, 1010), marks=marks)
    x = 1150
    d.text((x, 230), "19/20", font=F(DISP, 120), fill=LEAK)
    wrap(d, (x, 370), "wrote out the passphrase when not told what the words were for", F(REG, 34), INK, 660)
    d.text((x, 560), "0/20", font=F(DISP, 120), fill=SAFE)
    wrap(d, (x, 700), "when told they were passphrase parts, even with 12 tries", F(REG, 34), INK, 660)
    wrap(d, (x, 870), "Wording strongly changed refusal.", F(SEMI, 34), ACCENT, 660)
    return im

def s_split():
    im, d = canvas()
    eyebrow(d, "Did splitting the task leak more?")
    marks = [(944, 913, 1106, 1001, MARK)]  # relay_uninformed strict/explicit (Haiku 1/20)
    paste_fig(im, os.path.join(FIG, "fig2_v2_heatmap.png"), (80, 150, 1080, 1010),
              crop=(30, 60, 1165, 1010), marks=marks)
    x = 1150
    wrap(d, (x, 240), "No statistically significant gap", F(DISP, 62), INK, 680)
    y = wrap(d, (x, 440), "A few relay runs did leak, in Haiku (1/20 here) and in Sonnet.", F(REG, 36), INK, 660)
    wrap(d, (x, y + 30), "No split leaked more often than a single agent given the same unstated goal.",
         F(SEMI, 36), ACCENT, 660)
    return im

def s_study2_design():
    im, d = canvas()
    eyebrow(d, "Study 2 · separate experiment · protocol frozen before data collection", y=60)
    paste_fig(im, os.path.join(FIG, "fig5_provenance_design.png"), (90, 110, 1830, 900), crop=(0, 0, 2340, 900))
    wrap(d, (120, 930), "Every agent in the pipeline gets the trusted purpose of the task. 50 fresh seeds, Claude Haiku.",
         F(SEMI, 38), INK, 1700)
    return im

def s_study2_numbers():
    im, d = canvas()
    eyebrow(d, "Study 2 · paraphrased objective · without vs with the task's purpose")
    rows = [("Restricted task: passphrase recoverable", "45/50", "0/50", SAFE, "lower is safer"),
            ("Legitimate task: completed", "15/50", "33/49", SAFE, "higher is better")]
    y = 230
    for label, a, b, col, note in rows:
        d.text((120, y), label, font=F(SEMI, 44), fill=INK)
        d.text((120, y + 60), note, font=F(REG, 28), fill=MUTED)
        d.text((120, y + 120), a, font=F(DISP, 150), fill=MUTED)
        d.text((600, y + 150), "→", font=F(DISP, 110), fill=MUTED)
        d.text((820, y + 120), b, font=F(DISP, 150), fill=col)
        y += 380
    footer(d, "1 of 800 trials failed (backend error) and is excluded, hence 49 · zero in fifty is not a guarantee")
    return im

def s_filters():
    im, d = canvas()
    eyebrow(d, "Two filters, tested alongside", y=50)
    # LLM monitor and keyword gate rows of fig4, original pixels
    marks = [(10, 560, 2210, 665, MARK), (10, 718, 2210, 820, MARK)]
    paste_fig(im, os.path.join(FIG, "fig4_provenance_heldout.png"), (90, 100, 1830, 830), marks=marks)
    wrap(d, (120, 860), "Keyword filter: missed reworded requests (46/50 still recoverable) and blocked keyword-worded legitimate ones.",
         F(REG, 34), INK, 1680, spacing=8)
    wrap(d, (120, 960), "AI monitor: blocked 792 of 795 messages, and completed 0/50 legitimate tasks.",
         F(REG, 34), INK, 1680)
    return im

def s_takeaway():
    im, d = canvas()
    eyebrow(d, "Takeaway")
    wrap(d, (120, 240), "In both studies, compliance tracked what each agent was told about the goal.",
         F(DISP, 78), INK, 1680, spacing=20)
    wrap(d, (120, 620), "Check how context moves through a team, not only how each agent behaves.",
         F(SEMI, 46), ACCENT, 1680)
    footer(d, "A finding about this benign proxy, not a general law")
    return im

def s_limits():
    im, d = canvas()
    eyebrow(d, "Limits")
    items = ["One model family", "One harmless, made-up task",
             "Purpose supplied by my own harness: forged context untested", "Zero in fifty is not a guarantee"]
    y = 230
    for it in items:
        d.ellipse((125, y + 22, 145, y + 42), fill=LEAK)
        d.text((180, y), it, font=F(SEMI, 54), fill=INK)
        y += 140
    return im

def s_end():
    im, d = canvas()
    eyebrow(d, "Code, data and report", y=300)
    d.text((120, 360), REPO, font=F(DISP, 66), fill=INK)
    d.text((120, 470), "Who Knows the Goal?  ·  Team HJ  ·  Track 2", font=F(REG, 38), fill=MUTED)
    d.text((120, 760), "Thanks for watching.", font=F(SEMI, 44), fill=ACCENT)
    q = qrcode.QRCode(border=2, box_size=12)
    q.add_data("https://" + REPO); q.make(fit=True)
    qi = q.make_image(fill_color="black", back_color="white").convert("RGB").resize((380, 380), Image.NEAREST)
    im.paste(qi, (1400, 560))
    return im

SHOTS = [s_title, s_question, s_setup, s_topologies, s_study1, s_split,
         s_study2_design, s_study2_numbers, s_filters, s_takeaway, s_limits, s_end]


def prompter(im, text):
    """Guide version: narration line in a bar at the bottom."""
    im = im.copy()
    d = ImageDraw.Draw(im, "RGBA")
    font = F(SEMI, 30)
    lines = textwrap.wrap(text, 110)
    h = 30 + len(lines) * 40
    d.rectangle((0, H - h - 10, W, H), fill=(0, 0, 0, 215))
    y = H - h
    for ln in lines:
        d.text((60, y), ln, font=font, fill=(255, 235, 140)); y += 40
    return im


def stamp(sec):
    ms = int(round(sec * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def encode(paths, durs, out):
    """Stills -> H.264 with crossfades and a silent stereo AAC track."""
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for p, dur in zip(paths, durs):
        args += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur + XF:.3f}", "-i", p]
    total = sum(durs) + XF  # every input carries +XF; n-1 crossfades remove (n-1)*XF
    args += ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
    fc, prev, off = [], "0:v", 0.0
    for i in range(1, len(paths)):
        off += durs[i - 1]
        fc.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{i}]")
        prev = f"v{i}"
    fc.append(f"[{prev}]fade=t=in:st=0:d=0.6,fade=t=out:st={total - 0.8:.3f}:d=0.8,format=yuv420p[vout]")
    args += ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{len(paths)}:a",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-tune", "stillimage", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    subprocess.run(args, check=True)


def main():
    paras = narration()
    assert len(paras) == len(SHOTS), (len(paras), len(SHOTS))
    durs = [len(p.split()) / PACE + PAUSE for p in paras]
    durs[0] = max(durs[0], 7.0)    # let the title card breathe
    durs[-1] = max(durs[-1], 6.0)  # hold the end card
    total = sum(durs) + XF
    if total > MAX_TOTAL:
        k = (MAX_TOTAL - XF) / sum(durs); durs = [x * k for x in durs]
    os.makedirs(FR, exist_ok=True)
    clean, guide = [], []
    for i, (shot, para) in enumerate(zip(SHOTS, paras)):
        im = shot()
        p1, p2 = os.path.join(FR, f"{i:02}.png"), os.path.join(FR, f"{i:02}_guide.png")
        im.save(p1); prompter(im, para).save(p2)
        clean.append(p1); guide.append(p2)
    t, srt, sheet = 0.0, [], []
    for i, (para, dur) in enumerate(zip(paras, durs)):
        srt.append(f"{i + 1}\n{stamp(t)} --> {stamp(t + dur)}\n{para}\n")
        sheet.append(f"| {int(t // 60)}:{t % 60:04.1f} | {dur:4.1f} s | {len(para.split())} | {SHOTS[i].__name__[2:]} |")
        t += dur
    open(os.path.join(OUT, "narration.srt"), "w", encoding="utf-8").write("\n".join(srt))
    encode(clean, durs, os.path.join(OUT, "swarm-composition-video.mp4"))
    encode(guide, durs, os.path.join(OUT, "swarm-composition-video-guide.mp4"))
    print(f"total {sum(durs) + XF:.1f} s")
    print("| start | length | words | shot |\n|---|---|---|---|\n" + "\n".join(sheet))


if __name__ == "__main__":
    main()
