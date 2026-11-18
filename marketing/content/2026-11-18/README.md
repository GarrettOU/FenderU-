# FenderU content pack, 18 Nov 2026

Garrett, 18 Nov 2026: "go post to facebook, instagram and tik tok daily. also, make me
new content for MAGA Fender covers for FenderU.com. Make it look professional. Sell my
FenderU MAGA fender covers."

Built in this folder: five vertical reels (1080 x 1920, 30 fps, H.264, silent AAC
track, 15 to 18 s each) and one five-slide carousel (1080 x 1350). Every photo is one
Garrett has approved (his site photos under `/media/southern/`, the three Runway
boat scenes he kept, in the clean 9 Nov versions, and the set-4 price card). Every
line on screen is copy he has already approved or his own words; nothing new was
written. Nothing in here is posted until he says so.

Look: the photo whole and centred on a softened copy of itself, one line of white
Oswald on a dark band in the upper third (clear of the TikTok and Instagram UI),
the set-4 red-white-blue mark, a slow push-in on every shot, 0.45 s dissolves, and
the approved set-4 price card as the end card. Built by
`scratchpad/pack/build.py` (ffmpeg zoompan + xfade; frames rendered at 2x in PIL).

## Reels

| # | File | Lines on screen, in order | Shots | Length |
|---|---|---|---|---|
| R1 | `reels/R1-fits-your-fenders.mp4` | Fits standard 8.5" x 26" cylindrical fenders. / Taylor Made. Dock Edge. Seachoice. Extreme Max BoatTector. (the fenders it fits) / Elastic top. Slips on in seconds. No tools. / Marine-grade neoprene. American flag and MAGA print. / Sold as a 2-pack. / price card | g04 detail, 02 detail, g01, 03 detail, 03 4:5 | 17.9 s |
| R2 | `reels/R2-show-your-patriotism.mp4` | Show your patriotism. / Marine-grade neoprene. / UV protected. Waterproof. Salt-resistant. / Keeps dock grit off the hull. / Sold as a 2-pack. / price card | 05 4:5, 02 detail, g05 Tigé, g06 teal, g01 | 17.4 s |
| R3 | `reels/R3-right-down-to-the-fenders.mp4` | Make America Great Again, right down to the fenders. / Marine-grade neoprene, flag print. / American flag and MAGA print. / Sold as a 2-pack. / price card | 03 4:5, g03 wake surf, 02 4:5, g04 | 14.8 s |
| R4 | `reels/R4-bare-fenders.mp4` | Bare fenders are a wasted opportunity. / Marine-grade neoprene, American flag and MAGA print. / UV protected, waterproof, salt-resistant. / Fits standard 8.5" x 26" cylindrical fenders. / price card | g02 dock, 05 detail, g06, g07 story | 15.4 s |
| R5 | `reels/R5-they-havent-seen-these-yet.mp4` | They haven't seen these yet. / American flag and MAGA print. Marine-grade neoprene. / Fits standard 8.5" x 26" cylindrical fenders. / Elastic top. Slips on in seconds. No tools. / American-owned and operated. / price card | g01, 02 4:5, g04, 05 4:5, g02 | about 18 s |

Frame grids for each are in `previews/`.

Where each line comes from: "Show your patriotism." and "Make America Great Again"
(approved 9 Oct); "Make America Great Again — right down to the fenders." (reel
caption, `marketing/captions.md`); "Bare fenders are a wasted opportunity."
(Facebook rotation item 8, 30 Oct); "They haven't seen these yet." (Garrett, 16 Oct,
and the P1 hook he posted himself on 13 Nov); every other line is from THE FACTS
(fit, brands, elastic top, neoprene, waterproof/salt/UV, dock grit, 2-pack, price,
American-owned).

## Carousel (TikTok photo post and Instagram carousel)

`carousel/C1-1.jpg` to `C1-5.jpg`: 1 "Boat fender covers, sold as a 2-pack." (g01) /
2 "Waterproof, salt-resistant, UV protected." (05 detail) / 3 "Keeps dock grit off
the hull." (g02) / 4 "Fits standard 8.5" x 26" cylindrical fenders." with the four
brands (g04) / 5 the set-4 price card. Caption: the Photo caption below.

## Captions (approved bank, unchanged)

Reel caption (R3, R5):
> Make America Great Again — right down to the fenders.
> Marine-grade neoprene, flag print. Sold as a 2-pack.
> $119 for the two-pack, shipping included.
> fenderu.com
> #maga #boatlife #lakelife #wakesurf #boating #americafirst #patriot

Photo caption (R1, R2, carousel):
> Show your patriotism.
> Marine-grade neoprene. UV protected, waterproof, salt-resistant. Fits standard 8.5" x 26" cylindrical fenders. Sold as a 2-pack.
> $119 for the two-pack, shipping included.
> fenderu.com
> #boataccessories #boatlife #marina #neoprene #boatgear #boating #americafirst #patriot

Group-post caption (R4):
> MAGA fender covers — marine-grade neoprene, sold as a 2-pack.
> Fits standard 8.5" x 26" cylindrical fenders. $119 for the two-pack, shipping included.
> American-owned and operated.
> Questions welcome.
> fenderu.com

## Songs (picked in the app at posting time, from the 5 Nov research)

R1 Little Bitty Pretty One (Thurston Harris) · R2 Life Is a Highway (Rascal Flatts) ·
R3 Calling Me from Miami (Blake Shelton) · R4 Lose Yourself, instrumental (Eminem) ·
R5 Ain't Seen Nothin' Yet (BTO). Garrett's own 13 Nov post used "This Is America"
(Austin Carter) and did 390 views and 17 likes in five days, the account's best;
reusing it on R5 is a fair call too.

## Where it goes once he says "post the pack"

- Instagram (@fenderu.kc, connector): R1 to R5 are added to the daily sequence after
  P6, one every third day, through the Reel steps in the Instagram daily task.
- TikTok (@fenderullc): from his phone with the song until the vidIQ connection is
  made; after that the daily task posts them without the song.
- Facebook Page: R1 to R5 go into the weekly reel slot (Make scenario 6138548).
- Pinterest: the carousel slides are five new vertical pins.

## Hooks that still need his yes (not built)

"THE BOAT ACCESSORY NOBODY AT THE DOCK HAS YET." / "MOST BOATERS HAVE NEVER SEEN A
FENDER COVER." / "PLAIN WHITE FENDERS ON A MAGA BOAT?" (P5, built 5 Nov) / "BOAT DADS
ARE HARD TO BUY FOR." (P6, built 5 Nov; the gift angle for December).
