// Uploads dist/worker.js twice:
//  - `fenderu`: the existing Worker. Keeps its static assets (keep_assets),
//    which Cloudflare serves directly, so it acts as the asset server.
//  - `fenderu-front`: same code, no assets. Its ASSETS binding is a service
//    binding to `fenderu`, so every page passes through this code and gets the
//    checkout wiring. It is checked on its workers.dev address. Moving
//    fenderu.com onto it is a separate, owner-approved step.
// The site's files are never re-uploaded.
// Needs CLOUDFLARE_API_TOKEN (Workers Scripts: Edit).
// With STRIPE_SECRET_KEY set, also turns on card checkout: checks the key is
// the FenderU Stripe account and (re)creates the paid-order webhook.
import { readFileSync } from "node:fs";

const TOKEN = process.env.CLOUDFLARE_API_TOKEN;
if (!TOKEN) { console.error("CLOUDFLARE_API_TOKEN is not set"); process.exit(1); }
const API = "https://api.cloudflare.com/client/v4";
const SCRIPT = "fenderu";
const D1_ID = "0487edf4-30e2-40ca-a3a8-a89c3de1d48c";
const auth = { Authorization: `Bearer ${TOKEN}` };

async function cf(path, init = {}) {
  const r = await fetch(API + path, { ...init, headers: { ...auth, ...(init.headers || {}) } });
  const j = await r.json();
  if (!j.success) throw new Error(`${path}: ${JSON.stringify(j.errors)}`);
  return j.result;
}

let account = process.env.CLOUDFLARE_ACCOUNT_ID;
if (!account) {
  const accounts = await cf("/accounts");
  if (accounts.length !== 1) throw new Error(`Set CLOUDFLARE_ACCOUNT_ID; token sees ${accounts.length} accounts`);
  account = accounts[0].id;
}

const FRONT = "fenderu-front";
const shared = [{ type: "d1", name: "DB", id: D1_ID }];

const STRIPE_KEY = process.env.STRIPE_SECRET_KEY;
const FENDERU_STRIPE_ACCOUNT = "acct_1TbxBGQ7zed58VML";
const WEBHOOK_URL = "https://fenderu.com/api/stripe-webhook";
let newWebhookId = null;

async function stripeApi(method, path, params) {
  const r = await fetch("https://api.stripe.com" + path, {
    method,
    headers: { Authorization: `Bearer ${STRIPE_KEY}`, "Content-Type": "application/x-www-form-urlencoded" },
    body: params ? new URLSearchParams(params).toString() : undefined
  });
  const j = await r.json();
  if (!r.ok) throw new Error(`Stripe ${path}: ${j?.error?.message || r.status}`);
  return j;
}

if (STRIPE_KEY) {
  const acct = await stripeApi("GET", "/v1/account");
  if (acct.id !== FENDERU_STRIPE_ACCOUNT) throw new Error(`Stripe key is for ${acct.id}, not the FenderU account`);
  if (!acct.charges_enabled) throw new Error("FenderU Stripe account cannot take charges yet");
  const hooks = await stripeApi("GET", "/v1/webhook_endpoints?limit=100");
  for (const h of hooks.data.filter((h) => h.url === WEBHOOK_URL)) {
    await stripeApi("DELETE", `/v1/webhook_endpoints/${h.id}`);
  }
  const hook = await stripeApi("POST", "/v1/webhook_endpoints", {
    url: WEBHOOK_URL,
    "enabled_events[0]": "checkout.session.completed",
    "enabled_events[1]": "checkout.session.async_payment_succeeded",
    description: "fenderu.com paid orders"
  });
  newWebhookId = hook.id;
  shared.push({ type: "secret_text", name: "STRIPE_SECRET_KEY", text: STRIPE_KEY });
  shared.push({ type: "secret_text", name: "STRIPE_WEBHOOK_SECRET", text: hook.secret });
  console.log("card checkout: on (Stripe", acct.id + ")");
} else {
  console.log("card checkout: STRIPE_SECRET_KEY not set, card orders go through PayPal");
}

const code = readFileSync(new URL("dist/worker.js", import.meta.url));
async function upload(name, extra) {
  const form = new FormData();
  form.append("metadata", new Blob([JSON.stringify({
    main_module: "worker.js", compatibility_date: "2025-01-01", ...extra
  })], { type: "application/json" }));
  form.append("worker.js", new Blob([code], { type: "application/javascript+module" }), "worker.js");
  const r = await cf(`/accounts/${account}/workers/scripts/${name}`, { method: "PUT", body: form });
  console.log("uploaded", name, r.etag || "");
}

try {
  await upload(SCRIPT, { bindings: [{ type: "assets", name: "ASSETS" }, ...shared], keep_assets: true });
  await upload(FRONT, {
    bindings: [{ type: "service", name: "ASSETS", service: SCRIPT, environment: "production" }, ...shared]
  });
} catch (e) {
  if (newWebhookId) await stripeApi("DELETE", `/v1/webhook_endpoints/${newWebhookId}`).catch(() => {});
  throw e;
}

// Check fenderu-front on its own workers.dev address.
const sub = (await cf(`/accounts/${account}/workers/subdomain`)).subdomain;
if (!sub) throw new Error("account has no workers.dev subdomain");
await cf(`/accounts/${account}/workers/scripts/${FRONT}/subdomain`, {
  method: "POST", headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ enabled: true, previews_enabled: false })
});
const preview = `https://${FRONT}.${sub}.workers.dev`;
let ok = false, why = "";
for (let i = 0; i < 12 && !ok; i++) {
  await new Promise((r) => setTimeout(r, 10000));
  try {
    const page = await fetch(`${preview}/?check=${Date.now()}`);
    const html = await page.text();
    const img = await fetch(`${preview}/og-image.jpg`);
    const vid = await fetch(`${preview}/media/fb/reel-4-made-for-american-boats.mp4`, { method: "HEAD" });
    why = `page ${page.status}, wiring ${html.includes("__fuWired")}, price ${html.includes("$119")}, ` +
      `how-to-order ${html.includes('id="how"')}, image ${img.status}, video ${vid.status}`;
    ok = page.ok && html.includes("__fuWired") && html.includes("$119") && !html.includes('id="how"') && img.ok && vid.ok;
  } catch (e) { why = String(e); }
  console.log("front check:", why);
}
console.log(`FRONT_URL=${preview}`);
if (!ok) throw new Error(`fenderu-front failed its check (${why})`);
console.log("fenderu-front passed; fenderu.com not changed");
