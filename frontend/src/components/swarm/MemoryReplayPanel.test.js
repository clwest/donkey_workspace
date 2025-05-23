import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MemoryReplayPanel from "./MemoryReplayPanel";

const html = renderToStaticMarkup(<MemoryReplayPanel />);
if (!html.includes("Memory Replay")) {
  throw new Error("MemoryReplayPanel render failed");
}
console.log("MemoryReplayPanel test passed");
