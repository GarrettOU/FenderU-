// fenderu-front: serves fenderu.com. Pages and files come from the `fenderu`
// Worker over the ASSETS service binding; this code owns /api/* and adds the
// checkout wiring to every page.
//
// Payment at checkout (one Place Order button, the method is chosen above it):
//   Card   -> Stripe Checkout when STRIPE_SECRET_KEY is set (cards, Apple Pay,
//             Google Pay and whatever else is switched on in the Stripe
//             dashboard); otherwise PayPal's hosted page, which takes cards
//             without a PayPal account.
//   PayPal -> PayPal's hosted page; the sale comes back through the IPN.
//   Venmo  -> PayPal's Venmo button, shown only when PAYPAL_CLIENT_ID and
//             PAYPAL_SECRET are set. Stripe has no Venmo for US businesses,
//             and PayPal's hosted page doesn't offer it, so this is the only
//             verified way to take Venmo.
// An order is only ever recorded from a verified payment.

// Filled in by build.mjs from wire-checkout.js.
const WIRE_CHECKOUT = __WIRE_CHECKOUT__;

const JSON_HEADERS = { "Content-Type": "application/json" };
const PRICE_CENTS = 11900; // $119 per 2-pack, free shipping
const PRODUCT_NAME = "FenderU MAGA Fender Cover 2-Pack";
const CARRIER = "UPS";
const PAYPAL_RECEIVER = "garrettfrench1979@gmail.com";
// Make scenario "FenderU - new order alert" emails each new order to Garrett.
const ORDER_ALERT_URL = "https://hook.us2.make.com/vnrslz7r1mgscxh8ff28dx32gkghy33g";

// Reels built in marketing/reels after the site's files were frozen, served
// from the repo at a pinned commit so Facebook gets a real video/mp4 URL.
const REELS = {
  "/media/fb/reel-d-make-america-great-again.mp4":
    "https://raw.githubusercontent.com/GarrettOU/FenderU-/9c0a5e0/marketing/reels/maga-on-the-water.mp4"
};

const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: JSON_HEADERS });
const clip = (v, n = 300) => typeof v === "string" ? v.trim().slice(0, n) : "";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const post = request.method === "POST";

    if (url.pathname === "/api/order") {
      return json({ error: "This endpoint is closed. Orders are only recorded from a verified payment." }, 410);
    }
    if (post && url.pathname === "/api/checkout") return cardCheckout(request, env, url);
    if (post && url.pathname === "/api/stripe-webhook") return stripeWebhook(request, env, ctx);
    if (post && url.pathname === "/api/paypal-ipn") return paypalIpn(request, env, ctx);
    if (post && url.pathname === "/api/paypal/order") return paypalCreateOrder(request, env);
    if (post && url.pathname === "/api/paypal/capture") return paypalCapture(request, env, ctx);
    if (REELS[url.pathname]) return serveReel(request, REELS[url.pathname]);

    // Back from Stripe (/?thanks=1&sid=cs_...): save the paid order right away,
    // in case Stripe's webhook is slow or missed.
    const sid = url.searchParams.get("sid");
    if (sid && env.STRIPE_SECRET_KEY && /^cs_[A-Za-z0-9_]+$/.test(sid)) {
      ctx.waitUntil(confirmSession(env, sid, ctx).catch(() => {}));
    }

    const raw = await env.ASSETS.fetch(request);
    const type = raw.headers.get("Content-Type") || "";
    if (!type.includes("text/html")) return raw;
    const headers = new Headers(raw.headers);
    headers.delete("content-length");
    let html = scrubCopy(await raw.text());
    // PayPal Standard takes the merchant ID in place of the account email, so
    // the page source doesn't carry Garrett's address.
    if (env.PAYPAL_MERCHANT_ID) html = html.split("business=garrettfrench1979%40gmail.com").join("business=" + encodeURIComponent(env.PAYPAL_MERCHANT_ID));
    const res = new Response(html, { status: raw.status, statusText: raw.statusText, headers });

    const flags = (env.STRIPE_SECRET_KEY ? "window.FU_CARD_CHECKOUT=true;" : "") +
      (env.PAYPAL_CLIENT_ID && env.PAYPAL_SECRET ? `window.FU_PAYPAL_CLIENT_ID=${JSON.stringify(env.PAYPAL_CLIENT_ID)};` : "");
    return new HTMLRewriter()
      .on("body", {
        element(el) {
          el.append(`<script>${flags}${WIRE_CHECKOUT}</script>`, { html: true });
        }
      })
      .transform(res);
  }
};

