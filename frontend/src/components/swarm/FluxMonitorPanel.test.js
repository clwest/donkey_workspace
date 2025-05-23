import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import FluxMonitorPanel from "./FluxMonitorPanel";

const html = renderToStaticMarkup(<FluxMonitorPanel />);
if (!html.includes("Reflective Flux Index")) {
  throw new Error("FluxMonitorPanel render failed");
}
console.log("FluxMonitorPanel test passed");
