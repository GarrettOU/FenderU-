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
| — | none yet | Content Studio F-series |
| — | none yet | Keyword-style Pinterest title (DRAFT, PACK.md) |

## Posted (where, when)

Nothing from the Content Studio has been posted.

## Performance checks

- 11 Nov run: nothing from the Studio has posted, so there is nothing of ours to measure.
  - Make shows the daily Page photo (6138535) succeeding every day 30 Oct to 11 Nov, and Pinterest (6229425) succeeding on 4, 6, 9 and 11 Nov.
  - The video scenario (6138548) last ran 28 Oct.
  - Make reports run status only, not reach. vidIQ has no social account connected (account list empty), so Instagram reach can't be read.
  - Next: once any F or G video posts, read its Facebook reach the following week. Until a channel can report reach, judge the pack by Garrett's picks rather than by numbers.

## Queued, waiting on his word

- F1, F2-A, F3-A, F4, F5-A: ready, approved hooks. Needs "post <id>".
- F2-B, F3-B, F5-B: DRAFT hooks. Needs "approve <id> hook" or "no".
- F3-A/B use Runway photos: AI label on when posted.
- G1-G5 (11 Nov): ready, approved hooks. Needs "post G<n>" or "no G<n>". G3 uses Runway photos: AI label on.
- The Outfit: out of scope (see standing notes).

## Standing notes

- **The Outfit is out of the Studio's scope** until a lodge has signed and SI Claude Head says otherwise (Head, 9 Nov 16:25 UTC, replacing its 16:23 note). Do not try the Outfit repo again. The weekly run is FenderU only: five videos, platform exports, previews, PACK.md, draft PR, and one report under 25 lines.

- Imagery: any FenderU still or video uses `marketing/runway/clean/` only, never `sharp/` or `web/`. The Facebook and Pinterest rotations move to clean/ (commit 8792d87) once Garrett says "fix posters" (SI Claude Head, 9 Nov).
