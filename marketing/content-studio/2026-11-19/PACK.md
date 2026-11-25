# H pack, 19 Nov 2026: new boats, real video, same cover

> **Internal document. Never paste from it.** Copy only from the caption blocks.

Garrett, 19 Nov: "get tik tok going more often with new posts. create new reels for me to approve. use new boats, new videos, same MAGA fender covers that are sold at FenderU.com."

**Nothing here has been posted.** Each video goes up only after "post H1" (and so on). Built by `build_h.py` (b-roll fetched to the scratchpad, not committed).

## How the brief was met, and what was not done

- **Cover:** every cover pixel comes from Garrett's own photos (`marketing/src/media_southern_g01` to `g04`). They are cropped and scaled only. Nothing is pasted, redrawn, relit or AI-touched.
- **New boats and new video:** these are real filmed clips, not AI, from Pexels, which is free for commercial use. Each clip shows a different boat and setting. No cover was composited onto these boats.
- **Covers on the new boats were not attempted.** The October composite (`marketing/composite/`) was rejected as "looks fake or AI". The stock clips are hand-held and have no American-boat cylinder fender to lock onto, so tracking would read as pasted on. The AI scene tools here can't do it either: OpenArt has 9 credits, and vidIQ AI video costs about 80 credits per 8-second clip against a balance of 85. To show the cover on new boats for real: customer photos (the $20 photo offer) or a phone video at a dock.
- **Text:** the hook on all six is "THEY HAVEN'T SEEN THESE YET." (P1, approved 6 Nov), the line on his best TikTok so far. Every other line is approved copy. The banned-list check found 0 hits. Side margins are 129 px or more.
- **Spec:** 1080x1920, 30 fps, H.264, silent AAC track, 11.0 s each. The first frame is the cover on a fender on a boat. The end card reads "$119 FOR THE TWO-PACK, FREE SHIPPING." and "FENDERU.COM".
- **Sound:** none in the file. On TikTok he picks any sound from his in-app library, or posts it silent.

## Videos

| Video | New boat (real footage, credit) | Line over the boat | Line over his photo | Caption |
|---|---|---|---|---|
| H1 | Pontoon at a lake dock (Richard L, Pexels 32236223) | SHOW YOUR PATRIOTISM. | FITS STANDARD 8.5" x 26" CYLINDRICAL FENDERS. | Reel |
| H2 | Red runabout on a lake (iPhone Snaps, Pexels 33409724) | MAKE AMERICA GREAT AGAIN | SOLD AS A 2-PACK. | Reel |
| H3 | Cruiser in a marina slip (Teju, Pexels 37216200) | BARE FENDERS ARE A WASTED OPPORTUNITY. | SLIPS ON IN SECONDS, NO TOOLS. | Photo |
| H4 | Lake dock at sunset (Melody Manzano, Pexels 17833560) | MAKE AMERICA GREAT AGAIN. (rebuilt 25 Nov; the old line is banned) | MARINE-GRADE NEOPRENE, FLAG PRINT. | Reel |
| H5 | Boat across a lake, drone (Jaxon Matthew Willis, Pexels 12533599) | AMERICAN-OWNED AND OPERATED. | UV PROTECTED, WATERPROOF, SALT-RESISTANT. | Group |
| H6 | Yachts at a marina (Mihaela Claudia Puscas, Pexels 39796220) | MAGA FENDER COVERS / MARINE-GRADE NEOPRENE, SOLD AS A 2-PACK. | FITS STANDARD 8.5" x 26" CYLINDRICAL FENDERS. | Group |

## TikTok caption (all six; from the reel caption, hashtags trimmed)

> Make America Great Again.
> $119 for the two-pack, shipping included.
> fenderu.com
> #maga #boatlife #boating #americafirst #patriot

The full reel, photo and group captions are in `2026-11-11/PACK.md`, unchanged.
