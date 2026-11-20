// Bundles worker.js + wire-checkout.js into dist/worker.js.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
const here = new URL(".", import.meta.url);
const wire = readFileSync(new URL("wire-checkout.js", here), "utf8").replace(/<\/script/gi, "<\\/script");
const src = readFileSync(new URL("worker.js", here), "utf8").replace("__WIRE_CHECKOUT__", () => JSON.stringify(wire));
mkdirSync(new URL("dist/", here), { recursive: true });
writeFileSync(new URL("dist/worker.js", here), src);
console.log("built dist/worker.js");

// Copy guard: the corrected wording must survive every deploy. Run the built
// Worker's scrubCopy over the old lines the page files still carry and stop the
// deploy if any banned phrase gets through.
const { scrubCopy } = await import(new URL("dist/worker.js", here).href + "?t=" + Date.now());
const OLD_LINES = [
  "<li><span><strong>Elastic top</strong> — stretches over the fender and holds its shape</span></li>",
  "<li><span><strong>Elastic top</strong> &mdash; stretches over the fender and holds its shape</span></li>",
  "The elastic top stretches a bit to take up small differences, so here's exactly what we've checked",
  "<li>Waterproof &amp; salt-resistant — won't absorb water like fabric covers</li>",
  "<li>Waterproof &amp; salt-resistant — won&rsquo;t absorb water like fabric covers</li>",
  "<p>Neoprene fender covers, printed edge to edge.</p>",
  "<p>Shipped from Missouri.</p>"
].join("\n");
const out = scrubCopy(OLD_LINES);
const BANNED = [/elastic/i, /edge[\s-]to[\s-]edge/i, /like fabric covers/i, /missouri/i, /matched pair/i, /port and starboard/i, /sold as a pair/i];
const leaks = BANNED.filter((r) => r.test(out)).map(String);
const REQUIRED = ["Drawstring at both ends</strong>", "cinches snug over the fender", "Drawstrings at both ends cinch it snug, so here", "absorb water like other fabrics", "Kansas"];
const missing = REQUIRED.filter((x) => !out.includes(x));
if (leaks.length || missing.length) {
  console.error("COPY GUARD FAILED. Banned:", leaks, "Missing:", missing);
  process.exit(1);
}
console.log("copy guard: ok");
