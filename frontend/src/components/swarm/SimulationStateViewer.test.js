import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import SimulationStateViewer from "./SimulationStateViewer";

const html = renderToStaticMarkup(<SimulationStateViewer />);
if (!html.includes("Simulation States")) {
  throw new Error("SimulationStateViewer render failed");
}
console.log("SimulationStateViewer test passed");
