"""FenderU campaign set 4: one look across every piece.

System
- One typeface (Oswald, the site's face). Headline 60px caps, +4 tracking.
  Small labels 20px caps, +6 tracking. Wordmark FENDERU, 26px, +14 tracking.
- One grade on every photo: gentle S-curve, navy shadows, warm highlights,
  slightly lower saturation, soft vignette.
- Studio pieces sit on a navy seamless sweep with a floor reflection and
  contact shadow, lit from above.
- One line of copy per piece, bottom-left, lots of empty space. Price appears
  only on the closing card. Copy is Garrett's approved wording only.

Output: graphics/set4/*.jpg (1080x1350 feed, 1080x1920 story) and
reels/set4/*.mp4 (1080x1920, 30fps, silent AAC).
Usage: python3 marketing/make_set4.py [stills|reels]
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, CUT = os.path.join(HERE, "src"), os.path.join(HERE, "src", "cutout")
GOUT, ROUT = os.path.join(HERE, "graphics", "set4"), os.path.join(HERE, "reels", "set4")
FONTS = os.path.join(HERE, "fonts")
WHITE, SOFT = (246, 245, 242), (188, 194, 204)
RED, SKY = (204, 34, 0), (86, 116, 180)


def font(w, s):
    return ImageFont.truetype(os.path.join(FONTS, f"Oswald_{w}.ttf"), s)


def track(d, xy, text, f, fill, sp):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + sp
    return x - sp - xy[0]


def tw(d, text, f, sp):
    return sum(d.textlength(c, font=f) + sp for c in text) - sp


# ------------------------------------------------------------------ look

def grade(img):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255
    a = 0.5 + (a - 0.5) * 1.06                      # contrast
    a = a * a * (3 - 2 * a) * 0.35 + a * 0.65       # gentle S-curve
    lum = (a * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    a = lum + (a - lum) * 0.9                       # saturation
    sh = np.clip(1 - lum * 2, 0, 1)
    hi = np.clip(lum * 2 - 1, 0, 1)
    a = a + sh * np.array([-0.025, 0.0, 0.035]) + hi * np.array([0.025, 0.012, -0.02])
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a = a * (1 - 0.22 * np.clip(r - 0.55, 0, 1) ** 1.4)[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def fit(name, w, h, fy=0.5, fx=0.5, zoom=1.0):
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    r = max(w / im.width, h / im.height) * zoom
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = round((im.width - w) * fx), round((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def shade_bottom(img, frac=0.42, strength=0.78):
    w, h = img.size
    g = np.linspace(0, 1, h)
    g = np.clip((g - (1 - frac)) / frac, 0, 1) ** 1.6 * strength
    a = np.asarray(img).astype(np.float32)
    a = a * (1 - g[:, None, None]) + np.array([10, 14, 24]) * g[:, None, None]
    return Image.fromarray(a.astype(np.uint8))


def sweep(w, h, light=False):
    """Seamless studio sweep: lit from above, floor from 68% down."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx = (xx - w / 2) / (w * 0.6)
    if light:
        top, mid, edge = np.array([236, 236, 232]), np.array([250, 249, 246]), np.array([214, 214, 210])
    else:
        top, mid, edge = np.array([14, 20, 34]), np.array([38, 54, 88]), np.array([8, 11, 19])
    t = np.clip(1 - np.sqrt(cx ** 2 + ((yy - h * 0.42) / (h * 0.55)) ** 2), 0, 1) ** 1.2
    a = edge + (mid - edge) * t[..., None]
    floor = np.clip((yy - h * 0.68) / (h * 0.32), 0, 1)[..., None]
    a = a * (1 - floor * 0.25) + top * floor * 0.25
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def cover(n, height, angle=0):
    im = Image.open(os.path.join(CUT, f"cover-{n}.png")).convert("RGBA")
    r = height / im.height
    im = im.resize((round(im.width * r), round(height)), Image.LANCZOS)
    return im.rotate(angle, resample=Image.BICUBIC, expand=True) if angle else im


def stage(canvas, im, cx, floor_y, light=False):
    """Stand a cutout on the sweep floor with a contact shadow and reflection."""
    x, y = round(cx - im.width / 2), round(floor_y - im.height)
    w = im.width
    sh = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(sh).ellipse([cx - w * 0.55, floor_y - 18, cx + w * 0.55, floor_y + 22], fill=150 if light else 220)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    canvas.paste((0, 0, 0) if not light else (60, 60, 60), (0, 0), sh)
    ref = im.transpose(Image.FLIP_TOP_BOTTOM)
    fade = np.linspace(0.22 if not light else 0.14, 0, ref.height) ** 1.3
    alpha = (np.asarray(ref.split()[3]).astype(np.float32) * fade[:, None]).astype(np.uint8)
    ref.putalpha(Image.fromarray(alpha))
    canvas.paste(ref.filter(ImageFilter.GaussianBlur(2)), (x, floor_y + 4), ref.filter(ImageFilter.GaussianBlur(2)))
    canvas.paste(im, (x, y), im)


