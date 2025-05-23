import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MemoryRealmExplorer from "./MemoryRealmExplorer";

const html = renderToStaticMarkup(<MemoryRealmExplorer />);
if (!html.includes("Memory Realms")) {
  throw new Error("MemoryRealmExplorer render failed");
}
console.log("MemoryRealmExplorer test passed");
