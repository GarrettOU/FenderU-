// Read-only: prints how fenderu.com is attached to Workers and the fenderu
// Worker's current settings. Changes nothing.
const TOKEN = process.env.CLOUDFLARE_API_TOKEN;
if (!TOKEN) { console.log("no CLOUDFLARE_API_TOKEN"); process.exit(0); }
const API = "https://api.cloudflare.com/client/v4";
const get = async (path) => {
  const r = await fetch(API + path, { headers: { Authorization: `Bearer ${TOKEN}` } });
  const j = await r.json().catch(() => ({}));
  return j.success ? j.result : { error: j.errors || r.status };
};
const show = (label, v) => console.log(`\n== ${label}\n` + JSON.stringify(v, null, 1).slice(0, 3000));

const accounts = await get("/accounts");
const account = process.env.CLOUDFLARE_ACCOUNT_ID || accounts?.[0]?.id;
show("account", account);
show("custom domains", await get(`/accounts/${account}/workers/domains`));
const zones = await get("/zones?name=fenderu.com");
show("zone", Array.isArray(zones) ? zones.map((z) => ({ id: z.id, name: z.name })) : zones);
if (Array.isArray(zones) && zones[0]) show("zone routes", await get(`/zones/${zones[0].id}/workers/routes`));
show("script settings", await get(`/accounts/${account}/workers/scripts/fenderu/settings`));
const versions = await get(`/accounts/${account}/workers/scripts/fenderu/versions`);
show("versions", versions);
const latest = versions?.items?.[0]?.id;
if (latest) show("latest version detail", await get(`/accounts/${account}/workers/scripts/fenderu/versions/${latest}`));