// Garrett banned "edge to edge" and "Made for American Boats" everywhere.
// The page source is clean now; this stays as a backstop.
function scrubCopy(html) {
  return html
    .replace(/,?\s*(printed\s+)?edge[\s-]to[\s-]edge/gi, "")
    .replace(/made for american boats\.?\s*/gi, "")
    .replace(/([^.])\.\.(?=\s)/g, "$1.")
    // Hidden Netlify order form left over from the old host; nothing posts to it.
    .replace(/<form name="fenderu-order"[^>]*data-netlify[^>]*>[\s\S]*?<\/form>\s*/i, "");
}

async function serveReel(request, src) {
  const range = request.headers.get("Range");
  const r = await fetch(src, { method: request.method === "HEAD" ? "HEAD" : "GET", headers: range ? { Range: range } : {} });
  const headers = new Headers({ "Content-Type": "video/mp4", "Accept-Ranges": "bytes", "Cache-Control": "public, max-age=86400" });
  for (const h of ["Content-Length", "Content-Range"]) if (r.headers.get(h)) headers.set(h, r.headers.get(h));
  return new Response(r.body, { status: r.status, headers });
}

// Shipping details from the checkout form; null if anything required is missing.
function shipTo(d) {
  const f = {
    first: clip(d.first, 100), last: clip(d.last, 100), email: clip(d.email, 200), phone: clip(d.phone, 40),
    addr1: clip(d.addr1, 200), addr2: clip(d.addr2, 200), city: clip(d.city, 100),
    state: clip(d.state, 2).toUpperCase(), zip: clip(d.zip, 10)
  };
  if (!f.first || !f.last || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.email) || !f.addr1 || !f.city ||
      !/^[A-Z]{2}$/.test(f.state) || !/^\d{5}(-\d{4})?$/.test(f.zip)) return null;
  f.name = `${f.first} ${f.last}`;
  f.address = f.addr1 + (f.addr2 ? `, ${f.addr2}` : "");
  return f;
}
const quantity = (v) => Math.min(20, Math.max(1, parseInt(v, 10) || 1));

async function saveOrder(env, ctx, o, ref, note) {
  const r = await env.DB.prepare(
    `INSERT OR IGNORE INTO orders (created_at,name,email,phone,address,city,state,zip,quantity,carrier,total,payment_method,ref)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`
  ).bind(o.created_at, o.name, o.email, o.phone, o.address, o.city, o.state, o.zip,
    o.quantity, o.carrier, o.total, o.payment_method, ref).run();
  if (r.meta.changes > 0) {
    const alert = alertOrder(env, { ...o, order_id: r.meta.last_row_id, note });
    if (ctx) ctx.waitUntil(alert); else await alert;
  }
}

async function alertOrder(env, order) {
  try {
    const r = await fetch(env.ORDER_ALERT_URL || ORDER_ALERT_URL, {
      method: "POST", headers: JSON_HEADERS, body: JSON.stringify(order)
    });
    if (!r.ok || !order.order_id) return;
    await env.DB.prepare("UPDATE orders SET notified = 1 WHERE id = ?").bind(order.order_id).run();
  } catch (e) {}
}

// ---------- Stripe (cards, Apple Pay, Google Pay) ----------

async function stripe(env, method, path, params) {
  const base = env.STRIPE_API_BASE || "https://api.stripe.com";
  const res = await fetch(base + path, {
    method,
    headers: {
      Authorization: `Bearer ${env.STRIPE_SECRET_KEY}`,
      ...(params ? { "Content-Type": "application/x-www-form-urlencoded" } : {})
    },
    body: params ? new URLSearchParams(params).toString() : undefined
  });
  const body = await res.json();
  if (!res.ok) throw new Error(body?.error?.message || `Stripe ${res.status}`);
  return body;
}

async function cardCheckout(request, env, url) {
  if (!env.STRIPE_SECRET_KEY) return json({ error: "card checkout not configured" }, 503);
  try {
    const d = await request.json();
    const qty = quantity(d.qty);
    const f = shipTo(d);
    if (!f) return json({ error: "missing shipping details" }, 400);
    // No payment_method_types: Checkout shows every method switched on in the
    // Stripe dashboard (cards, Apple Pay, Google Pay, Link, ...). A delayed
    // method such as a bank debit is only recorded once it settles
    // (checkout.session.async_payment_succeeded), never on "unpaid".
    const params = {
      mode: "payment",
      "line_items[0][price_data][currency]": "usd",
      "line_items[0][price_data][unit_amount]": String(PRICE_CENTS),
      "line_items[0][price_data][product_data][name]": PRODUCT_NAME,
      "line_items[0][quantity]": String(qty),
      customer_email: f.email,
      success_url: `${url.origin}/?thanks=1&q=${qty}&sid={CHECKOUT_SESSION_ID}`,
      cancel_url: `${url.origin}/`,
      "payment_intent_data[description]": `${PRODUCT_NAME} x ${qty} - ${CARRIER}`,
      "payment_intent_data[shipping][name]": f.name,
      "payment_intent_data[shipping][phone]": f.phone,
      "payment_intent_data[shipping][address][line1]": f.addr1,
      "payment_intent_data[shipping][address][line2]": f.addr2,
      "payment_intent_data[shipping][address][city]": f.city,
      "payment_intent_data[shipping][address][state]": f.state,
      "payment_intent_data[shipping][address][postal_code]": f.zip,
      "payment_intent_data[shipping][address][country]": "US",
      "metadata[name]": f.name, "metadata[email]": f.email, "metadata[phone]": f.phone,
      "metadata[address]": f.address, "metadata[city]": f.city, "metadata[state]": f.state,
      "metadata[zip]": f.zip, "metadata[quantity]": `${qty} x 2-pack`, "metadata[carrier]": CARRIER
    };
    const session = await stripe(env, "POST", "/v1/checkout/sessions", params);
    return json({ url: session.url });
  } catch (e) {
    return json({ error: String(e.message || e).slice(0, 200) }, 502);
  }
}

