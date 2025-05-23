import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import NarrativePressureGauge from "./NarrativePressureGauge";
const html = renderToStaticMarkup(<NarrativePressureGauge sessionId={1} />);
if (!html.includes("Narrative Pressure")) {
  throw new Error("NarrativePressureGauge render failed");
}
console.log("NarrativePressureGauge test passed");
