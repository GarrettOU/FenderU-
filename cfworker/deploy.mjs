// Uploads dist/worker.js as the `fenderu` Worker. Keeps the static assets
// already on Cloudflare (keep_assets) and the D1 orders binding, so only the
// Worker code changes. Needs CLOUDFLARE_API_TOKEN (Workers Scripts: Edit).
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

const bindings = [
  { type: "assets", name: "ASSETS" },
  { type: "d1", name: "DB", id: D1_ID }
];

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
  bindings.push({ type: "secret_text", name: "STRIPE_SECRET_KEY", text: STRIPE_KEY });
  bindings.push({ type: "secret_text", name: "STRIPE_WEBHOOK_SECRET", text: hook.secret });
  console.log("card checkout: on (Stripe", acct.id + ")");
} else {
  console.log("card checkout: STRIPE_SECRET_KEY not set, card orders go through PayPal");
}

const metadata = {
  main_module: "worker.js",
  compatibility_date: "2025-01-01",
  bindings,
  keep_assets: true,
  // Send page requests through the Worker so it can add the checkout wiring.
  // With keep_assets, run_worker_first was accepted but not applied;
  // serve_directly:false is the older switch for the same behavior.
  assets: { config: { serve_directly: false } }
};

const form = new FormData();
form.append("metadata", new Blob([JSON.stringify(metadata)], { type: "application/json" }));
form.append("worker.js", new Blob([readFileSync(new URL("dist/worker.js", import.meta.url))], { type: "application/javascript+module" }), "worker.js");

let result;
try {
  result = await cf(`/accounts/${account}/workers/scripts/${SCRIPT}`, { method: "PUT", body: form });
} catch (e) {
  if (newWebhookId) await stripeApi("DELETE", `/v1/webhook_endpoints/${newWebhookId}`).catch(() => {});
  throw e;
}
console.log("deployed", SCRIPT, result.id || "", result.etag || "");