# ------------------------------------------------------------------ type

def wordmark(d, x, y, fill=WHITE):
    track(d, (x, y), "FENDERU", font("500Medium", 26), fill, 14)


def stripe(d, x, y, light=False):
    for i, c in enumerate((RED, (20, 26, 40) if light else WHITE, SKY)):
        d.rectangle([x + i * 30, y, x + i * 30 + 22, y + 3], fill=c)


def headline(d, x, y, text, fill=WHITE, size=60):
    stripe(d, x + 2, y - 26, light=fill != WHITE)
    while tw(d, text, font("700Bold", size), 4) > d.im.size[0] - 2 * x - 8:
        size -= 2
    track(d, (x, y), text, font("700Bold", size), fill, 4)


def label(d, x, y, text, fill=SOFT):
    track(d, (x, y), text, font("400Regular", 20), fill, 6)


def frame_type(img, line, sub=None, light=False, mark=True):
    d = ImageDraw.Draw(img)
    W, H = img.size
    fg = (20, 26, 40) if light else WHITE
    sb = (92, 98, 110) if light else SOFT
    if mark:
        wordmark(d, 72, 72, fg)
    headline(d, 72, H - (190 if sub else 150), line, fg)
    if sub:
        label(d, 74, H - 104, sub, sb)
    return img


# ------------------------------------------------------------------ stills

FW, FH = 1080, 1350


def s1_hero():
    c = sweep(FW, FH)
    stage(c, cover(5, 880), FW / 2, 1010)
    frame_type(c, "MAKE AMERICA GREAT AGAIN", "MARINE-GRADE NEOPRENE  ·  SOLD AS A 2-PACK")
    return c


def s2_boat():
    c = grade(fit("media_southern_g03-wake-surf-portrait.jpg", FW, FH))
    c = shade_bottom(c)
    return frame_type(c, "SHOW YOUR PATRIOTISM.")


def s3_detail():
    c = grade(fit("media_southern_g04-detail-portrait.jpg", FW, FH, fy=0.3))
    c = shade_bottom(c)
    return frame_type(c, "MARINE-GRADE NEOPRENE", "UV PROTECTED  ·  WATERPROOF  ·  SALT-RESISTANT")


def s4_pair_light():
    c = sweep(FW, FH, light=True)
    stage(c, cover(3, 800), FW / 2 + 130, 1000, light=True)
    stage(c, cover(1, 860), FW / 2 - 110, 1020, light=True)
    return frame_type(c, "SOLD AS A 2-PACK", "AMERICAN FLAG AND MAGA PRINT", light=True)


def s5_dock():
    c = grade(fit("img_p06.webp", FW, FH, fy=0.4))
    c = shade_bottom(c)
    return frame_type(c, 'FITS STANDARD 8.5" x 26" FENDERS', "SLIPS ON IN SECONDS  ·  NO TOOLS")


def s6_close():
    c = sweep(FW, FH)
    for n, cx, h in ((2, FW / 2 - 250, 700), (4, FW / 2 + 250, 700), (5, FW / 2, 780)):
        stage(c, cover(n, h), cx, 960 if n != 5 else 985)
    d = ImageDraw.Draw(c)
    wordmark(d, 72, 72)
    headline(d, 72, FH - 220, "$119  ·  FREE SHIPPING")
    label(d, 74, FH - 134, "SOLD AS A 2-PACK")
    t = "FENDERU.COM"
    track(d, (FW - 72 - tw(d, t, font("500Medium", 26), 10), FH - 140), t, font("500Medium", 26), WHITE, 10)
    return c


STILLS = [("01-hero-maga.jpg", s1_hero), ("02-boat-patriotism.jpg", s2_boat),
          ("03-detail-neoprene.jpg", s3_detail), ("04-two-pack-studio.jpg", s4_pair_light),
          ("05-dock-fit.jpg", s5_dock), ("06-price-card.jpg", s6_close)]


# ------------------------------------------------------------------ reels

