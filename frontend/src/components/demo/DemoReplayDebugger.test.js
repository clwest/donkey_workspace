import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import DemoReplayDebugger from "./DemoReplayDebugger";

const html = renderToStaticMarkup(
  <DemoReplayDebugger slug="a" sessionId="s" />
);
if (!html.includes("Demo Replay Debugger")) {
  throw new Error("DemoReplayDebugger render failed");
}
console.log("DemoReplayDebugger test passed");
