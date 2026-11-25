#!/usr/bin/env python3
"""H pack (19 Nov 2026): new boats, real video, same cover.

Garrett, 19 Nov: "get tik tok going more often with new posts. create new reels
for me to approve. use new boats, new videos, same MAGA fender covers that are
sold at FenderU.com."

Every cover pixel comes from Garrett's own photos (marketing/src/media_southern_g0*),
cropped and scaled only. The new boats are real filmed footage (Pexels, free for
commercial use, credited in PACK.md), never AI, and they never carry a cover.
No cover is composited onto anything. On-screen text uses approved lines only
(build_studio.py --check runs them through the banned list).

Usage: python3 build_h.py BROLL_DIR [H1 ...]
"""
import os, subprocess, sys
import numpy as np
import build_studio as b

OUT = os.path.join(b.HERE, "2026-11-19", "fenderu")
W, H, FPS = b.W, b.H, b.FPS
HOOK = ("THEY HAVEN'T SEEN THESE YET.", "APPROVED",
        "P1, launch-plan.md (approved 6 Nov); his best TikTok so far (13 Nov, 416 views)")
FIT = 'FITS STANDARD 8.5" x 26" CYLINDRICAL FENDERS.'

# clip shot: ("CLIP", seconds, (pexels_id, start_s), text, sub)
VIDEOS = [
    dict(id="H1", title="Pontoon at a lake dock", caption="reel", shots=[
        ("g03", 2.8, (0.58, 0.55, 1.00, 1.07, 0), "HOOK", None),
        ("CLIP", 3.2, ("32236223", 2.0), "SHOW YOUR PATRIOTISM.", None),
        ("g04", 2.2, (0.45, 0.45, 1.00, 1.06, 0), FIT, None),
        ("END", 2.8, None, None, None)]),
    dict(id="H2", title="Runabout on the lake", caption="reel", shots=[
        ("g01", 2.8, (0.60, 0.52, 1.00, 1.07, 0), "HOOK", None),
        ("CLIP", 3.2, ("33409724", 2.6), "MAKE AMERICA GREAT AGAIN", None),
        ("g04", 2.2, (0.45, 0.35, 1.05, 1.00, 0), "SOLD AS A 2-PACK.", None),
        ("END", 2.8, None, None, None)]),
    dict(id="H3", title="Cruiser in a marina slip", caption="photo", shots=[
        ("g02", 2.8, (0.45, 0.55, 1.00, 1.06, 0), "HOOK", None),
        ("CLIP", 3.2, ("37216200", 1.0), "BARE FENDERS ARE A WASTED OPPORTUNITY.", None),
        ("g04", 2.2, (0.45, 0.40, 1.00, 1.06, 0), "SLIPS ON IN SECONDS, NO TOOLS.", None),
        ("END", 2.8, None, None, None)]),
    dict(id="H4", title="Lake dock at sunset", caption="reel", shots=[
        ("g03", 2.8, (0.55, 0.62, 1.20, 1.28, 0), "HOOK", None),
        ("CLIP", 3.2, ("17833560", 3.0), "MAKE AMERICA GREAT AGAIN.", None),
        ("g01", 2.2, (0.60, 0.55, 1.06, 1.00, 0), "MARINE-GRADE NEOPRENE, FLAG PRINT.", None),
        ("END", 2.8, None, None, None)]),
    dict(id="H5", title="Boat across the lake (drone)", caption="group", shots=[
        ("g01", 2.8, (0.62, 0.55, 1.10, 1.18, 0), "HOOK", None),
        ("CLIP", 3.2, ("12533599", 12.0), "AMERICAN-OWNED AND OPERATED.", None),
        ("g02", 2.2, (0.42, 0.55, 1.00, 1.00, 0.10), "UV PROTECTED, WATERPROOF, SALT-RESISTANT.", None),
        ("END", 2.8, None, None, None)]),
    dict(id="H6", title="Yachts at the marina", caption="group", shots=[
        ("g04", 2.8, (0.45, 0.45, 1.00, 1.07, 0), "HOOK", None),
        ("CLIP", 3.2, ("39796220", 2.0), "MAGA FENDER COVERS", "MARINE-GRADE NEOPRENE, SOLD AS A 2-PACK."),
        ("g03", 2.2, (0.58, 0.55, 1.00, 1.06, 0), FIT, None),
        ("END", 2.8, None, None, None)]),
]
for v in VIDEOS:
    v["hook"] = HOOK