function stripeOrder(s, method) {
  const m = s.metadata || {};
  return {
    created_at: new Date().toISOString(),
    name: clip(m.name), email: clip(m.email || s.customer_email), phone: clip(m.phone),
    address: clip(m.address), city: clip(m.city), state: clip(m.state), zip: clip(m.zip),
    quantity: clip(m.quantity), carrier: clip(m.carrier),
    total: "$" + ((s.amount_total || 0) / 100).toFixed(2), payment_method: method
  };
}

async function recordStripeOrder(env, s, ctx) {
  if (!s || s.payment_status !== "paid") return false;
  await saveOrder(env, ctx, stripeOrder(s, "Card (Stripe)"), s.id, `Paid in full through Stripe. ${s.id}`);
  return true;
}

async function confirmSession(env, sid, ctx) {
  return recordStripeOrder(env, await stripe(env, "GET", `/v1/checkout/sessions/${sid}`), ctx);
}

async function hmacHex(secret, text) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(text));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function stripeWebhook(request, env, ctx) {
  if (!env.STRIPE_WEBHOOK_SECRET) return json({ error: "not configured" }, 503);
  const raw = await request.text();
  const header = request.headers.get("Stripe-Signature") || "";
  const t = parseInt((header.match(/(?:^|,)t=(\d+)/) || [])[1], 10);
  const sigs = header.split(",").filter((p) => p.startsWith("v1=")).map((p) => p.slice(3));
  if (!t || !sigs.length || Math.abs(Date.now() / 1000 - t) > 300) return json({ error: "bad signature" }, 400);
  if (!sigs.includes(await hmacHex(env.STRIPE_WEBHOOK_SECRET, `${t}.${raw}`))) return json({ error: "bad signature" }, 400);
  const event = JSON.parse(raw);
  const s = event.data?.object;
  if (event.type === "checkout.session.completed" || event.type === "checkout.session.async_payment_succeeded") {
    await recordStripeOrder(env, s, ctx);
  } else if (event.type === "checkout.session.async_payment_failed") {
    ctx.waitUntil(alertOrder(env, {
      ...stripeOrder(s || {}, "Bank payment FAILED"),
      note: "A delayed (bank) payment did not clear. No order was recorded. Do not ship."
    }));
  }
  return json({ received: true });
}

// ---------- PayPal hosted page (PayPal, and cards when Stripe is off) ----------

async function paypalIpn(request, env, ctx) {
  const raw = await request.text();
  try {
    const verify = await fetch(env.PAYPAL_IPN_VERIFY_URL || "https://ipnpb.paypal.com/cgi-bin/webscr", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "fenderu-ipn" },
      body: "cmd=_notify-validate&" + raw
    });
    if ((await verify.text()).trim() !== "VERIFIED") return new Response("", { status: 200 });
    const f = new URLSearchParams(raw);
    const receiver = (f.get("receiver_email") || f.get("business") || "").toLowerCase();
    const ours = receiver === PAYPAL_RECEIVER || (env.PAYPAL_MERCHANT_ID && f.get("receiver_id") === env.PAYPAL_MERCHANT_ID);
    if (f.get("payment_status") !== "Completed" || !ours || f.get("mc_currency") !== "USD") {
      return new Response("", { status: 200 });
    }
    const txn = clip(f.get("txn_id"), 64);
    const packs = (clip(f.get("item_name")).match(/Qty (\d+)/) || [])[1] || f.get("quantity") || "1";
    await saveOrder(env, ctx, {
      created_at: new Date().toISOString(),
      name: clip(f.get("address_name")) || `${clip(f.get("first_name"))} ${clip(f.get("last_name"))}`.trim(),
      email: clip(f.get("payer_email")), phone: clip(f.get("contact_phone")),
      address: clip(f.get("address_street")).replace(/\r?\n/g, ", "),
      city: clip(f.get("address_city")), state: clip(f.get("address_state")), zip: clip(f.get("address_zip")),
      quantity: `${packs} x 2-pack`, carrier: CARRIER,
      total: "$" + Number(f.get("mc_gross") || 0).toFixed(2), payment_method: "PayPal"
    }, "paypal:" + txn, `Paid in full through PayPal. Transaction ${txn}`);
  } catch (e) {}
  return new Response("", { status: 200 });
}

