import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import TrainingGroundSimulator from "./TrainingGroundSimulator";

const html = renderToStaticMarkup(<TrainingGroundSimulator />);
if (!html.includes("Narrative Training Grounds")) {
  throw new Error("TrainingGroundSimulator render failed");
}
console.log("TrainingGroundSimulator test passed");
