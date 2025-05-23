import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RitualMetricsDashboard from "./RitualMetricsDashboard";

const html = renderToStaticMarkup(<RitualMetricsDashboard />);
if (!html.includes("Ritual Metrics")) {
  throw new Error("RitualMetricsDashboard render failed");
}
console.log("RitualMetricsDashboard test passed");
