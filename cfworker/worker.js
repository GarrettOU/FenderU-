// Filled in by build.mjs from wire-checkout.js.
const WIRE_CHECKOUT = __WIRE_CHECKOUT__;

var CORS = { "Content-Type": "application/json" };

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/order" && request.method === "POST") {
      try {
        const d = await request.json();
        const pick = (k) => typeof d[k] === "string" ? d[k].slice(0, 300) : "";
        await env.DB.prepare(
          `INSERT INTO orders (created_at,name,email,phone,address,city,state,zip,quantity,carrier,total,payment_method)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`
        ).bind(
          new Date().toISOString(),
          pick("name"), pick("email"), pick("phone"), pick("address"), pick("city"),
          pick("state"), pick("zip"), pick("quantity"), pick("carrier"), pick("total"),
          pick("payment_method")
        ).run();
        return new Response(JSON.stringify({ success: true }), { status: 200, headers: CORS });
      } catch (e) {
        return new Response(JSON.stringify({ success: false, error: String(e).slice(0, 200) }), { status: 500, headers: CORS });
      }
    }

    const res = await env.ASSETS.fetch(request);
    const type = res.headers.get("Content-Type") || "";
    if (!type.includes("text/html")) return res;

    // The deployed pages lost their onclick attributes; put the button wiring back.
    return new HTMLRewriter()
      .on("body", {
        element(el) {
          el.append(`<script>${WIRE_CHECKOUT}</script>`, { html: true });
        }
      })
      .transform(res);
  }
};
