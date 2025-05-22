import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import BeliefContinuityDashboard from "./BeliefContinuityDashboard";

const html = renderToStaticMarkup(<BeliefContinuityDashboard />);
if (!html.includes("Belief Continuity")) {
  throw new Error("BeliefContinuityDashboard render failed");
}
console.log("BeliefContinuityDashboard test passed");
