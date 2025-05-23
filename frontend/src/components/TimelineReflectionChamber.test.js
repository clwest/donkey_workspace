import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import TimelineReflectionChamber from "./TimelineReflectionChamber";

const html = renderToStaticMarkup(<TimelineReflectionChamber />);
if (!html.includes("Cross-Timeline Reflection Rites")) {
  throw new Error("TimelineReflectionChamber render failed");
}
console.log("TimelineReflectionChamber test passed");
