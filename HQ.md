# FenderU HQ

Single home base for FenderU. Last consolidated **23 Oct 2026** from the old sessions "Selling Fender covers", "MAGA fender covers sales setup", the FenderU bits of "CEO agent for agentic business", every FenderU scheduled task, and their latest runs.

> **This repo is public.** Anything here can be read by anyone, including prospects and the supplier. Wholesale terms, costs, margin, inventory count, customer names and prospect phone numbers/addresses are deliberately **left out**. They live in the reply desk's task prompt and in Garrett's chat, not here.

---

## 1. Current state

| | |
|---|---|
| Site | FenderU.com is live. `fenderu-front` worker owns `/api/*`, and `fenderu` serves the pages. Checkout is one Place Order button with card / PayPal / Venmo options (commit e548296, 19 Oct). Cards and PayPal both run through PayPal. **Stripe is built but dormant** because there's no key. |
| Price | $119 with free shipping. It is the only public price. |
| Sales | **No confirmed revenue.** On 21 Oct Garrett said "we've had no sales or revenue yet." The order DB holds **1 row** (5 Oct, $119, PayPal, a Leawood KS buyer). It is unverified whether that row was a real paid order or a friend/test. There was also a $114 Stripe payment on 21 Aug that nobody confirmed shipped. |
| Hottest lead | Holden Beach Marina (see §2). Waiting on her quantity. |
| Outreach | 3 regional reps send 6 cold emails each, M/W/F (18 a run). The reply desk drafts every buyer reply for Garrett's approval. |
| Content | Daily Facebook Page photo, Pinterest 5 pins M/W/F (115 pins live after today), occasional reels. |

## 2. Open threads, in priority order

1. **Holden Beach Marina, Ashley Portis Dyer (office manager), Supply NC.** This is the bulk deal.
   - She has the free sample pair, delivered to the front desk 19 Oct. She said: "The material and print is nice."
   - **Fit question:** most boats there are under 26 ft and use the next size down fender. She was testing fit on those. Garrett told her it's the only size for now, and that a different size would need an order of a few hundred.
   - She asked for cost and retail. On **20 Oct** Garrett sent wholesale terms and asked how many pairs to start with. Those are the only approved wholesale terms, and they apply to her alone.
   - **Ball is in her court**, with no reply since 20 Oct (confirmed by the reply desk this morning).
   - A follow-up drafted on 21 Oct (a dozen sets, or a consignment option) was **never approved or sent**. Consignment is not an approved offer.
2. **Today's 12 new cold emails** (Gulf Coast 6, Florida 6), plus the Southwest rep's run, which was still running at the time of writing. No replies yet.
3. **Declined, do not recontact:** Bluewater Bay Marina (Niceville, 19 Oct) and Jacksonville Light Boat Parade (13 Oct).
4. **Older outreach still unanswered:** about 18 marinas emailed 19 Oct, 6 on 21 Oct, Captain's Locker 16 Oct, and Blue Water Supply and Patriot Depot on 22 Sept.
5. **The single DB order (5 Oct) and the 21 Aug Stripe $114.** Garrett should confirm whether either was a real buyer who still needs a shipment.
6. **Draft PR #1 "Commodore"** (CEO agent, 15 Oct). Garrett later said that agent is a separate business. The PR is still open and needs a close-or-keep call.
7. **Two Facebook reels (posted 17 Oct and 23 Oct) say "USPS PRIORITY MAIL WITH TRACKING" on screen.** Corrected UPS versions are built. Deleting the old ones is waiting on Garrett's "delete the two USPS reels".

## 3. Garrett's standing decisions (dated)

Newest wins. Where these conflict with the `fenderu-standing-rules` skill, **these win** (see §6, item 1).

| Date | Decision |
|---|---|
| 19 Sep | No "out the door in 48hrs", no Missouri. (Origin later banned entirely.) |
| 20 Sep | "Show me this stuff before you publish." / "Do not ever put my name on any posts." |
| 23 Sep | "It has to be able to take orders. Don't mess that up." He wants to know the second an order comes in, with full shipping info. |
| 23 Sep | Removed the "Get Yours / How to Order" section. |
| 26 Sep | Banned "made for American boats" and "printed edge to edge", removed from the site and all posts. Target patriot/MAGA lake groups. |
| 8 Oct | Giveaways are limited to one sample pair, plus $20 back for a real photo (first 20). No ambassador program, codes or multiple pairs. Economics are "between you and I". |
| 9 Oct | "Only make clean photos and reels that look real." Approved lines: "Show your patriotism." and "Make America Great Again". |
| 15–16 Oct | **"edge to edge" banned everywhere** ("it's not edge to edge"). |
| 16 Oct | **UPS only.** "Never usps." / "It's just UPS. No ground." |
| 16 Oct | "Don't say cards and PayPal in the emails." Never name payment methods in email. |
| 16 Oct | "Stop making stuff up without asking me first." |
| 16 Oct | Draft buyer replies for his approval. Nothing is sent to a buyer until he says send. |
| 16 Oct | Run reps regionally, by who is still boating this season. Each region writes in its own voice. |
| 19 Oct | One checkout button, with options at checkout. Research high-end sites before changing anything. |
| 20 Oct | Wholesale terms approved for Holden Beach only. Never offer them to anyone else. |
| 21 Oct | "Stop having them say what each marina does or where it is in the email. Get more creative." |
| 21 Oct | **"Don't say 'the pair' anywhere. Don't sound so cheesy. Sound nice, but professional."** |
| 21 Oct | "Four sets is not enough for a marina. Don't say a number if you're going to go that low." |
| standing | $119 with free shipping, the only price. FenderU Facebook Page only, never his personal profile. Write the site as `FenderU.com` in email. Only his own photos. |

