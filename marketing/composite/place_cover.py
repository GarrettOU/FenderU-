"""Place Garrett's REAL cover photo onto a fender in a boat scene.

Rule (26 Oct): never let an AI model draw the cover. The cover pixels come only
from marketing/src/cutout/*.png and are only resized and shaded here (a smooth
brightness/colour mask: cylinder falloff, sun highlight, scene colour cast),
then given a contact shadow and a water reflection. verify_print() then checks
the placed pixels against the original before anything is shown.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter


def _blur(arr, sigma):
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return np.array(im.filter(ImageFilter.GaussianBlur(sigma))).astype(np.float32)


def clear_fender(scene, box, keep_rope=None, thresh=70, grow=6, waterline=1045,
                 hull_dx=-260, water_dx=270):
    """Paint out the scene's own fender so none of it peeks out from behind the
    real cover. Dark pixels inside box (grown a few px to take the soft shadow)
    are filled by diffusion from the surrounding pixels, then the fine texture
    of a neighbouring patch (hull gloss to the left, water ripples to the right)
    is laid back over the fill so it isn't a smooth smear.
    keep_rope=(x0,x1,ymax) protects the bow line above the cover."""
    a = np.array(scene).astype(np.float32)
    H, W, _ = a.shape
    x0, y0, x1, y1 = box
    dark = Image.fromarray(((a.max(-1) < thresh) * 255).astype(np.uint8))
    m = np.array(dark.filter(ImageFilter.MaxFilter(2 * grow + 1))) > 0
    keep = np.zeros_like(m)
    keep[:y0, :] = keep[y1:, :] = True
    keep[:, :x0] = keep[:, x1:] = True
    if keep_rope:
        keep[:keep_rope[2], keep_rope[0]:keep_rope[1]] = True
    m &= ~keep

    # work on a padded crop for speed
    pad = 48
    cy0, cy1, cx0, cx1 = max(y0 - pad, 0), min(y1 + pad, H), max(x0 - pad, 0), min(x1 + pad, W)
    crop, cm = a[cy0:cy1, cx0:cx1].copy(), m[cy0:cy1, cx0:cx1]
    fill = crop.copy()
    fill[cm] = crop[~cm].mean(0)
    for sigma, n in ((12, 40), (5, 60), (2, 40)):
        for _ in range(n):
            b = np.stack([_blur(fill[..., c], sigma) for c in range(3)], -1)
            fill[cm] = b[cm]

    # borrow high-frequency texture from a donor patch beside the hole
    ys, xs = np.nonzero(cm)
    dx = np.where(ys + cy0 >= waterline, water_dx, hull_dx)
    dxs = np.clip(xs + cx0 + dx, 0, W - 1)
    low = np.stack([_blur(a[..., c], 6) for c in range(3)], -1)
    hp = a - low
    fill[ys, xs] += 0.9 * hp[ys + cy0, dxs]
    a[cy0:cy1, cx0:cx1] = fill
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def shade(cut, warmth=(1.03, 1.0, 0.96), light=0.95, edge=0.55, hi_pos=0.36, hi=0.10):
    """Smooth brightness/colour mask only: cylinder falloff to both edges, a soft
    highlight down the sun side, and the scene's warm cast. Per row, so the
    narrower fender ends get the same treatment as the body."""
    a = np.array(cut).astype(np.float32)
    al = a[..., 3] > 0
    h, w = al.shape
    xs = np.arange(w)[None, :].repeat(h, 0).astype(np.float32)
    xmin = np.where(al.any(1), np.argmax(al, 1), 0)
    xmax = np.where(al.any(1), w - 1 - np.argmax(al[:, ::-1], 1), 1)
    span = np.maximum(xmax - xmin, 1)[:, None]
    t = np.clip((xs - xmin[:, None]) / span, 0, 1)
    lam = np.sqrt(np.clip(1 - (2 * t - 1) ** 2, 0, 1)) ** 0.7
    prof = (edge + (1 - edge) * lam + hi * np.exp(-((t - hi_pos) / 0.10) ** 2)) * light
    for c in range(3):
        a[..., c] = np.clip(a[..., c] * prof * warmth[c], 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA"), prof


def place(scene_path, cutout_path, out_path, fender_top, fender_bottom, center_x,
          eye_y=270, crop_top=230, body_center=347, waterline=None,
          clear_box=None, keep_rope=None):
    scene = Image.open(scene_path).convert("RGB")
    if clear_box:
        scene = clear_fender(scene, clear_box, keep_rope, waterline=waterline or 10**6)
    cut = Image.open(cutout_path).convert("RGBA")
    bottom = int(np.where(np.array(cut)[..., 3] > 128)[0].max())
    s = (fender_bottom - fender_top) / (bottom - eye_y)
    cut = cut.crop((0, crop_top, cut.width, bottom + 1))
    w, h = round(cut.width * s), round(cut.height * s)
    cut = cut.resize((w, h), Image.LANCZOS)          # resize only
    x0 = round(center_x - body_center * s)
    y0 = round(fender_top - (eye_y - crop_top) * s)
    shaded, prof = shade(cut)
    alpha = shaded.split()[3]

    out = scene.copy()
    # contact shadow: a broad soft one offset down-left, plus a tight dark rim
    # right at the silhouette so the fender reads as resting on the hull
    W, H = scene.size
    soft = Image.new("L", (W, H), 0)
    soft.paste(alpha.point(lambda v: int(v * 0.8)), (x0 - 14, y0 + 12))
    soft = soft.filter(ImageFilter.GaussianBlur(10))
    rim = Image.new("L", (W, H), 0)
    rim.paste(alpha, (x0, y0))
    rim = rim.filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.5))
    sh = np.maximum(np.array(soft), np.array(rim))
    out = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), out, Image.fromarray(sh))

    # water reflection: squashed mirror, blurred, faint, broken by the water's
    # own ripples and fading/darkening toward the bottom
    if waterline is not None:
        rh = int(h * 0.55)
        refl = shaded.transpose(Image.FLIP_TOP_BOTTOM).resize((w, rh), Image.LANCZOS)
        refl = refl.filter(ImageFilter.GaussianBlur(2.5))
        r = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ry = waterline + (waterline - (y0 + h))
        r.paste(refl, (x0, ry))
        ra = np.array(r).astype(np.float32)
        yy = np.arange(H)[:, None].astype(np.float32)
        fade = np.clip(1 - (yy - waterline) / 190.0, 0, 1)
        base = np.array(scene.convert("L")).astype(np.float32)
        ripple = base - _blur(base, 5)
        ripple = np.clip(0.55 + ripple / 18.0, 0.15, 1.0)
        ra[..., 3] *= 0.20 * fade * ripple
        ra[..., :3] *= 0.65 + 0.35 * fade
        ra[:waterline, :, 3] = 0
        r = Image.fromarray(np.clip(ra, 0, 255).astype(np.uint8), "RGBA")
        out = Image.alpha_composite(out.convert("RGBA"), r).convert("RGB")

    out.paste(shaded, (x0, y0), shaded)
    out.save(out_path, quality=95)
    return dict(scale=s, x0=x0, y0=y0, w=w, h=h, crop_top=crop_top, prof=prof)


def verify_print(out_path, cutout_path, info, sheet_path):
    """Side-by-side of the placed cover vs the original photo at the same size,
    plus two scores: the raw correlation of the print area, and the correlation
    once the known shading mask is divided back out (which is what proves no
    pixel was redrawn: only a smooth multiplier separates the two)."""
    cut = Image.open(cutout_path).convert("RGBA")
    bottom = int(np.where(np.array(cut)[..., 3] > 128)[0].max())
    cut = cut.crop((0, info["crop_top"], cut.width, bottom + 1)).resize((info["w"], info["h"]), Image.LANCZOS)
    placed = Image.open(out_path).convert("RGB").crop(
        (info["x0"], info["y0"], info["x0"] + info["w"], info["y0"] + info["h"]))
    m = np.array(cut)[..., 3] > 250
    g1 = np.array(cut.convert("L")).astype(float)
    g2 = np.array(placed.convert("L")).astype(float)
    raw = float(np.corrcoef(g1[m], g2[m])[0, 1])
    unshaded = float(np.corrcoef(g1[m], (g2 / np.maximum(info["prof"], 0.05))[m])[0, 1])
    k = 3
    orig = Image.new("RGB", cut.size, (255, 255, 255)); orig.paste(cut, (0, 0), cut)
    a, b = orig.resize((info["w"] * k, info["h"] * k)), placed.resize((info["w"] * k, info["h"] * k))
    sheet = Image.new("RGB", (a.width * 2 + 60, a.height + 40), (235, 235, 235))
    sheet.paste(a, (20, 20)); sheet.paste(b, (a.width + 40, 20))
    sheet.save(sheet_path, quality=92)
    return raw, unshaded


if __name__ == "__main__":
    scene, cutout, out, sheet = sys.argv[1:5]
    t, btm, cx, wl = map(int, sys.argv[5:9])
    info = place(scene, cutout, out, t, btm, cx, waterline=wl,
                 clear_box=(498, 372, 746, 1095), keep_rope=(612, 660, 440))
    raw, unshaded = verify_print(out, cutout, info, sheet)
    print({k: v for k, v in info.items() if k != "prof"},
          "print correlation raw", round(raw, 4), "with shading removed", round(unshaded, 4))
