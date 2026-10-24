"""Builds marketplace images for Amazon and Etsy from Garrett's own photos.

listings/images/
  01-main-white.jpg     2000x2000, pure white (255,255,255), the 2-pack, no text
                        (Amazon main-image rule: white background, product ~85%)
  02-single-white.jpg   2000x2000, one cover, pure white, no text
  03-on-the-boat.jpg    2000x2000, Garrett's boat photo (lifestyle)
  04-detail.jpg ... 06  his set-3 graphics padded to square (Etsy only: they carry
                        price and web address, which Amazon images may not)
  07-detail-photo.jpg   close on the print, no text (Amazon and Etsy)
Usage: python3 marketing/make_listing_images.py
"""
import os
from PIL import Image
from make_studio import cover

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "listings", "images")
S = 2000


def white(name, covers):
    c = Image.new("RGB", (S, S), (255, 255, 255))
    h = round(S * 0.86)
    ims = [cover(n, h) for n in covers]
    gap = 40
    total = sum(i.width for i in ims) + gap * (len(ims) - 1)
    x = (S - total) // 2
    for im in ims:
        c.paste(im, (x, (S - h) // 2), im)
        x += im.width + gap
    c.save(os.path.join(OUT, name), quality=95)


def square_from(name, path, bg=(23, 25, 27)):
    im = Image.open(os.path.join(HERE, path)).convert("RGB")
    r = S / max(im.size)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    c = Image.new("RGB", (S, S), bg)
    c.paste(im, ((S - im.width) // 2, (S - im.height) // 2))
    c.save(os.path.join(OUT, name), quality=93)


def main():
    os.makedirs(OUT, exist_ok=True)
    white("01-main-white.jpg", [5, 1])
    white("02-single-white.jpg", [5])
    im = Image.open(os.path.join(HERE, "src", "media_southern_g02-dock-square.jpg")).convert("RGB")
    im.resize((S, S), Image.LANCZOS).save(os.path.join(OUT, "03-on-the-boat.jpg"), quality=93)
    square_from("04-detail.jpg", "graphics/set3/g4-detail-square.jpg")
    square_from("05-fit.jpg", "graphics/set3/g5-fit-story.jpg")
    square_from("06-sold-as-2-pack.jpg", "graphics/set3/g3-dock-split-portrait.jpg")
    square_from("07-detail-photo.jpg", "src/media_southern_g04-detail-portrait.jpg", bg=(255, 255, 255))
    print(sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