// ---------- PayPal Orders API (Venmo button) ----------

async function paypalApi(env, method, path, body) {
  const base = env.PAYPAL_API_BASE || "https://api-m.paypal.com";
  const tok = await fetch(base + "/v1/oauth2/token", {
    method: "POST",
    headers: {
      Authorization: "Basic " + btoa(`${env.PAYPAL_CLIENT_ID}:${env.PAYPAL_SECRET}`),
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: "grant_type=client_credentials"
  }).then((r) => r.json());
  if (!tok.access_token) throw new Error("PayPal sign-in failed");
  const r = await fetch(base + path, {
    method,
    headers: { Authorization: `Bearer ${tok.access_token}`, "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined
  });
  const j = await r.json();
  if (!r.ok) throw new Error(j?.details?.[0]?.description || j?.message || `PayPal ${r.status}`);
  return j;
}

async function paypalCreateOrder(request, env) {
  if (!env.PAYPAL_CLIENT_ID || !env.PAYPAL_SECRET) return json({ error: "PayPal API not configured" }, 503);
  try {
    const d = await request.json();
    const qty = quantity(d.qty);
    const f = shipTo(d);
    if (!f) return json({ error: "missing shipping details" }, 400);
    const total = ((PRICE_CENTS * qty) / 100).toFixed(2);
    const meta = { n: f.name, e: f.email, p: f.phone, q: qty };
    const order = await paypalApi(env, "POST", "/v2/checkout/orders", {
      intent: "CAPTURE",
      purchase_units: [{
        description: `${PRODUCT_NAME} x ${qty}`,
        custom_id: JSON.stringify(meta).slice(0, 127),
        amount: {
          currency_code: "USD", value: total,
          breakdown: { item_total: { currency_code: "USD", value: total } }
        },
        items: [{ name: PRODUCT_NAME, quantity: String(qty), unit_amount: { currency_code: "USD", value: (PRICE_CENTS / 100).toFixed(2) } }],
        shipping: {
          name: { full_name: f.name },
          address: {
            address_line_1: f.addr1, address_line_2: f.addr2 || undefined, admin_area_2: f.city,
            admin_area_1: f.state, postal_code: f.zip, country_code: "US"
          }
        }
      }],
      application_context: { shipping_preference: "SET_PROVIDED_ADDRESS", brand_name: "FenderU", user_action: "PAY_NOW" }
    });
    return json({ id: order.id });
  } catch (e) {
    return json({ error: String(e.message || e).slice(0, 200) }, 502);
  }
}

async function paypalCapture(request, env, ctx) {
  if (!env.PAYPAL_CLIENT_ID || !env.PAYPAL_SECRET) return json({ error: "PayPal API not configured" }, 503);
  try {
    const { id } = await request.json();
    if (!/^[A-Z0-9]{10,40}$/.test(String(id))) return json({ error: "bad order id" }, 400);
    const o = await paypalApi(env, "POST", `/v2/checkout/orders/${id}/capture`, {});
    const unit = o.purchase_units?.[0] || {};
    const cap = unit.payments?.captures?.[0];
    if (o.status !== "COMPLETED" || !cap || cap.status !== "COMPLETED") return json({ error: "payment not completed" }, 402);
    let meta = {};
    try { meta = JSON.parse(unit.custom_id || "{}"); } catch (e) {}
    const a = unit.shipping?.address || {};
    const method = o.payment_source?.venmo ? "Venmo" : o.payment_source?.card ? "Card (PayPal)" : "PayPal";
    await saveOrder(env, ctx, {
      created_at: new Date().toISOString(),
      name: clip(meta.n) || clip(unit.shipping?.name?.full_name), email: clip(meta.e), phone: clip(meta.p),
      address: [a.address_line_1, a.address_line_2].filter(Boolean).join(", "),
      city: clip(a.admin_area_2), state: clip(a.admin_area_1), zip: clip(a.postal_code),
      quantity: `${quantity(meta.q)} x 2-pack`, carrier: CARRIER,
      total: "$" + Number(cap.amount?.value || 0).toFixed(2), payment_method: method
    }, "ppo:" + cap.id, `Paid in full through ${method}. Capture ${cap.id}`);
    return json({ ok: true });
  } catch (e) {
    return json({ error: String(e.message || e).slice(0, 200) }, 502);
  }
}
