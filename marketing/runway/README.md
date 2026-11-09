# Runway photos (28 Oct 2026)

Garrett made these himself in Runway AI and sent them on 28 Oct 2026 with the
instruction to use them ("i'm going to send you some more pics to use"). They
are his, approved by him, and the only AI boat scenes allowed in FenderU
marketing. The rule against pasting the real cover onto AI scenes still stands
for anything built here.

| File | Scene | Fit note |
|---|---|---|
| 01-yellow-cruiser-parade.jpg | yellow cruiser under way in a boat parade | **retired 30 Oct** (out of focus, Garrett) |
| 02-red-express-cruiser.jpg | red express cruiser, flags on the rails | cruiser, the 25-35 ft market. **Kept, sharpened** |
| 03-yellow-bowrider.jpg | yellow bowrider under way | bowrider. **Kept, sharpened** |
| 04-red-bowrider-bimini.jpg | red bowrider with bimini, couple aboard | **retired 30 Oct** (out of focus, Garrett) |
| 05-teal-wakeboat-party.jpg | teal wake boat in a parade crowd | wake boat. **Kept, sharpened** |
| 06-white-wakeboat-party.jpg | white wake boat in a parade crowd | **retired 30 Oct** (out of focus, Garrett) |
| 07-wakeboat-maga-crew.jpg | wake boat, four people in red hats | **not used**: hat and shirt lettering is garbled |

Originals are 2752 x 1536. `web/` and `crops/` are the first-pass (soft)
versions and are no longer used anywhere.

**30 Oct 2026, Garrett:** "the new pictures made by runway aren't in focus and
shouldn't be used. there's too many of those too. find a way to make them in
focus and use half of them. the middle middle, right middle, and middle bottom
photos." Those gallery positions are 02, 03 and 05. `sharp/` holds the only
versions now in use: each of the three at 1600 wide (`<name>.jpg`), square
(`-sq`, 1350), vertical 4:5 (`-45`, 1080 x 1350) and a 4:5 detail crop close
on the covers (`-detail`), plus two site sizes (`-1100`, 1100 x 614, and
`-720`, 720 x 402) for the gallery.

**4 Nov 2026, Garrett:** "clean up and focus the bottom 3 pictures under 'MAGA
on the water' because they are fuzzy and out of focus. stop making these
mistakes." The first pass (commit bfdc93e, two-pass unsharp mask) was not
enough: the site was downscaling a 1600-px file to a 342-px card, which
softened it again. Every file in `sharp/` was regenerated at commit ca73ec5
with a stronger pipeline applied at the output size, after the Lanczos
downscale: ImageMagick adaptive-sharpen 0x1.2 and unsharp 0x1.5+1.2+0.02,
then a fine unsharp mask (radius 0.7, 100 %) and 5 % contrast. Nothing in the
picture was redrawn. The site now serves the 720 and 1100 files through
`srcset` so phones get the 1100 file at about 2.8x and desktops the 720 file at
2x, both sharpened for that size. Pinned URLs use commit ca73ec5; the bfdc93e
files are retired.

Where the three are used:
- Daily Facebook Page post rotation: 12 of 24 items (wide, square, 4:5 and detail of each), never two days running.
- Pinterest: at most two of every five pins, until each of the nine remaining variants has been pinned once.
- Site gallery: `/media/runway/02-…`, `03-…`, `05-…` (`-720` and `-1100`, with `srcset`) served by the front worker from `sharp/` at ca73ec5.
- Channel-owner DM (`marketing/outreach/channel-owner-dm.md`): 05 or 02.
- Boaters for Trump group posts Garrett pastes himself (`marketing/outreach/boaters-for-trump-posts.md`): 02, 03, 05.
Still posted before the change and not yet taken down: the 28 Oct Facebook reel (`marketing/reels/runway-reel-01-fb.mp4`), which uses all six; two 30 Oct pins on 01 and 06 are deleted and re-made by the next Pinterest run.

**9 Nov 2026, Garrett:** "I've said multiple times to clean up the clarity of the
Runway pictures on my website for FenderU and it's still not done." Diagnosis by
the SI Claude Head: the `sharp/` files were over-sharpened, not blurry. Measured
Laplacian variance at 720 px: `sharp/*-720` 25,000 to 40,000, `sharp/*-1100`
13,000 to 21,000, against 400 to 700 for Garrett's real site photos. That is the
halo-and-crunch look he was seeing, and the desktop browser (2x) was picking the
most over-processed file (720). The 2752 px originals are clean. `clean/` holds
each kept photo at 720, 1100, 1440 and 2200 wide, made with a single Lanczos
downscale from the original and one light unsharp pass (0x0.6+0.5+0.008),
measured 2,000 to 5,000. The site now serves `clean/` under `/media/runway/v3/`
with a four-step `srcset`, so 2x and 3x screens get a file at or above their
pixel density. `sharp/` stays for the Facebook and Pinterest rotations until
those prompts are repointed; nothing was deleted.
