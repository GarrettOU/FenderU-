#!/usr/bin/env python3
"""Content Studio builder, FenderU vertical videos from stills (9 Nov 2026).

Every on-screen line below is lifted verbatim from an approved source (see SRC
tags). A hook that is not an approved line is marked DRAFT and the build tags the
preview grid DRAFT. Photos are only Garrett's own (marketing/src/media_southern_g0*)
and the three Runway photos he kept (marketing/runway/clean/02, 03, 05). Photos
are only cropped and scaled (Lanczos); no filter, grade or redraw touches them.

Usage: python3 build_studio.py [VIDEO_ID ...]   (default: all)
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MK = os.path.dirname(HERE)
OUT = os.path.join(HERE, "2026-11-09", "fenderu")
FONT = os.path.join(MK, "fonts", "Oswald_700Bold.ttf")
FONT_MED = os.path.join(MK, "fonts", "Oswald_500Medium.ttf")
W, H, FPS = 1080, 1920, 30

# ---- sources ----------------------------------------------------------------
P = {
    "g01": "src/media_southern_g01-pair-portrait.jpg",
    "g02": "src/media_southern_g02-dock-square.jpg",
    "g03": "src/media_southern_g03-wake-surf-portrait.jpg",
    "g04": "src/media_southern_g04-detail-portrait.jpg",
    "r02": "runway/clean/02-red-express-cruiser-2200.jpg",
    "r03": "runway/clean/03-yellow-bowrider-2200.jpg",
    "r05": "runway/clean/05-teal-wakeboat-party-2200.jpg",
}
RUNWAY = {"r02", "r03", "r05"}

# ---- approved lines (verbatim) and where each comes from --------------------
SRC_CAP = "marketing/captions.md"
SRC_FACT = "fenderu-standing-rules, Facts you may state"
SRC_HQ = "HQ.md section 3"
END_PRICE = "$119 for the two-pack, free shipping."
END_SITE = "fenderu.com"

# Each video: id, title, hook (text, status, source), shots, caption key.
# shot = (photo, seconds, (fx, fy, zoom_from, zoom_to, dx), text, subtext)
#   fx, fy: focus point (0-1) in the photo; zoom 1.0 = largest 9:16 window;
#   dx: horizontal pan across the shot as a fraction of photo width.
BRANDS_SUB = 'STANDARD 8.5" x 26" CYLINDRICAL FENDERS'
VIDEOS = [
    dict(id="F1", title="Fit guide", caption="photo",
         hook=('FITS STANDARD 8.5" x 26" CYLINDRICAL FENDERS.', "APPROVED", SRC_CAP + " (photo post)"),
         shots=[
             ("g03", 2.8, (0.58, 0.55, 1.00, 1.07, 0), "HOOK", None),
             ("g04", 1.7, (0.45, 0.45, 1.00, 1.05, 0), "TAYLOR MADE", BRANDS_SUB),
             ("g01", 1.7, (0.60, 0.55, 1.06, 1.00, 0), "BASS PRO SHOPS", BRANDS_SUB),
             ("g02", 1.7, (0.45, 0.55, 1.00, 1.00, 0.10), "DOCK EDGE", BRANDS_SUB),
             ("g03", 1.7, (0.55, 0.62, 1.25, 1.32, 0), "SEACHOICE", BRANDS_SUB),
             ("g04", 1.7, (0.45, 0.55, 1.15, 1.08, 0), "EXTREME MAX BOATTECTOR", BRANDS_SUB),
             ("g01", 2.0, (0.62, 0.55, 1.00, 1.06, 0), "SOLD AS A 2-PACK.", None),
             ("END", 2.8, None, None, None),
         ],
         lines=[('Taylor Made / Bass Pro Shops / Dock Edge / Seachoice / Extreme Max BoatTector; "standard 8.5 x 26 cylindrical fenders"', SRC_FACT),
                ("Sold as a 2-pack.", SRC_CAP)]),
    dict(id="F2-A", title="Slips on, approved hook", caption="photo",
         hook=("SHOW YOUR PATRIOTISM.", "APPROVED", SRC_HQ + ", 9 Oct; " + SRC_CAP)),
    dict(id="F2-B", title="Slips on, DRAFT hook", caption="photo",
         hook=("SLIPS ON IN SECONDS. NO TOOLS.", "DRAFT", "research section F2, built from the approved fact 'slips on in seconds, no tools'; not yet approved as a hook")),
    dict(id="F3-A", title="POV push-in, approved hook", caption="reel",
         hook=("MARINE-GRADE NEOPRENE, FLAG PRINT.", "APPROVED", SRC_CAP + " (reel caption)")),
    dict(id="F3-B", title="POV push-in, DRAFT hook", caption="reel",
         hook=("MARINE-GRADE NEOPRENE. AMERICAN FLAG AND MAGA PRINT.", "DRAFT", "research section F3 with the banned 'edge to edge' removed; not yet approved")),
    dict(id="F4", title="Who you're buying from", caption="group",
         hook=("AMERICAN-OWNED AND OPERATED.", "APPROVED", SRC_CAP + " (group post)"),
         shots=[
             ("g01", 2.8, (0.60, 0.52, 1.00, 1.07, 0), "HOOK", None),
             ("g04", 2.2, (0.45, 0.45, 1.00, 1.06, 0), "THE OWNER ANSWERS HIS OWN EMAIL.", None),
             ("g03", 2.2, (0.58, 0.58, 1.10, 1.02, 0), "IF IT DOESN'T FIT, HE'LL TAKE THE RETURN.", None),
             ("g02", 2.0, (0.40, 0.55, 1.00, 1.00, 0.12), "QUESTIONS WELCOME.", None),
             ("END", 2.8, None, None, None),
         ],
         lines=[("the owner answers his own email; if it doesn't fit, he'll take the return", SRC_FACT),
                ("Questions welcome.", SRC_CAP)]),
    dict(id="F5-A", title="Fact carousel, approved hook", caption="group",
         hook=("MAGA FENDER COVERS", "APPROVED", SRC_CAP + " (group post first line); set3 g6 graphic")),
    dict(id="F5-B", title="Fact carousel, DRAFT hook", caption="group",
         hook=("BOAT FENDER COVERS, SOLD AS A 2-PACK.", "DRAFT", "research section F5 slide 1; 'boat fender covers' is not an approved phrase")),
]

F2_SHOTS = [
    ("g03", 2.8, (0.58, 0.55, 1.00, 1.07, 0), "HOOK", None),
    ("g04", 2.0, (0.45, 0.40, 1.00, 1.06, 0), "SLIPS ON IN SECONDS, NO TOOLS.", None),
    ("g04", 2.0, (0.45, 0.30, 1.30, 1.22, 0), "ELASTIC TOP.", None),
    ("g01", 2.0, (0.60, 0.55, 1.06, 1.00, 0), "MARINE-GRADE NEOPRENE.", None),
    ("g02", 2.0, (0.42, 0.55, 1.00, 1.00, 0.10), "UV PROTECTED, WATERPROOF, SALT-RESISTANT.", None),
    ("END", 2.8, None, None, None),
]
F2_LINES = [("slips on in seconds, no tools; elastic top", SRC_FACT),
            ("Marine-grade neoprene. / UV protected, waterproof, salt-resistant.", SRC_CAP)]
F3_SHOTS = [
    ("r02", 2.8, (0.77, 0.68, 1.00, 1.08, 0), "HOOK", None),
    ("r03", 2.0, (0.62, 0.72, 1.00, 1.06, 0), "MAKE AMERICA GREAT AGAIN", None),
    ("r05", 2.0, (0.30, 0.62, 1.06, 1.00, 0), "SOLD AS A 2-PACK.", None),
    ("g03", 2.2, (0.58, 0.55, 1.00, 1.06, 0), None, None),
    ("END", 2.8, None, None, None),
]
F3_LINES = [("Make America Great Again", SRC_HQ + ", 9 Oct"), ("Sold as a 2-pack.", SRC_CAP)]
F5_SHOTS = [
    ("g03", 2.8, (0.58, 0.55, 1.00, 1.07, 0), "HOOK", None),
    ("g04", 2.2, (0.45, 0.45, 1.00, 1.06, 0), "UV PROTECTED, WATERPROOF, SALT-RESISTANT.", None),
    ("g01", 2.2, (0.60, 0.55, 1.06, 1.00, 0), "KEEPS DOCK GRIT OFF THE HULL.", None),
    ("g02", 2.2, (0.42, 0.55, 1.00, 1.00, 0.10), "30-DAY RETURNS.", None),
    ("END", 2.8, None, None, None),
]
F5_LINES = [("UV protected, waterproof, salt-resistant.", SRC_CAP),
            ("keeps dock grit off the hull; 30-day returns", SRC_FACT)]
for v in VIDEOS:
    if v["id"].startswith("F2"): v["shots"], v["lines"] = list(F2_SHOTS), F2_LINES
    if v["id"] == "F2-B":
        v["shots"][1] = ("g04", 2.0, (0.45, 0.40, 1.00, 1.06, 0), "KEEPS DOCK GRIT OFF THE HULL.", None)
        v["lines"] = F2_LINES + [("keeps dock grit off the hull", SRC_FACT)]
    if v["id"].startswith("F3"): v["shots"], v["lines"] = F3_SHOTS, F3_LINES
    if v["id"].startswith("F5"): v["shots"], v["lines"] = F5_SHOTS, F5_LINES
for v in VIDEOS:
    if v["id"] == "F5-A":
        v["hook_sub"] = "MARINE-GRADE NEOPRENE, SOLD AS A 2-PACK."

# ---- pack of 11 Nov 2026: hooks P1, P2, P3, P5, P6 from launch-plan.md ------
# Approved by Garrett 6 Nov ("Approve the post.", HQ.md section 3); P5 and P6
# confirmed approved by SI Claude Head on 9 Nov.
SRC_LP = "launch-plan.md section 3; approved 6 Nov (HQ.md section 3)"
FIT = 'FITS STANDARD 8.5" x 26" CYLINDRICAL FENDERS.'
VIDEOS_1111 = [
    dict(id="G1", title="They haven't seen these", caption="reel",
         hook=("THEY HAVEN'T SEEN THESE YET.", "APPROVED", "P1, " + SRC_LP),
         shots=[("g03", 2.8, (0.62, 0.50, 1.04, 1.12, 0), "HOOK", None),
                ("g04", 2.0, (0.45, 0.50, 1.10, 1.02, 0), "MARINE-GRADE NEOPRENE, FLAG PRINT.", None),
                ("g01", 2.0, (0.58, 0.55, 1.00, 1.00, -0.08), "SOLD AS A 2-PACK.", None),
                ("g02", 2.0, (0.50, 0.55, 1.08, 1.02, 0), FIT, None),
                ("END", 2.8, None, None, None)],
         lines=[("Marine-grade neoprene, flag print. / Sold as a 2-pack. / " + FIT, SRC_CAP)]),
    dict(id="G2", title="Bare fenders", caption="photo",
         hook=("BARE FENDERS ARE A WASTED OPPORTUNITY.", "APPROVED", "P2, " + SRC_LP + "; Facebook rotation item 8"),
         shots=[("g01", 2.8, (0.60, 0.52, 1.00, 1.08, 0), "HOOK", None),
                ("g03", 2.0, (0.55, 0.60, 1.18, 1.10, 0), "SHOW YOUR PATRIOTISM.", None),
                ("g04", 2.0, (0.45, 0.35, 1.00, 1.07, 0), "SLIPS ON IN SECONDS, NO TOOLS.", None),
                ("g02", 2.0, (0.38, 0.55, 1.00, 1.00, 0.12), "KEEPS DOCK GRIT OFF THE HULL.", None),
                ("END", 2.8, None, None, None)],
         lines=[("Show your patriotism.", SRC_CAP), ("slips on in seconds, no tools; keeps dock grit off the hull", SRC_FACT)]),
    dict(id="G3", title="Right down to the fenders (Runway)", caption="reel",
         hook=("MAKE AMERICA GREAT AGAIN, RIGHT DOWN TO THE FENDERS.", "APPROVED", "P3, " + SRC_LP + "; reel caption"),
         shots=[("r05", 2.8, (0.30, 0.64, 1.00, 1.08, 0), "HOOK", None),
                ("r02", 2.0, (0.77, 0.70, 1.08, 1.00, 0), "MARINE-GRADE NEOPRENE.", None),
                ("r03", 2.0, (0.62, 0.74, 1.00, 1.06, 0), "UV PROTECTED, WATERPROOF, SALT-RESISTANT.", None),
                ("g03", 2.0, (0.58, 0.55, 1.06, 1.00, 0), "SOLD AS A 2-PACK.", None),
                ("END", 2.8, None, None, None)],
         lines=[("Marine-grade neoprene. / UV protected, waterproof, salt-resistant. / Sold as a 2-pack.", SRC_CAP)]),
    dict(id="G4", title="Plain white fenders", caption="group",
         hook=("PLAIN WHITE FENDERS ON A MAGA BOAT?", "APPROVED", "P5, " + SRC_LP + "; confirmed by SI Claude Head 9 Nov"),
         shots=[("g02", 2.8, (0.45, 0.55, 1.00, 1.06, 0), "HOOK", None),
                ("g04", 2.0, (0.45, 0.45, 1.00, 1.06, 0), "MAGA FENDER COVERS", "MARINE-GRADE NEOPRENE, SOLD AS A 2-PACK."),
                ("g01", 2.0, (0.62, 0.55, 1.06, 1.00, 0), FIT, None),
                ("g03", 2.0, (0.58, 0.58, 1.00, 1.06, 0), "SLIPS ON IN SECONDS, NO TOOLS.", None),
                ("END", 2.8, None, None, None)],
         lines=[("MAGA fender covers — marine-grade neoprene, sold as a 2-pack. / " + FIT, SRC_CAP), ("slips on in seconds, no tools", SRC_FACT)]),
    dict(id="G5", title="Boat dads", caption="photo",
         hook=("BOAT DADS ARE HARD TO BUY FOR.", "APPROVED", "P6, " + SRC_LP + "; confirmed by SI Claude Head 9 Nov"),
         shots=[("g01", 2.8, (0.58, 0.52, 1.00, 1.07, 0), "HOOK", None),
                ("g04", 2.0, (0.45, 0.42, 1.05, 1.00, 0), "MAGA FENDER COVERS", "MARINE-GRADE NEOPRENE, SOLD AS A 2-PACK."),
                ("g03", 2.0, (0.58, 0.55, 1.00, 1.06, 0), "IF IT DOESN'T FIT, HE'LL TAKE THE RETURN.", None),
                ("g02", 2.0, (0.42, 0.55, 1.00, 1.00, 0.10), "QUESTIONS WELCOME.", None),
                ("END", 2.8, None, None, None)],
         lines=[("MAGA fender covers — marine-grade neoprene, sold as a 2-pack. / Questions welcome.", SRC_CAP), ("if it doesn't fit, he'll take the return", SRC_FACT)]),
]
PACK = os.environ.get("STUDIO_PACK", "2026-11-09")
if PACK == "2026-11-11":
    VIDEOS = VIDEOS_1111
    OUT = os.path.join(HERE, "2026-11-11", "fenderu")

# ---- banned list (HQ.md section 3 wins over the skill) ------------------------
BANNED = [r"the pair", r"\busps\b", r"edge to edge", r"every dock", r"every marina", r"every parade",
          r"matched pair", r"port and starboard", r"\bfly\b", r"flying", r"flies", r"american-made",
          r"made in usa", r"madeinusa", r"full.?wrap", r"show your colors", r"48 ?h", r"limited",
          r"\brun\b", r"when they.re gone", r"paypal", r"venmo", r"cash app", r"stripe", r"\bcard\b",
          r"kansas", r"missouri", r"midwest", r"ships (from|within|in)", r"order by", r"5-star",
          r"★", r"both sides", r"made for american boats", r"shipped by", r"\$99", r"\$118",
          r"#americanmade", r"\bcards\b", r"priority mail", r"ups ground", r"no surprise", r"salt life",
          r"packed by", r"\b175\b"]

def banned_hits(text):
    return [b for b in BANNED if re.search(b, text, re.I)]

# ---- drawing ------------------------------------------------------------------
CHAR = (18, 20, 24)
RED, NAVY, WHITE = (178, 34, 52), (28, 46, 92), (255, 255, 255)

def font(size, med=False):
    return ImageFont.truetype(FONT_MED if med else FONT, size)

def wrap(draw, text, f, maxw):
    words, lines, cur = text.replace('" x ', '"\u00a0x\u00a0').split(" "), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return [l.replace("\u00a0", " ") for l in lines]

def text_band(canvas_size, text, sub=None, y_top=330, size=78, maxw=796):
    # maxw 796 + 2 x 34 padding = 864 band, so at least 108 px (10%) clear each side at 1080 wide
    """Transparent RGBA layer: dark band, flag hairline, white Oswald, centred."""
    cw, ch = canvas_size
    layer = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(size); fs = font(int(size * 0.46), med=True)
    while True:
        lines = wrap(d, text, f, maxw)
        if len(lines) <= 3 or size < 52: break
        size -= 6; f = font(size); fs = font(int(size * 0.46), med=True)
    lh = int(size * 1.18)
    slines = wrap(d, sub, fs, maxw) if sub else []
    slh = int(fs.size * 1.35)
    pad = 34
    tw = max([d.textlength(l, font=f) for l in lines] + [d.textlength(l, font=fs) for l in slines])
    bw = int(tw + pad * 2); bh = int(len(lines) * lh + (len(slines) * slh + 14 if slines else 0) + pad * 2 + 10)
    x0 = (cw - bw) // 2
    d.rounded_rectangle([x0, y_top, x0 + bw, y_top + bh], radius=10, fill=CHAR + (205,))
    # hairline: red / white / navy
    hx = x0 + pad; hy = y_top + 18
    for i, c in enumerate((RED, WHITE, NAVY)):
        d.rectangle([hx + i * 34, hy, hx + i * 34 + 26, hy + 3], fill=c + (255,))
    y = y_top + pad + 6
    for l in lines:
        d.text(((cw - d.textlength(l, font=f)) / 2, y - size * 0.08), l, font=f, fill=WHITE + (255,)); y += lh
    if slines:
        y += 14
        for l in slines:
            d.text(((cw - d.textlength(l, font=fs)) / 2, y), l, font=fs, fill=(220, 222, 226, 255)); y += slh
    return layer

def end_card(size=(W, H)):
    cw, ch = size
    im = Image.new("RGB", size, CHAR)
    d = ImageDraw.Draw(im)
    f1 = font(84); f2 = font(64, med=True)
    lines = wrap(d, END_PRICE.upper(), f1, 860)
    total = len(lines) * 100 + 60 + 80
    y = (ch - total) // 2 - (60 if ch > 1500 else 0)
    hx = (cw - 3 * 34) // 2
    for i, c in enumerate((RED, WHITE, NAVY)):
        d.rectangle([hx + i * 34, y - 50, hx + i * 34 + 26, y - 46], fill=c)
    for l in lines:
        d.text(((cw - d.textlength(l, font=f1)) / 2, y), l, font=f1, fill=WHITE); y += 100
    y += 60
    s = END_SITE.upper()
    d.text(((cw - d.textlength(s, font=f2)) / 2, y), s, font=f2, fill=(220, 222, 226))
    return im

_cache = {}
def photo(key):
    if key not in _cache:
        _cache[key] = Image.open(os.path.join(MK, P[key])).convert("RGB")
    return _cache[key]

def window(img, fx, fy, zoom, aspect):
    iw, ih = img.size
    if iw / ih > aspect: bh = ih; bw = ih * aspect
    else: bw = iw; bh = iw / aspect
    bw /= zoom; bh /= zoom
    x0 = min(max(fx * iw - bw / 2, 0), iw - bw); y0 = min(max(fy * ih - bh / 2, 0), ih - bh)
    return (x0, y0, x0 + bw, y0 + bh)

def ease(t): return t * t * (3 - 2 * t)

def frame(shot, t, size=(W, H)):
    key, dur, mv, txt, sub = shot
    if key == "END": return end_card(size)
    fx, fy, z0, z1, dx = mv
    e = ease(t)
    img = photo(key)
    box = window(img, fx + dx * (e - 0.5), fy, z0 + (z1 - z0) * e, size[0] / size[1])
    return img.resize(size, Image.LANCZOS, box=box)

def overlay(base, layer):
    if layer is None: return base
    out = base.convert("RGBA"); out.alpha_composite(layer); return out.convert("RGB")

def shot_layer(v, shot, size=(W, H), y_top=330):
    key, dur, mv, txt, sub = shot
    if txt is None or key == "END": return None
    if txt == "HOOK":
        return text_band(size, v["hook"][0], v.get("hook_sub"), y_top=y_top, size=84)
    return text_band(size, txt, sub, y_top=y_top, size=72)

# ---- build --------------------------------------------------------------------
def build(v):
    vid = v["id"]; d = os.path.join(OUT, vid); os.makedirs(d, exist_ok=True)
    mp4 = os.path.join(d, f"{vid}.mp4")
    frames_total = sum(round(s[1] * FPS) for s in v["shots"])
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-preset", "slow", "-crf", "20", "-r", str(FPS), "-g", "60", "-c:a", "aac", "-b:a", "128k",
           "-shortest", "-movflags", "+faststart", mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    grid_idx = set(int(i * (frames_total - 1) / 14) for i in range(15))
    grid_frames, n = [], 0
    for shot in v["shots"]:
        nf = round(shot[1] * FPS); layer = shot_layer(v, shot)
        for i in range(nf):
            im = overlay(frame(shot, i / max(nf - 1, 1)), layer)
            p.stdin.write(im.tobytes())
            if n in grid_idx: grid_frames.append((n, im.copy()))
            n += 1
    p.stdin.close(); p.wait()
    assert p.returncode == 0, vid
    # first-frame still for checks
    grid_frames[0][1].save(os.path.join(d, f"{vid}-frame1.jpg"), quality=92)
    # 5x3 frame grid
    tw, th, hdr = 216, 384, 90
    g = Image.new("RGB", (tw * 5, th * 3 + hdr), (245, 245, 245))
    gd = ImageDraw.Draw(g)
    status = v["hook"][1]
    hc = (178, 34, 52) if status == "DRAFT" else (24, 110, 60)
    gd.rectangle([0, 0, g.width, hdr], fill=hc)
    gd.text((16, 10), f"{vid}  ·  {v['title']}  ·  HOOK {status}" + ("  ·  NOT APPROVED" if status == "DRAFT" else ""),
            font=font(30), fill=WHITE)
    gd.text((16, 52), f"\"{v['hook'][0]}\"  ·  {frames_total / FPS:.1f}s", font=font(22, med=True), fill=WHITE)
    for k, (fn, im) in enumerate(grid_frames[:15]):
        t = im.resize((tw, th), Image.LANCZOS); g.paste(t, ((k % 5) * tw, hdr + (k // 5) * th))
        gd.text(((k % 5) * tw + 6, hdr + (k // 5) * th + 4), f"{fn / FPS:.1f}s", font=font(18, med=True), fill=(255, 230, 0))
    g.save(os.path.join(d, f"{vid}-grid.jpg"), quality=88)
    # 1080x1350 still (first shot + hook)
    s0 = v["shots"][0]
    st = overlay(frame(s0, 0.0, (1080, 1350)), shot_layer(v, s0, (1080, 1350), y_top=150))
    st.save(os.path.join(d, f"{vid}-still-1080x1350.jpg"), quality=92)
    # carousel slides for F5
    if vid.startswith("F5"):
        for k, shot in enumerate(v["shots"], 1):
            sl = overlay(frame(shot, 0.0, (1080, 1350)), shot_layer(v, shot, (1080, 1350), y_top=150))
            sl.save(os.path.join(d, f"{vid}-carousel-{k}.jpg"), quality=92)
    return dict(id=vid, mp4=os.path.relpath(mp4, HERE), seconds=frames_total / FPS)

def onscreen_text(v):
    t = [v["hook"][0], v.get("hook_sub") or ""]
    for s in v["shots"]:
        if s[3] and s[3] != "HOOK": t.append(s[3])
        if s[4]: t.append(s[4])
    if any(s[0] == "END" for s in v["shots"]): t += [END_PRICE, END_SITE]
    return [x for x in t if x]

# Caption lines used in PACK.md (verbatim from marketing/captions.md, hashtags trimmed)
CAPTION_LINES = [
    "Make America Great Again — right down to the fenders.",
    "Marine-grade neoprene, flag print. Sold as a 2-pack.",
    "$119 for the two-pack, shipping included.",
    "fenderu.com",
    "#maga #boatlife #boating #americafirst #patriot",
    "Show your patriotism.",
    'Marine-grade neoprene. UV protected, waterproof, salt-resistant. Fits standard 8.5" x 26" cylindrical fenders. Sold as a 2-pack.',
    "#boataccessories #boatlife #boatgear #americafirst #patriot",
    "MAGA fender covers — marine-grade neoprene, sold as a 2-pack.",
    'Fits standard 8.5" x 26" cylindrical fenders. $119 for the two-pack, shipping included.',
    "American-owned and operated.",
    "Questions welcome.",
    "#maga #boatlife #lakelife #wakesurf #boating #americafirst #patriot",
    "#boataccessories #boatlife #marina #neoprene #boatgear #boating #americafirst #patriot",
    "MAGA Fender Covers, Marine-Grade Neoprene, Sold as a 2-Pack",  # Pinterest title, DRAFT
]

if __name__ == "__main__":
    cap_hits = [(c, banned_hits(c)) for c in CAPTION_LINES if banned_hits(c)]
    if cap_hits: sys.exit(f"BANNED in captions: {cap_hits}")
    if sys.argv[1:] == ["--check"]:
        n = sum(len(onscreen_text(v)) for v in VIDEOS)
        bad = [(v["id"], t) for v in VIDEOS for t in onscreen_text(v) if banned_hits(t)]
        sys.exit(f"BANNED on screen: {bad}" if bad else print(f"check ok: {n} on-screen lines, {len(CAPTION_LINES)} caption lines, 0 hits") or 0)
    want = set(sys.argv[1:])
    report = []
    for v in VIDEOS:
        if want and v["id"] not in want: continue
        hits = [(x, banned_hits(x)) for x in onscreen_text(v) if banned_hits(x)]
        if hits: sys.exit(f"BANNED in {v['id']}: {hits}")
        r = build(v); r["runway"] = sorted({s[0] for s in v["shots"]} & RUNWAY)
        r["text"] = onscreen_text(v); report.append(r); print(json.dumps(r))
    with open(os.path.join(OUT, "build-report.json"), "w") as fh: json.dump(report, fh, indent=1)
