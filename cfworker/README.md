# fenderu Worker

Serves fenderu.com and takes orders.

- **Buttons.** The deployed `index.html` lost its `onclick`/`onchange`
  attributes. The Worker adds `wire-checkout.js` to each page, which binds the
  buttons to the checkout code already on the page. Copy and design unchanged.
- **Card (Stripe).** With `STRIPE_SECRET_KEY` set, "Credit or Debit Card" opens
  a Stripe Checkout page. Price ($119 per 2-pack, free shipping) is set by the
  Worker. The order is saved only after Stripe reports it paid (webhook, and
  again when the buyer returns to `/?thanks=1&sid=...`). If Stripe fails, the
  button falls back to the PayPal card checkout. Without a key, cards go
  through PayPal as before.
- **PayPal.** The PayPal link now carries `notify_url=/api/paypal-ipn`. Verified,
  completed payments to garrettfrench1979@gmail.com are saved.
- **Venmo / Cash App.** `/api/order`, unchanged.
- **Order alerts.** Every new saved order is posted to the Make scenario
  "FenderU - new order alert", which emails the full ship-to details.
- Orders live in D1 `fenderu-orders`, table `orders`. `ref` (unique) holds the
  Stripe session or `paypal:<txn>` so no order is saved twice.

Deploy: push to `main` or run the "Deploy fenderu Worker" action. Needs repo
secrets `CLOUDFLARE_API_TOKEN` and, for Stripe cards, `STRIPE_SECRET_KEY`.
`deploy.mjs` refuses a Stripe key that is not the FenderU account.
Only Worker code is uploaded; existing images and pages stay as they are.
