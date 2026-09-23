// Uploads dist/worker.js as the `fenderu` Worker. Keeps the static assets
// already on Cloudflare (keep_assets) and the D1 orders binding, so only the
// Worker code changes. Needs CLOUDFLARE_API_TOKEN (Workers Scripts: Edit).
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

const metadata = {
  main_module: "worker.js",
  compatibility_date: "2025-01-01",
  bindings: [
    { type: "assets", name: "ASSETS" },
    { type: "d1", name: "DB", id: D1_ID }
  ],
  keep_assets: true,
  // Send page requests through the Worker so it can add the checkout wiring.
  assets: { config: { run_worker_first: true } }
};

const form = new FormData();
form.append("metadata", new Blob([JSON.stringify(metadata)], { type: "application/json" }));
form.append("worker.js", new Blob([readFileSync(new URL("dist/worker.js", import.meta.url))], { type: "application/javascript+module" }), "worker.js");

const result = await cf(`/accounts/${account}/workers/scripts/${SCRIPT}`, { method: "PUT", body: form });
console.log("deployed", SCRIPT, result.id || "", result.etag || "");