## 4. On autopilot (scheduled tasks)

| Task | ID | Schedule (Central unless noted) | Last run |
|---|---|---|---|
| Gulf Coast rep, 6 emails | trig_01Cvaa3LDsiQKJxT46gFUqjz | M/W/F 9:08 | 23 Oct OK, 6 sent, links clean |
| Florida rep, 6 emails | trig_01S31KvhutyKz9TGyNJvEV4N | M/W/F 9:41 | 23 Oct OK, 6 sent, links clean |
| Desert SW & Texas rep, 6 emails | trig_01Mc7xPsa8Ks2LqFzfwZYErW | M/W/F 10:14 | 23 Oct still running at time of writing |
| Reply desk, drafts for approval | trig_01SrkuhBPr4DKmVHnsf9EHoX | daily 8:17 | 23 Oct: "No new replies" |
| Order watch | trig_01PS4C8bxWMStfDhsiSharAw | 13:13 and 23:13 UTC | 23 Oct: no orders in 24h, lifetime 1 |
| Daily Facebook photo (Make 6138535) | trig_018usLi3DXp1gHMwi6qZvBzH | daily 15:00 UTC | 23 Oct OK, posted m04-page-fit |
| Pinterest, 5 pins (Make 6229425) | trig_01RsiDJJzPciuoeXAxuYtfgn | M/W/F 14:00 UTC | 23 Oct OK, 5 pins live |
| Weekly reel (Make 6138548) | trig_01BcnYr68vXND9MAdaxa4yQD | **disabled** since 15 Oct | last 3 Oct |
| Instant order alert | Make 6374100 | on every order | must stay active |

Two other tasks on the account are not FenderU and are left alone: "Lawn watering check" and "Mark CEO daily run".

## 5. Blocked on Garrett's click (one line each)

- Stripe secret key, plus payout bank account and tax ID. Until then, cards go through PayPal.
- PayPal client ID and secret, so Venmo works through PayPal.
- Delete the Gmail filter that sends info@fenderu.com mail, and the Make order alerts, to Trash. The order watch rescues them twice a day in the meantime.
- Say "delete the two USPS reels".
- Finish TikTok Shop signup, and give Etsy OAuth consent.
- Close or keep draft PR #1 (Commodore).
- Firecrawl credits ran out on 21 Oct. The reps fall back to web search.

## 6. Five things Garrett is most likely missing

1. **The rulebook skill is stale and contradicts him.** It still lists "USPS Priority Mail" and "edge to edge" as approved, and it doesn't know about the 21 Oct ban on "the pair". Any job that loads only the skill will publish banned copy. The Pinterest job flagged this today.
2. **"The pair" (banned 21 Oct) is still everywhere.** It appears in every rep, reply-desk, Facebook and Pinterest prompt, in today's cold emails ("$119 the pair") and in live captions. (The live site was not rechecked for it in this pass.) The 21 Oct rewrite of the rep emails was drafted but never loaded into the reps.
3. **Holden Beach has gone quiet for three days, and the fit question is the real blocker.** If her boats run smaller fenders, quantity won't come until there's an answer on size. Whether to follow up, and with what, is his call.
4. **Two reps emailed personal Gmail addresses today** (Perdido Marine Supply and Hull and Hitch), which their own rules forbid. They also still describe each store and its location, which he said to stop on 21 Oct.
5. **Older Pinterest pin descriptions may still say "USPS Priority Mail".** The Pinterest job can read titles only, not descriptions, so it can't audit them. All 110 earlier titles are clean.

## 7. 30-day cash plan (proposed 23 Oct, awaiting Garrett's approval)

The stock is already paid for, so every pair sold is cash. Nothing below goes out without his "send".

**What each channel has produced so far**

| Channel | Volume | Result |
|---|---|---|
| Cold email to marina stores | about 200 sent since mid-Sept | 1 warm lead (Holden Beach), 2 declines, 1 out-of-office, 0 sales |
| Facebook Page, daily photo | daily since late Aug | 0 confirmed sales |
| Pinterest | 115 pins since 15 Sept | 0 confirmed sales |
| Grok "FenderU daily sales push" email | daily | lands in Trash unread, never used |
| FenderU.com | | 1 order row, unverified |

**What to cut**
- Most of the new-prospect cold-email volume. At 54 new emails a week, the rate is about 1 warm reply per 200. Proposal: 1 rep run a week instead of 9, with the budget moved to following up shops already emailed.
- The Grok daily push, which nobody reads. Only Garrett can turn it off; it is outside this setup.

**Three moves, in order**
1. Close Holden Beach. Send a short check-in asking whether the covers fit her smaller fenders, and how many she wants. The draft is in chat for approval.
2. One follow-up to the shops already emailed who never answered, re-offering the one free sample pair. Wording would be built only from approved lines and shown first.
3. A direct-to-buyer gift push before Christmas on the FenderU Page ("gift item" is Garrett's own framing). Organic posting has produced nothing, so this means a small paid boost of the best-performing Page post to boaters in the open-water regions. Budget is his call. Before any money is spent, check the live checkout end to end at phone width, without placing an order.
