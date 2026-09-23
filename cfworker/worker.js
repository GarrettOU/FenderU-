// Filled in by build.mjs from wire-checkout.js.
const WIRE_CHECKOUT = __WIRE_CHECKOUT__;

const JSON_HEADERS = { "Content-Type": "application/json" };
const PRICE_CENTS = 11900; // $119 per 2-pack, free shipping
const PRODUCT_NAME = "FenderU MAGA Fender Cover 2-Pack";
// Make scenario "FenderU - new order alert" emails each new order to Garrett.
const ORDER_ALERT_URL = "https://hook.us2.make.com/vnrslz7r1mgscxh8ff28dx32gkghy33g";

const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: JSON_HEADERS });
const clip = (v, n = 300) => typeof v === "string" ? v.trim().slice(0, n) : "";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const post = request.method === "POST";

    if (post && url.pathname === "/api/order") return p2pOrder(request, env, ctx);
    if (post && url.pathname === "/api/checkout") return cardCheckout(request, env, url);
    if (post && url.pathname === "/api/stripe-webhook") return stripeWebhook(request, env, ctx);
    if (post && url.pathname === "/api/paypal-ipn") return paypalIpn(request, env, ctx);

    // Back from Stripe (/?thanks=1&sid=cs_...): save the paid order right away,
    // in case Stripe's webhook is slow or missed.
    const sid = url.searchParams.get("sid");
    if (sid && env.STRIPE_SECRET_KEY && /^cs_[A-Za-z0-9_]+$/.test(sid)) {
      ctx.waitUntil(confirmSession(env, sid, ctx).catch(() => {}));
    }

    const res = await env.ASSETS.fetch(request);
    const type = res.headers.get("Content-Type") || "";
    if (!type.includes("text/html")) return res;

    // The deployed pages lost their onclick attributes; put the button wiring back.
    const flags = env.STRIPE_SECRET_KEY ? "window.FU_CARD_CHECKOUT=true;" : "";
    let scriptText = "";
    return new HTMLRewriter()
      // Ask PayPal to report each payment back to /api/paypal-ipn so PayPal
      // orders get saved and alerted like the others.
      .on("script", {
        text(t) {
          scriptText += t.text;
          if (!t.lastInTextNode) { t.remove(); return; }
          {
            t.replace(scriptText.replace("+'&no_note=1'",
              "+'&no_note=1&notify_url='+encodeURIComponent(window.location.origin+'/api/paypal-ipn')"), { html: true });
            scriptText = "";
          }
        }
      })
      .on("body", {
        element(el) {
          el.append(`<script>${flags}${WIRE_CHECKOUT}</script>`, { html: true });
        }
      })
      .transform(res);
  }
};

// Venmo / Cash App orders, posted by the page's own sendP2POrder().
async function p2pOrder(request, env, ctx) {
  try {
    const d = await request.json();
    const pick = (k) => clip(d[k]);
    const created = new Date().toISOString();
    const r = await env.DB.prepare(
      `INSERT INTO orders (created_at,name,email,phone,address,city,state,zip,quantity,carrier,total,payment_method)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`
    ).bind(
      created,
      pick("name"), pick("email"), pick("phone"), pick("address"), pick("city"),
      pick("state"), pick("zip"), pick("quantity"), pick("carrier"), pick("total"),
      pick("payment_method")
    ).run();
    ctx.waitUntil(alertOrder(env, {
      order_id: r.meta.last_row_id, created_at: created,
      name: pick("name"), email: pick("email"), phone: pick("phone"), address: pick("address"),
      city: pick("city"), state: pick("state"), zip: pick("zip"), quantity: pick("quantity"),
      carrier: pick("carrier"), total: pick("total"), payment_method: pick("payment_method"),
      note: `Buyer says they sent ${pick("payment_method") || "payment"}. Check it landed before shipping.`
    }));
    return json({ success: true });
  } catch (e) {
    return json({ success: false, error: String(e).slice(0, 200) }, 500);
  }
}

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

// Creates a Stripe Checkout page for the cart. Price is set here, never by the browser.
async function cardCheckout(request, env, url) {
  if (!env.STRIPE_SECRET_KEY) return json({ error: "card checkout not configured" }, 503);
  try {
    const d = await request.json();
    const qty = Math.min(20, Math.max(1, parseInt(d.qty, 10) || 1));
    const f = {
      first: clip(d.first, 100), last: clip(d.last, 100), email: clip(d.email, 200),
      phone: clip(d.phone, 40), addr1: clip(d.addr1, 200), addr2: clip(d.addr2, 200),
      city: clip(d.city, 100), state: clip(d.state, 2).toUpperCase(), zip: clip(d.zip, 10),
      carrier: d.carrier === "ups" ? "UPS Ground" : "USPS Priority"
    };
    if (!f.first || !f.last || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.email) || !f.addr1 ||
        !f.city || !/^[A-Z]{2}$/.test(f.state) || !/^\d{5}(-\d{4})?$/.test(f.zip)) {
      return json({ error: "missing shipping details" }, 400);
    }
    const name = `${f.first} ${f.last}`;
    const address = f.addr1 + (f.addr2 ? `, ${f.addr2}` : "");
    const origin = url.origin;
    const params = {
      mode: "payment",
      "line_items[0][price_data][currency]": "usd",
      "line_items[0][price_data][unit_amount]": String(PRICE_CENTS),
      "line_items[0][price_data][product_data][name]": PRODUCT_NAME,
      "line_items[0][quantity]": String(qty),
      customer_email: f.email,
      success_url: `${origin}/?thanks=1&q=${qty}&sid={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/`,
      "payment_intent_data[description]": `${PRODUCT_NAME} x ${qty} - ${f.carrier}`,
      "payment_intent_data[shipping][name]": name,
      "payment_intent_data[shipping][phone]": f.phone,
      "payment_intent_data[shipping][address][line1]": f.addr1,
      "payment_intent_data[shipping][address][line2]": f.addr2,
      "payment_intent_data[shipping][address][city]": f.city,
      "payment_intent_data[shipping][address][state]": f.state,
      "payment_intent_data[shipping][address][postal_code]": f.zip,
      "payment_intent_data[shipping][address][country]": "US",
      "metadata[name]": name,
      "metadata[email]": f.email,
      "metadata[phone]": f.phone,
      "metadata[address]": address,
      "metadata[city]": f.city,
      "metadata[state]": f.state,
      "metadata[zip]": f.zip,
      "metadata[quantity]": `${qty} x 2-pack`,
      "metadata[carrier]": f.carrier
    };
    const session = await stripe(env, "POST", "/v1/checkout/sessions", params);
    return json({ url: session.url });
  } catch (e) {
    return json({ error: String(e.message || e).slice(0, 200) }, 502);
  }
}