RW, RH, FPS = 1080, 1920, 30


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def render(name, seconds, frame_fn):
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}",
           "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", os.path.join(ROUT, name)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(seconds * FPS)):
        p.stdin.write(frame_fn(i / FPS).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait():
        raise SystemExit(f"ffmpeg failed: {name}")


def type_layer(line, sub=None, price=False):
    L = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    wordmark(d, 72, 110)
    if price:
        headline(d, 72, RH - 330, "$119  ·  FREE SHIPPING", size=66)
        label(d, 74, RH - 236, "SOLD AS A 2-PACK")
        t = "FENDERU.COM"
        track(d, (74, RH - 170), t, font("500Medium", 34), WHITE, 12)
    else:
        headline(d, 72, RH - (300 if sub else 250), line, size=64)
        if sub:
            label(d, 74, RH - 206, sub)
    return L


def fade_in(L, a):
    if a >= 1:
        return L
    out = L.copy()
    out.putalpha(L.split()[3].point(lambda v: round(v * a)))
    return out


def push(img, t, dur, z0=1.0, z1=1.08, dx=0.0):
    k = ease(t / dur) * 0.7 + (t / dur) * 0.3
    z = z0 + (z1 - z0) * k
    w, h = round(RW / z), round(RH / z)
    x = round((img.width - w) / 2 + dx * k * (img.width - w) / 2)
    y = round((img.height - h) / 2)
    return img.crop((x, y, x + w, y + h)).resize((RW, RH), Image.BICUBIC)


def scene_sequence(name, scenes):
    """scenes: list of (background PIL image, duration, type layer)."""
    starts = np.cumsum([0] + [s[1] for s in scenes[:-1]])
    total = sum(s[1] for s in scenes)

    def frame(t):
        i = int(np.searchsorted(starts, t, side="right") - 1)
        bg, dur, L = scenes[i]
        lt = t - starts[i]
        c = push(bg, lt, dur, dx=0.25 if i % 2 else -0.25)
        if L is not None:
            c.paste(fade_in(L, ease((lt - 0.35) / 0.5)), (0, 0), fade_in(L, ease((lt - 0.35) / 0.5)))
        if i > 0 and lt < 0.4:
            prev_bg, pdur, pL = scenes[i - 1]
            p = push(prev_bg, pdur, pdur, dx=0.25 if (i - 1) % 2 else -0.25)
            if pL is not None:
                p.paste(pL, (0, 0), pL)
            c = Image.blend(p, c, ease(lt / 0.4))
        if t > total - 0.4:
            c = Image.blend(c, Image.new("RGB", c.size, (8, 11, 19)), ease((t - (total - 0.4)) / 0.4))
        return c
    render(name, total, frame)


def studio_bg(covers, light=False):
    c = sweep(RW, RH, light)
    for n, cx, h, fl in covers:
        stage(c, cover(n, h), cx, fl, light)
    return c


def boat_bg(name, **kw):
    return shade_bottom(grade(fit(name, RW, RH, **kw)), 0.38, 0.85)


def reels():
    os.makedirs(ROUT, exist_ok=True)
    scene_sequence("A-campaign-15s.mp4", [
        (studio_bg([(5, RW / 2, 1150, 1330)]), 3.6, type_layer("MAKE AMERICA GREAT AGAIN")),
        (boat_bg("media_southern_g03-wake-surf-portrait.jpg"), 3.0, type_layer("SHOW YOUR PATRIOTISM.")),
        (boat_bg("media_southern_g04-detail-portrait.jpg", fy=0.3), 3.0, type_layer("MARINE-GRADE NEOPRENE", "UV PROTECTED  ·  WATERPROOF  ·  SALT-RESISTANT")),
        (studio_bg([(2, RW / 2 - 260, 900, 1260), (4, RW / 2 + 260, 900, 1260), (5, RW / 2, 1000, 1290)]), 4.4, type_layer(None, price=True)),
    ])
    scene_sequence("B-on-the-water-12s.mp4", [
        (boat_bg("media_southern_g01-pair-portrait.jpg"), 3.2, type_layer("SOLD AS A 2-PACK", "AMERICAN FLAG AND MAGA PRINT")),
        (boat_bg("img_p06.webp", fy=0.4), 3.2, type_layer('FITS STANDARD 8.5" x 26" FENDERS', "SLIPS ON IN SECONDS  ·  NO TOOLS")),
        (boat_bg("media_southern_g03-wake-surf-portrait.jpg", zoom=1.15, fy=0.6), 1.8, None),
        (studio_bg([(3, RW / 2 + 150, 1000, 1270), (1, RW / 2 - 130, 1080, 1290)]), 4.0, type_layer(None, price=True)),
    ])
    scene_sequence("C-studio-10s.mp4", [
        (studio_bg([(1, RW / 2, 1150, 1330)], light=True), 3.2, None),
        (studio_bg([(3, RW / 2 + 150, 1000, 1270), (1, RW / 2 - 130, 1080, 1290)], light=True), 3.0, None),
        (studio_bg([(2, RW / 2 - 260, 900, 1260), (4, RW / 2 + 260, 900, 1260), (5, RW / 2, 1000, 1290)]), 3.8, type_layer(None, price=True)),
    ])


def stills():
    os.makedirs(GOUT, exist_ok=True)
    for name, fn in STILLS:
        fn().save(os.path.join(GOUT, name), quality=94)
    print(sorted(os.listdir(GOUT)))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "stills"):
        stills()
    if what in ("all", "reels"):
        reels()
