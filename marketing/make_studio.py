"""Builds FenderU product graphics from Garrett's own white-background photos.

Input:  marketing/src/cutout/cover-N.png (background removed from
        marketing/src/white/cover-N.jpg)
Output: marketing/graphics/
  square-*.jpg   1080x1080  Facebook Page feed
  pin-*.jpg      1000x1500  Pinterest
  portrait-*.jpg 1080x1350  Facebook Page feed, tall

Site style: deep charcoal/navy, thin red/white/navy rule, letter-spaced
uppercase in Oswald. Every word on an image is copy Garrett already approved.
Usage: python3 marketing/make_studio.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CUT = os.path.join(HERE, "src", "cutout")
OUT = os.path.join(HERE, "graphics")
FONTS = os.path.join(HERE, "fonts")
WHITE, RED, NAVY, MUTED = (255, 255, 255), (204, 34, 0), (27, 42, 74), (190, 194, 198)


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONTS, f"Oswald_{weight}.ttf"), size)


def spaced(d, xy, text, fnt, fill, sp, anchor_right=False):
    w = sum(d.textlength(c, font=fnt) + sp for c in text) - sp
    x, y = xy
    if anchor_right:
        x -= w
    for c in text:
        d.text((x, y), c, font=fnt, fill=fill)
        x += d.textlength(c, font=fnt) + sp
    return w


def rule(d, x, y, scale=1.0):
    for i, c in enumerate((RED, WHITE, (70, 100, 170))):
        d.rectangle([x + i * 46 * scale, y, x + i * 46 * scale + 38 * scale, y + 4 * scale], fill=c)


def backdrop(w, h):
    """Charcoal to navy, lighter behind the product."""
    bg = Image.new("RGB", (w, h), (24, 26, 28))
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse([w * 0.05, h * 0.0, w * 0.95, h * 0.95], fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(min(w, h) * 0.18))
    tint = Image.new("RGB", (w, h), (44, 56, 82))
    return Image.composite(tint, bg, glow)


def cover(n, height):
    im = Image.open(os.path.join(CUT, f"cover-{n}.png")).convert("RGBA")
    r = height / im.height
    return im.resize((round(im.width * r), round(height)), Image.LANCZOS)


def place(canvas, im, x, y):
    """Paste with a soft drop shadow so it sits on the backdrop."""
    a = im.split()[3]
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: v * 0.55))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    canvas.paste((0, 0, 0), (x + 14, y + 22), sh)
    canvas.paste(im, (x, y), im)


def pair(canvas, a, b, cx, top, h):
    """The 2-pack: two covers side by side, the back one slightly smaller."""
    back, front = cover(b, h * 0.94), cover(a, h)
    gap = front.width * 0.18
    place(canvas, back, round(cx - gap / 2 - back.width * 0.15), round(top + h * 0.03))
    place(canvas, front, round(cx - front.width + gap * 1.6), round(top))


def square(name, a, b):
    W = H = 1080
    c = backdrop(W, H)
    pair(c, a, b, 360, 70, 940)
    d = ImageDraw.Draw(c)
    x = 640
    f = font("700Bold", 76)
    y = 240
    rule(d, x, y)
    y += 30
    for line in ("MAKE", "AMERICA", "GREAT", "AGAIN"):
        d.text((x, y), line, font=f, fill=WHITE)
        y += f.getbbox(line)[3] + 14
    y += 26
    spaced(d, (x + 2, y), "SOLD AS A 2-PACK", font("400Regular", 28), MUTED, 5)
    y += 80
    d.text((x, y), "$119", font=font("700Bold", 60), fill=WHITE)
    y += 92
    spaced(d, (x + 2, y), "FREE SHIPPING", font("500Medium", 30), WHITE, 7)
    spaced(d, (W - 60, H - 80), "FENDERU.COM", font("500Medium", 32), MUTED, 9, anchor_right=True)
    c.save(os.path.join(OUT, name), quality=93)


def pin(name, a, b):
    W, H = 1000, 1500
    c = backdrop(W, H)
    pair(c, a, b, W / 2 - 20, 40, 1010)
    d = ImageDraw.Draw(c)
    top = 1080
    d.rectangle([0, top, W, H], fill=(30, 32, 34))
    rule(d, 70, top + 50)
    d.text((70, top + 75), "MAGA FENDER COVERS", font=font("700Bold", 76), fill=WHITE)
    spaced(d, (72, top + 185), "MARINE-GRADE NEOPRENE  ·  SOLD AS A 2-PACK", font("400Regular", 27), MUTED, 4)
    spaced(d, (72, top + 240), "$119  ·  FREE SHIPPING", font("500Medium", 34), WHITE, 5)
    spaced(d, (72, H - 75), "FENDERU.COM", font("500Medium", 30), MUTED, 9)
    c.save(os.path.join(OUT, name), quality=93)


def portrait(name, n):
    W, H = 1080, 1350
    c = backdrop(W, H)
    im = cover(n, 1000)
    place(c, im, round(W / 2 - im.width / 2), 50)
    d = ImageDraw.Draw(c)
    top = 1080
    d.rectangle([0, top, W, H], fill=(30, 32, 34))
    rule(d, 72, top + 45)
    d.text((72, top + 68), "SHOW YOUR PATRIOTISM.", font=font("700Bold", 64), fill=WHITE)
    spaced(d, (74, top + 170), "$119  ·  FREE SHIPPING", font("500Medium", 30), MUTED, 5)
    spaced(d, (W - 72, top + 170), "FENDERU.COM", font("500Medium", 30), WHITE, 8, anchor_right=True)
    c.save(os.path.join(OUT, name), quality=93)


def plate(name, covers):
    """2160x3840 vertical backdrop for reels: product in the top two thirds,
    leaving the bottom clear for the reel's text band."""
    W, H = 2160, 3840
    c = backdrop(W, H)
    if len(covers) == 1:
        im = cover(covers[0], 2500)
        place(c, im, round(W / 2 - im.width / 2), 160)
    else:
        pair(c, covers[0], covers[1], W / 2 - 40, 160, 2500)
    c.save(os.path.join(HERE, "src", name), quality=92)


def main():
    os.makedirs(OUT, exist_ok=True)
    square("square-1.jpg", 5, 1)
    square("square-2.jpg", 4, 2)
    pin("pin-1.jpg", 5, 3)
    pin("pin-2.jpg", 1, 4)
    portrait("portrait-1.jpg", 5)
    portrait("portrait-2.jpg", 1)
    plate("studio-single.jpg", [5])
    plate("studio-pair.jpg", [5, 1])
    plate("studio-pair-2.jpg", [3, 2])
    print(sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
