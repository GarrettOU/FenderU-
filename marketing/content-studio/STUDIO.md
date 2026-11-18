# Content Studio log (FenderU)

Future runs: read this first, then `fenderu-standing-rules`, HQ.md §3, `marketing/tiktok-instagram/launch-plan.md`, `marketing/research/social-playbook-2026-11-09.md`, `marketing/captions.md`.

## Built

| Date | What | Where |
|---|---|---|
| 9 Nov 2026 | FenderU F1, F2-A, F2-B, F3-A, F3-B, F4, F5-A, F5-B (research section F). Each has a 9:16 master, a 1080x1350 still and a frame grid; F5 also has carousel slides | `2026-11-09/` (see PACK.md); builder `build_studio.py` |
| 11 Nov 2026 | FenderU G1-G5, all hooks approved (launch-plan P1, P2, P3, P5, P6). Each has a 9:16 master, a 1080x1350 still, a frame grid and a first frame | `2026-11-11/` (PACK.md); `STUDIO_PACK=2026-11-11 python3 build_studio.py` |
| 9 Nov 2026 | The Outfit: **not built**. The repo isn't reachable from this session (attach refused, no clone credentials) | — |

## Garrett's approvals (his word, with date)

| Date | Word | Covers |
|---|---|---|
| 6 Nov 2026 | "Approve the post." | TikTok/Instagram pack P1-P6 as shown, hooks P1-P6 included (launch-plan.md); P1 first. HQ.md §3 wins, so the P5 and P6 hooks are approved (confirmed by SI Claude Head, 9 Nov). |
| 13 Nov 2026 | "post G1" | G1 to the Facebook Page (reel, UploadVideo) and Pinterest (video pin). **Not yet posted:** the Make connector failed to connect on 13 Nov, so it posts as soon as Make is back. File: raw.githubusercontent.com/GarrettOU/FenderU-/79bc533/marketing/content-studio/2026-11-11/fenderu/G1/G1.mp4 (checked: 200, 2.07 MB) |
| — | none yet | Content Studio F-series |
| — | none yet | Keyword-style Pinterest title (DRAFT, PACK.md) |

## Posted (where, when)

- **13 Nov 2026: G1 posted to TikTok (@fenderullc) by Garrett from his phone** (he said "posted"). Caption: the reel caption with 5 hashtags. Sound: his pick from the in-app library, or none.
- **13 Nov 2026, 16:19 UTC: G1 posted to the FenderU Facebook Page** as a video. Page check passed: the connection lists exactly one page, FenderU 1235020856358701. Make scenario 6138548 used UploadVideo with the bank reel caption whole, execution fdaa7ab99c154ec8bf749659968d3d53, SUCCESS. The slot was borrowed from 6229425 and given back (6229425 active again, 6138548 inactive); 6374100 was not touched.
- **14 Nov 2026, 18:26 UTC: G1 still pinned to Pinterest** on Garrett's "pin G1 still" (13 Nov). Board: Patriotic Boat Fender Covers (763852855489296990). Title: "MAGA fender covers — marine-grade neoprene, sold as a 2-pack." Description: the group-post caption without hashtags. Link: https://fenderu.com/. Image: G1-still-1080x1350.jpg at 79bc533. Make scenario 6229425, execution 1f088f931d59407881d1143aea57c7e1, SUCCESS. The scenario was temporarily set to this single pin, then restored to its five-pin blueprint and left active.
- Video pins: not built. That needs a Pinterest media-upload step and waits on "build video pins".

## Performance checks

- 11 Nov run: nothing from the Studio has posted, so there is nothing of ours to measure.
  - Make shows the daily Page photo (6138535) succeeding every day 30 Oct to 11 Nov, and Pinterest (6229425) succeeding on 4, 6, 9 and 11 Nov.
  - The video scenario (6138548) last ran 28 Oct.
  - Make reports run status only, not reach. vidIQ has no social account connected (account list empty), so Instagram reach can't be read.
  - Next: once any F or G video posts, read its Facebook reach the following week. Until a channel can report reach, judge the pack by Garrett's picks rather than by numbers.

- **18 Nov run.**
  - G1 on TikTok: vidIQ public data shows video 7707688760661642526 at 416 views, 17 likes, 2 comments and 1 share after 5 days. It is 12 s long, matching G1 (11.6 s; the P1 draft is 15 s). HQ.md item 0d calls the 13 Nov TikTok post "P1". The length says G1, and both open on the same hook, "THEY HAVEN'T SEEN THESE YET." The old August posts sit at 106 to 114 views with 0 or 1 like.
  - vidIQ has no connected accounts yet: the 15 Nov links were never completed, so it can't publish or read private insights. The HQ daily TikTok task waits on the same connection.
  - Lesson 1: the one post with on-screen text over a cover-on-boat photo plus his own trending sound got about 4x the reach of the August posts. Keep the first frame on the cover and let him pick the sound in the app.
  - Lesson 2: TikTok reach is the only number we can read. Once vidIQ is connected, read Instagram and Facebook reach weekly before building more.

## Queued, waiting on his word

- F1, F2-A, F3-A, F4, F5-A: ready, approved hooks. Needs "post <id>".
- F2-B, F3-B, F5-B: DRAFT hooks. Needs "approve <id> hook" or "no".
- F3-A/B use Runway photos: AI label on when posted.
- **G1: approved to post 13 Nov ("post G1"), waiting on the Make connector.** TikTok and Instagram stay on his phone.
- G2-G5 (11 Nov): ready, approved hooks. Needs "post G<n>" or "no G<n>". G3 uses Runway photos: AI label on.
- The Outfit: out of scope (see standing notes).

## Standing notes

- **18 Nov: no new pack built this run, on purpose.** The 18 Nov main-session pack (`marketing/content/2026-11-18/`, R1-R5 and a carousel, approved and in every rotation) already uses the same approved hooks. Waiting to post: F (8, of which 5 are postable), G2-G5, R1-R5 and P1-P6. Every approved hook line has now been built at least twice. A new pack would only repeat them with different crops, so the next one waits on new lines from Garrett, or on his "build H pack" (repeats with fresh photo sequences).

- **Music (13 Nov):** @fenderullc is a TikTok Business account. None of the launch-plan songs show up in its sound library (Garrett: "none of that music on on my tik tok app. none."). From now on, pack notes say "any sound from your in-app library, or none". No band songs unless he switches the account to Personal.
- **Getting files to his phone:** send each approved video with SendUserFile so he can Save Video from the Claude app before posting.

- **The Outfit is out of the Studio's scope** until a lodge has signed and SI Claude Head says otherwise (Head, 9 Nov 16:25 UTC, replacing its 16:23 note). Do not try the Outfit repo again. The weekly run is FenderU only: five videos, platform exports, previews, PACK.md, draft PR, and one report under 25 lines.

- Imagery: any FenderU still or video uses `marketing/runway/clean/` only, never `sharp/` or `web/`. The Facebook and Pinterest rotations move to clean/ (commit 8792d87) once Garrett says "fix posters" (SI Claude Head, 9 Nov).
