import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ThreadDiagnosticsPanel from "./ThreadDiagnosticsPanel";

const thread = { continuity_score: 0.8, last_diagnostic_run: new Date().toISOString() };
const html = renderToStaticMarkup(<ThreadDiagnosticsPanel thread={thread} />);
if (!html.includes("Health Score")) {
  throw new Error("Diagnostics panel render failed");
}
console.log("ThreadDiagnosticsPanel test passed");
