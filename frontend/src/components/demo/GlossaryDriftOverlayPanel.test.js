import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import GlossaryDriftOverlayPanel from "./GlossaryDriftOverlayPanel";

const html = renderToStaticMarkup(
  <GlossaryDriftOverlayPanel slug="a" sessionId="s" />
);
if (!html.includes("Drift Overlay")) {
  throw new Error("GlossaryDriftOverlayPanel render failed");
}
console.log("GlossaryDriftOverlayPanel test passed");