// Saves a paid Stripe order once (unique on ref), then emails Garrett.
async function recordStripeOrder(env, s, ctx) {
  if (!s || s.payment_status !== "paid") return false;
  const m = s.metadata || {};
  const o = {
    created_at: new Date().toISOString(),
    name: clip(m.name), email: clip(m.email || s.customer_email), phone: clip(m.phone),
    address: clip(m.address), city: clip(m.city), state: clip(m.state), zip: clip(m.zip),
    quantity: clip(m.quantity), carrier: clip(m.carrier),
    total: "$" + ((s.amount_total || 0) / 100).toFixed(2), payment_method: "Card (Stripe)"
  };
  const r = await env.DB.prepare(
    `INSERT OR IGNORE INTO orders (created_at,name,email,phone,address,city,state,zip,quantity,carrier,total,payment_method,ref)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`
  ).bind(
    o.created_at, o.name, o.email, o.phone, o.address, o.city, o.state, o.zip,
    o.quantity, o.carrier, o.total, o.payment_method, s.id
  ).run();
  if (r.meta.changes > 0) {
    const alert = alertOrder(env, { ...o, order_id: r.meta.last_row_id, note: `Paid in full by card. Stripe ${s.id}` });
    if (ctx) ctx.waitUntil(alert); else await alert;
  }
  return true;
}

async function alertOrder(env, order) {
  try {
    await fetch(env.ORDER_ALERT_URL || ORDER_ALERT_URL, {
      method: "POST", headers: JSON_HEADERS, body: JSON.stringify(order)
    });
  } catch (e) {}
}

async function confirmSession(env, sid, ctx) {
  const s = await stripe(env, "GET", `/v1/checkout/sessions/${sid}`);
  return recordStripeOrder(env, s, ctx);
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
  const parts = Object.fromEntries(header.split(",").map((p) => p.split("=")).filter((p) => p.length === 2));
  const t = parseInt(parts.t, 10);
  const sigs = header.split(",").filter((p) => p.startsWith("v1=")).map((p) => p.slice(3));
  if (!t || !sigs.length || Math.abs(Date.now() / 1000 - t) > 300) return json({ error: "bad signature" }, 400);
  const expected = await hmacHex(env.STRIPE_WEBHOOK_SECRET, `${t}.${raw}`);
  if (!sigs.includes(expected)) return json({ error: "bad signature" }, 400);

  const event = JSON.parse(raw);
  if (event.type === "checkout.session.completed" || event.type === "checkout.session.async_payment_succeeded") {
    await recordStripeOrder(env, event.data.object, ctx);
  }
  return json({ received: true });
}

// PayPal Instant Payment Notification for the page's PayPal / card checkout.
const PAYPAL_RECEIVER = "garrettfrench1979@gmail.com";
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
    if (f.get("payment_status") !== "Completed" || receiver !== PAYPAL_RECEIVER || f.get("mc_currency") !== "USD") {
      return new Response("", { status: 200 });
    }
    const txn = clip(f.get("txn_id"), 64);
    const packs = (clip(f.get("item_name")).match(/Qty (\d+)/) || [])[1] || f.get("quantity") || "1";
    const street = clip(f.get("address_street"));
    const o = {
      created_at: new Date().toISOString(),
      name: clip(f.get("address_name")) || `${clip(f.get("first_name"))} ${clip(f.get("last_name"))}`.trim(),
      email: clip(f.get("payer_email")), phone: clip(f.get("contact_phone")),
      address: street.replace(/\r?\n/g, ", "), city: clip(f.get("address_city")),
      state: clip(f.get("address_state")), zip: clip(f.get("address_zip")),
      quantity: `${packs} x 2-pack`,
      carrier: /UPS Ground/.test(f.get("item_name") || "") ? "UPS Ground" : "USPS Priority",
      total: "$" + Number(f.get("mc_gross") || 0).toFixed(2), payment_method: "PayPal"
    };
    const r = await env.DB.prepare(
      `INSERT OR IGNORE INTO orders (created_at,name,email,phone,address,city,state,zip,quantity,carrier,total,payment_method,ref)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`
    ).bind(o.created_at, o.name, o.email, o.phone, o.address, o.city, o.state, o.zip,
      o.quantity, o.carrier, o.total, o.payment_method, "paypal:" + txn).run();
    if (r.meta.changes > 0) {
      ctx.waitUntil(alertOrder(env, { ...o, order_id: r.meta.last_row_id, note: `Paid in full through PayPal. Transaction ${txn}` }));
    }
  } catch (e) {}
  return new Response("", { status: 200 });
}
