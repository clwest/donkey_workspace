import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MythSimulationConsole from "./MythSimulationConsole";

const html = renderToStaticMarkup(<MythSimulationConsole />);
if (!html.includes("Myth Simulators")) {
  throw new Error("MythSimulationConsole render failed");
}
console.log("MythSimulationConsole test passed");
