"""Place Garrett's REAL cover photo onto a fender in a boat scene.

Rule (26 Oct): never let an AI model draw the cover. The cover pixels come only
from marketing/src/cutout/*.png and are only resized, shaded (brightness/colour)
and given a contact shadow and reflection here. Then verify_print() checks the
placed pixels against the original before anything is shown.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

def clear_fender(scene, box, keep_rope=None, thresh=70, grow=6):
    """Paint out the scene's own fender (dark pixels inside box, grown a few px
    to catch its soft shadow) by blending across each row from the untouched
    pixels on either side, so nothing of it peeks out from behind the real
    cover. keep_rope=(x0,x1,ymax) protects the bow line above the cover."""
    from PIL import ImageFilter as F
    a = np.array(scene).astype(np.float32)
    x0, y0, x1, y1 = box
    dark = Image.fromarray(((a.max(-1) < thresh) * 255).astype(np.uint8))
    m = np.array(dark.filter(F.MaxFilter(2 * grow + 1))) > 0
    keep = np.zeros_like(m)
    keep[:y0, :] = keep[y1:, :] = True; keep[:, :x0] = keep[:, x1:] = True
    if keep_rope:
        keep[:keep_rope[2], keep_rope[0]:keep_rope[1]] = True
    m &= ~keep
    for y in range(y0, y1):
        row = m[y]
        if not row.any():
            continue
        xs = np.arange(a.shape[1])
        for c in range(3):
            a[y, row, c] = np.interp(xs[row], xs[~row], a[y, ~row, c])
    return Image.fromarray(a.astype(np.uint8), "RGB")

def place(scene_path, cutout_path, out_path, fender_top, fender_bottom, center_x,
          eye_y=270, crop_top=230, body_center=347, waterline=None,
          warmth=(1.03, 1.0, 0.96), light=0.94, rim=0.72, clear_box=None, keep_rope=None):
    scene = Image.open(scene_path).convert("RGB")
    if clear_box:
        scene = clear_fender(scene, clear_box, keep_rope)
    cut = Image.open(cutout_path).convert("RGBA")
    bottom = int(np.where(np.array(cut)[..., 3] > 128)[0].max())
    s = (fender_bottom - fender_top) / (bottom - eye_y)
    cut = cut.crop((0, crop_top, cut.width, bottom + 1))
    w, h = round(cut.width * s), round(cut.height * s)
    cut = cut.resize((w, h), Image.LANCZOS)          # resize only
    x0 = round(center_x - body_center * s)
    y0 = round(fender_top - (eye_y - crop_top) * s)

    # light match: overall level, warm daylight, and a cylinder falloff to the right
    a = np.array(cut).astype(np.float32)
    xs = np.linspace(0, 1, w)
    prof = light * (1 - (1 - rim) * np.clip((xs - 0.55) / 0.45, 0, 1) ** 1.6)
    prof *= 1 - 0.10 * np.clip((0.12 - xs) / 0.12, 0, 1)
    for c in range(3):
        a[..., c] = np.clip(a[..., c] * prof[None, :] * warmth[c], 0, 255)
    shaded = Image.fromarray(a.astype(np.uint8), "RGBA")
    alpha = shaded.split()[3]

    out = scene.copy()
    # soft contact shadow on the hull behind/left of the fender
    sh = Image.new("L", scene.size, 0)
    sh.paste(alpha.point(lambda v: int(v * 0.55)), (x0 - 16, y0 + 10))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    out = Image.composite(Image.new("RGB", scene.size, (0, 0, 0)), out, sh)

    # faint, blurred water reflection below the waterline
    if waterline is not None:
        refl = shaded.transpose(Image.FLIP_TOP_BOTTOM)
        r = Image.new("RGBA", scene.size, (0, 0, 0, 0))
        r.paste(refl, (x0, waterline + (waterline - (y0 + h))))
        r = r.filter(ImageFilter.GaussianBlur(3))
        ra = np.array(r).astype(np.float32)
        ra[..., 3] *= 0.22
        ra[:waterline, :, 3] = 0
        r = Image.fromarray(ra.astype(np.uint8), "RGBA")
        out = Image.alpha_composite(out.convert("RGBA"), r).convert("RGB")

    out.paste(shaded, (x0, y0), shaded)
    out.save(out_path, quality=95)
    return dict(scale=s, x0=x0, y0=y0, w=w, h=h, crop_top=crop_top)

def verify_print(out_path, cutout_path, info, sheet_path):
    """Side-by-side of the placed cover vs the original photo at the same size,
    plus a structural score. Returns the correlation of the print area."""
    cut = Image.open(cutout_path).convert("RGBA")
    bottom = int(np.where(np.array(cut)[..., 3] > 128)[0].max())
    cut = cut.crop((0, info["crop_top"], cut.width, bottom + 1)).resize((info["w"], info["h"]), Image.LANCZOS)
    placed = Image.open(out_path).convert("RGB").crop(
        (info["x0"], info["y0"], info["x0"] + info["w"], info["y0"] + info["h"]))
    m = np.array(cut)[..., 3] > 250
    g1 = np.array(cut.convert("L")).astype(float)[m]
    g2 = np.array(placed.convert("L")).astype(float)[m]
    corr = float(np.corrcoef(g1, g2)[0, 1])
    # sheet: original (left) | placed (right), enlarged 3x
    k = 3
    orig = Image.new("RGB", cut.size, (255, 255, 255)); orig.paste(cut, (0, 0), cut)
    a, b = orig.resize((info["w"] * k, info["h"] * k)), placed.resize((info["w"] * k, info["h"] * k))
    sheet = Image.new("RGB", (a.width * 2 + 60, a.height + 40), (235, 235, 235))
    sheet.paste(a, (20, 20)); sheet.paste(b, (a.width + 40, 20))
    sheet.save(sheet_path, quality=92)
    return corr

if __name__ == "__main__":
    scene, cutout, out, sheet = sys.argv[1:5]
    t, btm, cx, wl = map(int, sys.argv[5:9])
    info = place(scene, cutout, out, t, btm, cx, waterline=wl,
                 clear_box=(498, 372, 748, 1095), keep_rope=(612, 660, 440))
    corr = verify_print(out, cutout, info, sheet)
    print(info, "print correlation", round(corr, 4))
