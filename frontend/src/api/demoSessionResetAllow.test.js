import fs from "fs";
const src = fs.readFileSync(
  new URL("./assistants.js", import.meta.url),
  "utf8",
);
if (!/resetDemoSession\([\s\S]*allowUnauthenticated:\s*true/.test(src)) {
  throw new Error("resetDemoSession missing allowUnauthenticated");
}
console.log("resetDemoSession auth test passed");
