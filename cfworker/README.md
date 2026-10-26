# fenderu-front Worker

Serves fenderu.com and takes orders. Pages and files come from the `fenderu`
Worker over a service binding; this Worker owns `/api/*` and adds
`wire-checkout.js` to every page.

## Checkout

One Place Order button. The buyer picks how to pay in the Payment step, above
the button; credit card is preselected and the button's label says where it
goes next ("Continue to Payment" / "Continue to PayPal").

| Choice | Goes to | Needs |
|---|---|---|
| Credit or debit card | Stripe Checkout: cards, Apple Pay, Google Pay, Cash App Pay, plus anything switched on in the Stripe dashboard | `STRIPE_SECRET_KEY`. Without it: PayPal's card button (REST keys) or, with no keys at all, PayPal's hosted page |
| PayPal | PayPal's own button (REST keys), else PayPal's hosted page | nothing; better with `PAYPAL_CLIENT_ID` + `PAYPAL_SECRET` |
| Venmo | PayPal's Venmo button, drawn in the Place Order button's spot | `PAYPAL_CLIENT_ID` + `PAYPAL_SECRET` (live REST app). The option only shows for buyers PayPal says can use Venmo |

With the PayPal REST keys set, every PayPal, Venmo and (Stripe off) card
payment is created and captured through `/api/paypal/*` and recorded the
moment it completes. The old PayPal Standard link (`webscr`) is only used when
there are no keys at all. `PAYPAL_MERCHANT_ID` (optional) replaces the account
email in that link so the page source doesn't carry it.

Stripe has no PayPal or Venmo for US businesses (PayPal on Stripe is EU/UK
only), so PayPal and Venmo go through PayPal itself.

## What Garrett has to do (about 10 minutes)

Both are added as repository secrets: GitHub → the FenderU- repo → Settings →
Secrets and variables → Actions → New repository secret. Then run the
"Deploy fenderu Worker" action (Actions tab → Deploy fenderu Worker → Run
workflow). The deploy checks each key against Stripe / PayPal live before it
turns anything on.

**Stripe (cards, Apple Pay, Google Pay, Cash App Pay)**
1. dashboard.stripe.com → sign in to the FenderU account (acct_1TbxBGQ7zed58VML).
2. Top right: make sure "Test mode" is OFF.
3. Developers → API keys → Secret key → Reveal live key → copy (starts `sk_live_`).
4. GitHub secret `STRIPE_SECRET_KEY` = that key.
5. Optional, recommended: Settings → Payments → Payment methods → turn on Apple Pay, Google Pay, Cash App Pay, Link. Checkout shows whatever is on.

**PayPal REST (PayPal + Venmo, and cards when Stripe is off)**
1. developer.paypal.com → Log in with the FenderU PayPal **Business** account (a personal account can't take Venmo; upgrade it in PayPal first if needed).
2. Apps & Credentials → switch the toggle from Sandbox to **Live**.
3. Create App → name "FenderU site" → Create App.
4. Copy **Client ID** and **Secret key** (Show).
5. GitHub secrets `PAYPAL_CLIENT_ID` and `PAYPAL_SECRET`.

**Merchant ID (optional, 1 minute)**: paypal.com → Settings (gear) → Account
settings → Business information → "PayPal Merchant ID" → GitHub secret
`PAYPAL_MERCHANT_ID`.

An order is saved only from a verified payment: Stripe (webhook, and again
when the buyer returns to `/?thanks=1&sid=...`), PayPal IPN
(`/api/paypal-ipn`), or a completed PayPal capture (`/api/paypal/capture`).
`/api/order` is closed (410): it took unverified Venmo/Cash App claims.

Every new order is posted to the Make scenario "FenderU - new order alert",
which emails the full ship-to details. Orders live in D1 `fenderu-orders`,
table `orders`; `ref` (unique) holds the Stripe session, `paypal:<txn>` or
`ppo:<capture>` so no order is saved twice.

## Deploy

Push to `claude/bold-edison-3ylos0` or run the "Deploy fenderu Worker" action.
Repo secrets: `CLOUDFLARE_API_TOKEN` (required), `STRIPE_SECRET_KEY` (turns on
Stripe cards; must be the FenderU account), `PAYPAL_CLIENT_ID` and
`PAYPAL_SECRET` (turn on Venmo; checked against PayPal live before use).

Only `fenderu-front` is uploaded. The `fenderu` Worker's code and the site's
files are never touched. Secrets already set on `fenderu-front` are kept.
