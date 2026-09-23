// Bundles worker.js + wire-checkout.js into dist/worker.js.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
const here = new URL(".", import.meta.url);
const wire = readFileSync(new URL("wire-checkout.js", here), "utf8").replace(/<\/script/gi, "<\\/script");
const src = readFileSync(new URL("worker.js", here), "utf8").replace("__WIRE_CHECKOUT__", () => JSON.stringify(wire));
mkdirSync(new URL("dist/", here), { recursive: true });
writeFileSync(new URL("dist/worker.js", here), src);
console.log("built dist/worker.js");
