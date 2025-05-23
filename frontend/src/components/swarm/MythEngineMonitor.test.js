import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MythEngineMonitor from "./MythEngineMonitor";

const html = renderToStaticMarkup(<MythEngineMonitor />);
if (!html.includes("Myth Engine Instances")) {
  throw new Error("MythEngineMonitor render failed");
}
console.log("MythEngineMonitor test passed");
