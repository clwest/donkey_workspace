import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import SimulationGridViewer from "./SimulationGridViewer";

const html = renderToStaticMarkup(<SimulationGridViewer />);
if (!html.includes("Simulation Grid")) {
  throw new Error("SimulationGridViewer render failed");
}
console.log("SimulationGridViewer test passed");
