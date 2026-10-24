"""Builds the third FenderU content set from Garrett's own photos.

Graphics -> marketing/graphics/set3/   (Facebook Page, Pinterest)
Reels    -> marketing/reels/set3/      (1080x1920, 30fps, silent AAC track so
                                         Facebook accepts the upload)

Sources are only Garrett's photos: the white-background shots (cut out in
src/cutout/) and his own boat photos in src/. Every word on screen is copy he
has already approved; no "the pair" (banned 21 Oct 2026).
Usage: python3 marketing/make_set3.py [graphics|reels]
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
from make_studio import font, spaced, rule, backdrop, cover, place, WHITE, RED, MUTED

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
GOUT = os.path.join(HERE, "graphics", "set3")
ROUT = os.path.join(HERE, "reels", "set3")
CHAR, NAVY, INK, PAPER = (30, 32, 34), (27, 42, 74), (22, 30, 48), (244, 243, 240)


def width(d, text, fnt, sp):
    return sum(d.textlength(c, font=fnt) + sp for c in text) - sp


def centered(d, cx, y, text, fnt, fill, sp):
    spaced(d, (cx - width(d, text, fnt, sp) / 2, y), text, fnt, fill, sp)


def photo(name, w, h, zoom=1.0, fy=0.5):
    """Garrett's photo cover-cropped to w x h; fy picks the vertical focus."""
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    r = max(w / im.width, h / im.height) * zoom
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = round((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def fade_bottom(img, start, alpha=235, color=CHAR):
    w, h = img.size
    g = Image.new("L", (1, h), 0)
    for y in range(h):
        g.putpixel((0, y), 0 if y < start else min(alpha, round(alpha * (y - start) / (h * 0.18))))
    img.paste(Image.new("RGB", (w, h), color), (0, 0), g.resize((w, h)))


def price_line(d, x, y, size=34, fill=WHITE):
    spaced(d, (x, y), "$119  ·  FREE SHIPPING", font("500Medium", size), fill, 6)


# ---------------------------------------------------------------- graphics

def g1_trio():
    W = H = 1080
    c = backdrop(W, H)
    for n, cx, h in ((2, 270, 690), (4, 810, 690), (5, 540, 780)):
        im = cover(n, h)
        place(c, im, round(cx - im.width / 2), 210 + (780 - h) // 2)
    d = ImageDraw.Draw(c)
    rule(d, W / 2 - 63, 70)
    centered(d, W / 2, 98, "MAKE AMERICA GREAT AGAIN", font("700Bold", 66), WHITE, 3)
    d.rectangle([0, H - 110, W, H], fill=CHAR)
    price_line(d, 60, H - 76, 32)
    t = "FENDERU.COM"
    spaced(d, (W - 60 - width(d, t, font("500Medium", 32), 9), H - 76), t, font("500Medium", 32), MUTED, 9)
    c.save(os.path.join(GOUT, "g1-trio-square.jpg"), quality=93)


def g2_light_hero():
    W, H = 1080, 1350
    c = Image.new("RGB", (W, H), PAPER)
    im = cover(1, 1250).rotate(-7, resample=Image.BICUBIC, expand=True)
    place(c, im, W - im.width - 40, 40)
    d = ImageDraw.Draw(c)
    for i, col in enumerate((RED, NAVY, (70, 100, 170))):
        d.rectangle([70 + i * 46, 150, 108 + i * 46, 154], fill=col)
    y = 180
    for line in ("SHOW", "YOUR", "PATRIOTISM."):
        d.text((70, y), line, font=font("700Bold", 92), fill=INK)
        y += 116
    spaced(d, (74, y + 40), "MARINE-GRADE NEOPRENE", font("500Medium", 28), (90, 96, 108), 5)
    spaced(d, (74, y + 86), "SOLD AS A 2-PACK", font("500Medium", 28), (90, 96, 108), 5)
    d.rectangle([0, H - 120, W, H], fill=INK)
    price_line(d, 70, H - 82, 34)
    t = "FENDERU.COM"
    spaced(d, (W - 70 - width(d, t, font("500Medium", 34), 9), H - 82), t, font("500Medium", 34), MUTED, 9)
    c.save(os.path.join(GOUT, "g2-light-hero-portrait.jpg"), quality=93)


def g3_dock_split():
    W, H = 1080, 1350
    c = Image.new("RGB", (W, H), CHAR)
    c.paste(photo("media_southern_g01-pair-portrait.jpg", W, 930, fy=0.45), (0, 0))
    d = ImageDraw.Draw(c)
    top = 930
    rule(d, 72, top + 55)
    d.text((72, top + 80), "SOLD AS A 2-PACK", font=font("700Bold", 92), fill=WHITE)
    spaced(d, (74, top + 215), "AMERICAN FLAG AND MAGA PRINT  ·  MARINE-GRADE NEOPRENE", font("400Regular", 25), MUTED, 3)
    price_line(d, 74, top + 290, 34)
    t = "FENDERU.COM"
    spaced(d, (W - 72 - width(d, t, font("500Medium", 34), 9), top + 290), t, font("500Medium", 34), MUTED, 9)
    c.save(os.path.join(GOUT, "g3-dock-split-portrait.jpg"), quality=93)


def g4_detail():
    W = H = 1080
    c = photo("media_southern_g04-detail-portrait.jpg", W, H, fy=0.35)
    fade_bottom(c, 640)
    d = ImageDraw.Draw(c)
    rule(d, 66, H - 300)
    d.text((66, H - 275), "MARINE-GRADE NEOPRENE", font=font("700Bold", 74), fill=WHITE)
    spaced(d, (68, H - 160), "UV PROTECTED  ·  WATERPROOF  ·  SALT-RESISTANT", font("400Regular", 29), MUTED, 4)
    t = "FENDERU.COM"
    spaced(d, (68, H - 88), t, font("500Medium", 30), WHITE, 9)
    c.save(os.path.join(GOUT, "g4-detail-square.jpg"), quality=93)


def g5_fit_story():
    W, H = 1080, 1920
    c = backdrop(W, H)
    back, front = cover(3, 1180), cover(5, 1260)
    place(c, back, 560, 150)
    place(c, front, 250, 110)
    d = ImageDraw.Draw(c)
    top = 1440
    d.rectangle([0, top, W, H], fill=CHAR)
    rule(d, 72, top + 60)
    d.text((72, top + 84), 'FITS STANDARD 8.5" x 26" FENDERS', font=font("700Bold", 62), fill=WHITE)
    spaced(d, (74, top + 190), "SLIPS ON IN SECONDS  ·  NO TOOLS", font("400Regular", 32), MUTED, 5)
    price_line(d, 74, top + 260, 36)
    t = "FENDERU.COM"
    spaced(d, (74, H - 100), t, font("700Bold", 44), WHITE, 10)
    c.save(os.path.join(GOUT, "g5-fit-story.jpg"), quality=93)


def g6_dock():
    W, H = 1080, 1350
    c = photo("media_southern_g02-dock-square.jpg", W, H)
    fade_bottom(c, 860)
    d = ImageDraw.Draw(c)
    rule(d, 70, H - 330)
    d.text((70, H - 305), "MAGA FENDER COVERS", font=font("700Bold", 88), fill=WHITE)
    spaced(d, (72, H - 180), "AMERICAN-OWNED AND OPERATED", font("400Regular", 30), MUTED, 5)
    price_line(d, 72, H - 110, 34)
    t = "FENDERU.COM"
    spaced(d, (W - 70 - width(d, t, font("500Medium", 34), 9), H - 110), t, font("500Medium", 34), MUTED, 9)
    c.save(os.path.join(GOUT, "g6-dock-portrait.jpg"), quality=93)


# ---------------------------------------------------------------- reels

RW, RH, FPS = 1080, 1920, 30


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def render(name, seconds, frame_fn):
    """Pipe PIL frames to ffmpeg with a silent AAC track."""
    n = int(seconds * FPS)
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-b:v", "8M",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
           os.path.join(ROUT, name)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame_fn(i / FPS).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait():
        raise SystemExit(f"ffmpeg failed on {name}")


def endcard_layer():
    img = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top = RH - 640
    d.rectangle([0, top, RW, RH], fill=CHAR + (245,))
    rule(d, 72, top + 80)
    d.text((72, top + 110), "$119", font=font("700Bold", 170), fill=WHITE)
    spaced(d, (76, top + 340), "FREE SHIPPING", font("500Medium", 52), WHITE, 10)
    spaced(d, (76, top + 420), "SOLD AS A 2-PACK", font("400Regular", 36), MUTED, 5)
    t = "FENDERU.COM"
    f = font("700Bold", 56)
    spaced(d, (RW - 72 - width(d, t, f, 10), RH - 120), t, f, WHITE, 10)
    return img


def band_layer(title_lines, sub, top=RH - 520):
    img = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, top, RW, RH], fill=CHAR + (232,))
    rule(d, 72, top + 70)
    y = top + 100
    for line in title_lines:
        d.text((72, y), line, font=font("700Bold", 96), fill=WHITE)
        y += 116
    spaced(d, (74, y + 26), sub, font("400Regular", 34), MUTED, 5)
    spaced(d, (74, RH - 92), "FENDERU.COM", font("500Medium", 30), MUTED, 8)
    return img


def with_alpha(layer, a):
    if a >= 1:
        return layer
    out = layer.copy()
    out.putalpha(layer.split()[3].point(lambda v: round(v * a)))
    return out


def r1_lineup():
    """Light studio: the five covers drop in one at a time, then the end card."""
    base = Image.new("RGB", (RW, RH), PAPER)
    covers = [cover(n, h) for n, h in ((3, 980), (1, 980), (5, 1080))]
    cxs = [235, 845, 540]
    tops = [230, 230, 150]
    title = band_layer(["MAKE AMERICA", "GREAT AGAIN"], "AMERICAN FLAG AND MAGA PRINT")
    end = endcard_layer()

    def frame(t):
        c = base.copy()
        for i, (im, cx, top) in enumerate(zip(covers, cxs, tops)):
            k = ease((t - 0.45 * i) / 0.7)
            if k <= 0:
                continue
            y = round(-im.height + (top + im.height) * k)
            place(c, im, round(cx - im.width / 2), y)
        if 3.0 < t <= 8.0:
            c.paste(*(lambda L: (L, (0, 0), L))(with_alpha(title, ease((t - 3.0) / 0.5))))
        if t > 8.0:
            c.paste(*(lambda L: (L, (0, 0), L))(with_alpha(end, ease((t - 8.0) / 0.4))))
        return c
    render("r1-studio-lineup.mp4", 13, frame)


def r2_dock():
    """Garrett's boat photos, slow push-in, one approved line per scene."""
    scenes = [
        ("media_southern_g03-wake-surf-portrait.jpg", ["MAKE AMERICA", "GREAT AGAIN"], "SHOW YOUR PATRIOTISM."),
        ("media_southern_g01-pair-portrait.jpg", ["SOLD AS A", "2-PACK"], "MARINE-GRADE NEOPRENE"),
        ("media_southern_g04-detail-portrait.jpg", ["UV PROTECTED", "WATERPROOF"], "SALT-RESISTANT"),
        ("media_southern_g02-dock-square.jpg", None, None),
    ]
    durs = [3.2, 3.2, 3.2, 4.4]
    big = [photo(p, RW * 1, RH * 1, zoom=1.0) for p, _, _ in scenes]
    bands = [band_layer(t, s) if t else endcard_layer() for _, t, s in scenes]
    starts = [sum(durs[:i]) for i in range(len(durs))]

    def frame(t):
        i = max(k for k in range(len(starts)) if t >= starts[k])
        lt = t - starts[i]
        z = 1 + 0.08 * lt / durs[i]
        im = big[i]
        w, h = round(RW / z), round(RH / z)
        x, y = (RW - w) // 2, (RH - h) // 2
        c = im.crop((x, y, x + w, y + h)).resize((RW, RH), Image.BICUBIC)
        c.paste(bands[i], (0, 0), bands[i])
        if lt < 0.25 and i:
            c = Image.blend(Image.new("RGB", (RW, RH), (0, 0, 0)), c, lt / 0.25)
        return c
    render("r2-on-the-boat.mp4", sum(durs), frame)


def r3_reveal():
    """Starts tight on the print and pulls back to the full cover, then the 2-pack."""
    bg = backdrop(RW, RH)
    single = cover(5, 1300)
    back, front = cover(3, 1180), cover(1, 1260)
    title = band_layer(["SHOW YOUR", "PATRIOTISM."], "MARINE-GRADE NEOPRENE")
    pack = band_layer(["SOLD AS A", "2-PACK"], 'FITS STANDARD 8.5" x 26" FENDERS')
    end = endcard_layer()

    def frame(t):
        c = bg.copy()
        if t < 6.0:
            z = 3.2 - 2.2 * ease(t / 4.5)
            s = single.resize((round(single.width * z), round(single.height * z)), Image.LANCZOS)
            cx, cy = RW / 2, 140 + 650 * min(z, 1.6) / 1.6
            place(c, s, round(cx - s.width / 2), round(cy - s.height * 0.45))
            if t > 2.6:
                c.paste(*(lambda L: (L, (0, 0), L))(with_alpha(title, ease((t - 2.6) / 0.5))))
        else:
            k = ease((t - 6.0) / 0.7)
            place(c, back, round(560 + 300 * (1 - k)), 160)
            place(c, front, 250, 120)
            c.paste(*(lambda L: (L, (0, 0), L))(with_alpha(pack if t < 9.0 else end, 1 if t < 9.0 else ease((t - 9.0) / 0.5))))
        return c
    render("r3-print-reveal.mp4", 13, frame)


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "graphics"):
        os.makedirs(GOUT, exist_ok=True)
        for f in (g1_trio, g2_light_hero, g3_dock_split, g4_detail, g5_fit_story, g6_dock):
            f()
        print(sorted(os.listdir(GOUT)))
    if what in ("all", "reels"):
        os.makedirs(ROUT, exist_ok=True)
        for f in (r1_lineup, r2_dock, r3_reveal):
            f()
        print(sorted(os.listdir(ROUT)))


if __name__ == "__main__":
    main()
