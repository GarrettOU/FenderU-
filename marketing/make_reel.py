"""Builds marketing/reels/maga-on-the-water.mp4 (1080x1920, silent AAC track).

Scenes are site photos with a slow push-in and a charcoal text band in the
site's style (thin red/white/navy rule, letter-spaced uppercase). All copy is
Garrett's approved wording only (see captions.md); the end card carries the current price.
Usage: python3 marketing/make_reel.py <path-to-Oswald-dir> [studio]
"studio" builds maga-studio.mp4 from the white-background photos
(run make_studio.py first for the src/studio-*.jpg plates).
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "src"), os.path.join(HERE, "reels")
TMP = os.path.join(HERE, ".build")
FONTS = sys.argv[1]
W, H, FPS = 1080, 1920, 30
CHAR, WHITE, RED, NAVY, MUTED = (35, 37, 38), (255, 255, 255), (204, 34, 0), (27, 42, 74), (190, 194, 198)

def font(weight, size):
    return ImageFont.truetype(os.path.join(FONTS, f"{weight}/Oswald_{weight}.ttf"), size)

def spaced(draw, xy, text, fnt, fill, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + spacing

def spaced_width(draw, text, fnt, spacing):
    return sum(draw.textlength(c, font=fnt) + spacing for c in text) - spacing

def rule(draw, x, y):
    for i, c in enumerate((RED, WHITE, NAVY)):
        draw.rectangle([x + i * 46, y, x + i * 46 + 38, y + 4], fill=c)

def band(title, sub, name):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top = H - 420
    d.rectangle([0, top, W, H], fill=CHAR + (235,))
    rule(d, 72, top + 70)
    tf = font("700Bold", 92)
    d.text((72, top + 100), title, font=tf, fill=WHITE)
    spaced(d, (74, top + 240), sub.upper(), font("400Regular", 34), MUTED, 5)
    spaced(d, (74, H - 90), "FENDERU.COM", font("500Medium", 30), MUTED, 8)
    img.save(os.path.join(TMP, name))

def endcard(name):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top = H - 640
    d.rectangle([0, top, W, H], fill=CHAR + (245,))
    rule(d, 72, top + 80)
    d.text((72, top + 110), "$119 THE PAIR", font=font("700Bold", 150), fill=WHITE)
    spaced(d, (76, top + 320), "FREE SHIPPING", font("500Medium", 52), WHITE, 10)
    spaced(d, (76, top + 400), "UPS WITH TRACKING", font("400Regular", 34), MUTED, 5)
    spaced(d, (76, top + 450), "SOLD AS A 2-PACK", font("400Regular", 34), MUTED, 5)
    t = "FENDERU.COM"
    f = font("600SemiBold", 56)
    spaced(d, (W - 72 - spaced_width(d, t, f, 10), H - 110), t, f, WHITE, 10)
    img.save(os.path.join(TMP, name))

SCENES = [
    ("media_southern_g03-wake-surf-portrait.jpg", "MAKE AMERICA\nGREAT AGAIN", "Show your patriotism.", 4.0),
    ("media_southern_g01-pair-portrait.jpg", "MARINE-GRADE\nNEOPRENE", "UV protected. Waterproof. Salt-resistant.", 4.0),
    ("media_southern_g04-detail-portrait.jpg", 'FITS 8.5" x 26"\nFENDERS', "Slips on in seconds. No tools.", 4.0),
    ("studio-pair.jpg", None, None, 5.0),
]

STUDIO_SCENES = [
    ("media_southern_g03-wake-surf-portrait.jpg", "MAKE AMERICA\nGREAT AGAIN", "Show your patriotism.", 3.5),
    ("studio-single.jpg", "MARINE-GRADE\nNEOPRENE", "UV protected. Waterproof. Salt-resistant.", 3.5),
    ("studio-pair-2.jpg", 'FITS 8.5" x 26"\nFENDERS', "Slips on in seconds. No tools.", 3.5),
    ("studio-pair.jpg", None, None, 5.0),
]
STUDIO = len(sys.argv) > 2 and sys.argv[2] == "studio"
if STUDIO:
    SCENES = STUDIO_SCENES

def main():
    os.makedirs(TMP, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    segs = []
    for i, (photo, title, sub, dur) in enumerate(SCENES):
        ov = f"ov{i}.png"
        if title:
            band(title, sub, ov)
            # multi-line titles need the band raised; redraw with line spacing
            if "\n" in title:
                img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
                top = H - 520
                d.rectangle([0, top, W, H], fill=CHAR + (235,))
                rule(d, 72, top + 70)
                d.multiline_text((72, top + 100), title, font=font("700Bold", 92), fill=WHITE, spacing=6)
                spaced(d, (74, top + 340), sub.upper(), font("400Regular", 34), MUTED, 5)
                spaced(d, (74, H - 90), "FENDERU.COM", font("500Medium", 30), MUTED, 8)
                img.save(os.path.join(TMP, ov))
        else:
            endcard(ov)
        frames = int(dur * FPS)
        seg = os.path.join(TMP, f"seg{i}.mp4")
        # End card shows the whole product above the band instead of a close crop.
        fit = (f"crop=iw*0.76:ih:0:0,scale={W*2}:{(H-640)*2}:force_original_aspect_ratio=decrease,"
               f"pad={W*2}:{H*2}:(ow-iw)/2:120:color=0x232526," if not title and not photo.startswith("studio") else
               f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},")
        vf = (f"[0:v]{fit}"
              f"zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}[bg];"
              f"[bg][1:v]overlay=0:0,format=yuv420p,fade=t=in:st=0:d=0.3,fade=t=out:st={dur-0.3}:d=0.3[v]")
        subprocess.run([FF, "-v", "error", "-y", "-loop", "1", "-i", os.path.join(SRC, photo),
                        "-i", os.path.join(TMP, ov), "-filter_complex", vf, "-map", "[v]",
                        "-t", str(dur), "-r", str(FPS), "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", seg], check=True)
        segs.append(seg)
    lst = os.path.join(TMP, "list.txt")
    open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    out = os.path.join(OUT, "maga-studio.mp4" if STUDIO else "maga-on-the-water.mp4")
    subprocess.run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100", "-shortest",
                    "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS),
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out], check=True)
    print(out)

if __name__ == "__main__":
    main()
