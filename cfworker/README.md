# fenderu Worker

Serves fenderu.com. `/api/order` writes Venmo/Cash App orders to the
`fenderu-orders` D1 database; every other request is passed to the static
assets already uploaded to Cloudflare.

The deployed `index.html` lost its `onclick`/`onchange` attributes, so the
Add to Cart, cart, and Place Order buttons did nothing. The Worker now adds
`wire-checkout.js` to each HTML page, which binds those buttons to the
checkout functions already on the page. No page copy or design is changed.

Deploy: `node cfworker/build.mjs && node cfworker/deploy.mjs` with
`CLOUDFLARE_API_TOKEN` set, or push to `main` (GitHub Action). Only the
Worker code is uploaded; existing images and pages stay as they are.
