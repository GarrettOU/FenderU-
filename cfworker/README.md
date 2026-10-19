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
| Credit or debit card | Stripe Checkout: cards, Apple Pay, Google Pay, plus anything switched on in the Stripe dashboard | `STRIPE_SECRET_KEY`. Without it, cards go through PayPal's hosted page (no PayPal account needed) |
| PayPal | PayPal's hosted page | nothing |
| Venmo | PayPal's Venmo button, drawn in the Place Order button's spot | `PAYPAL_CLIENT_ID` + `PAYPAL_SECRET` (live REST app). The option only shows for buyers PayPal says can use Venmo |

Stripe has no PayPal or Venmo for US businesses (PayPal on Stripe is EU/UK
only), so PayPal and Venmo go through PayPal itself.

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