CREDITS = {
    "32236223": ("Richard L", "https://www.pexels.com/video/scenic-view-of-lake-with-pontoon-boat-32236223/"),
    "33409724": ("iPhone Snaps", "https://www.pexels.com/video/speedboat-racing-through-scenic-lake-waters-33409724/"),
    "37216200": ("Teju", "https://www.pexels.com/video/serene-marina-with-boat-docked-on-a-foggy-day-37216200/"),
    "17833560": ("Melody Manzano", "https://www.pexels.com/video/a-dock-with-two-boats-on-it-at-sunset-17833560/"),
    "12533599": ("Jaxon Matthew Willis", "https://www.pexels.com/video/drone-footage-of-a-motorboat-in-a-lake-12533599/"),
    "39796220": ("Mihaela Claudia Puscas", "https://www.pexels.com/video/serene-marina-yacht-reflections-during-summer-39796220/"),
}


def clip_frames(broll, pid, start, nframes):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", os.path.join(broll, f"c_{pid}.mp4"),
           "-vf", f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}",
           "-frames:v", str(nframes), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (W * H * 3)
    frames = [b.Image.frombytes("RGB", (W, H), raw[i * W * H * 3:(i + 1) * W * H * 3]) for i in range(n)]
    while len(frames) < nframes:          # hold last frame if the clip runs short
        frames.append(frames[-1])
    return frames


def build(v, broll):
    vid = v["id"]; d = os.path.join(OUT, vid); os.makedirs(d, exist_ok=True)
    mp4 = os.path.join(d, f"{vid}.mp4")
    total = sum(round(s[1] * FPS) for s in v["shots"])
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-preset", "slow", "-crf", "20", "-g", "60", "-c:a", "aac", "-b:a", "128k", "-shortest",
         "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
    grid_idx = set(int(i * (total - 1) / 14) for i in range(15))
    grid, n = [], 0
    for shot in v["shots"]:
        nf = round(shot[1] * FPS)
        if shot[0] == "CLIP":
            layer = b.text_band((W, H), shot[3], shot[4], y_top=330, size=72) if shot[3] else None
            frames = clip_frames(broll, shot[2][0], shot[2][1], nf)
        else:
            layer = b.shot_layer(v, shot)
            frames = [b.frame(shot, i / max(nf - 1, 1)) for i in range(nf)]
        for fr in frames:
            im = b.overlay(fr, layer)
            enc.stdin.write(im.tobytes())
            if n in grid_idx: grid.append((n, im.copy()))
            n += 1
    enc.stdin.close(); enc.wait(); assert enc.returncode == 0
    grid[0][1].save(os.path.join(d, f"{vid}-frame1.jpg"), quality=92)
    tw, th, hdr = 216, 384, 90
    g = b.Image.new("RGB", (tw * 5, th * 3 + hdr), (245, 245, 245)); gd = b.ImageDraw.Draw(g)
    gd.rectangle([0, 0, g.width, hdr], fill=(24, 110, 60))
    gd.text((16, 10), f"{vid}  ·  {v['title']}  ·  HOOK APPROVED", font=b.font(30), fill=b.WHITE)
    gd.text((16, 52), f"\"{v['hook'][0]}\"  ·  {total / FPS:.1f}s  ·  new boat = real footage, cover = your photo",
            font=b.font(20, med=True), fill=b.WHITE)
    for k, (fn, im) in enumerate(grid[:15]):
        g.paste(im.resize((tw, th), b.Image.LANCZOS), ((k % 5) * tw, hdr + (k // 5) * th))
        gd.text(((k % 5) * tw + 6, hdr + (k // 5) * th + 4), f"{fn / FPS:.1f}s", font=b.font(18, med=True), fill=(255, 230, 0))
    g.save(os.path.join(d, f"{vid}-grid.jpg"), quality=88)
    s0 = v["shots"][0]
    b.overlay(b.frame(s0, 0.0, (1080, 1350)), b.shot_layer(v, s0, (1080, 1350), y_top=150)).save(
        os.path.join(d, f"{vid}-still-1080x1350.jpg"), quality=92)
    return total / FPS


def onscreen(v):
    t = [v["hook"][0]]
    for s in v["shots"]:
        if s[3] and s[3] != "HOOK": t.append(s[3])
        if s[4]: t.append(s[4])
    return t + [b.END_PRICE, b.END_SITE]


if __name__ == "__main__":
    broll, want = sys.argv[1], set(sys.argv[2:])
    bad = [(v["id"], t) for v in VIDEOS for t in onscreen(v) if b.banned_hits(t)]
    if bad: sys.exit(f"BANNED: {bad}")
    for v in VIDEOS:
        if want and v["id"] not in want: continue
        print(v["id"], build(v, broll), "s")
