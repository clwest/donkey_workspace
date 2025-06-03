import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MoodStabilityGauge from "./MoodStabilityGauge";

const html = renderToStaticMarkup(<MoodStabilityGauge score={0.6} />);
if (!html.includes("progress-bar")) {
  throw new Error("MoodStabilityGauge render failed");
}
console.log("MoodStabilityGauge test passed");
