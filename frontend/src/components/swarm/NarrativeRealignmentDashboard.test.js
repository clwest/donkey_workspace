import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import NarrativeRealignmentDashboard from "./NarrativeRealignmentDashboard";

const html = renderToStaticMarkup(<NarrativeRealignmentDashboard />);
if (!html.includes("Narrative Realignment Proposals")) {
  throw new Error("NarrativeRealignmentDashboard render failed");
}
console.log("NarrativeRealignmentDashboard test passed");
