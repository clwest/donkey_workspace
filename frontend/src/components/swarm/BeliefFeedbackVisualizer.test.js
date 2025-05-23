import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import BeliefFeedbackVisualizer from "./BeliefFeedbackVisualizer";

const html = renderToStaticMarkup(<BeliefFeedbackVisualizer />);
if (!html.includes("Belief Feedback Signals")) {
  throw new Error("BeliefFeedbackVisualizer render failed");
}
console.log("BeliefFeedbackVisualizer test passed");
