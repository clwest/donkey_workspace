import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import DreamWorldSimulator from "./DreamWorldSimulator";

const html = renderToStaticMarkup(<DreamWorldSimulator />);
if (!html.includes("Dream Worlds")) {
  throw new Error("DreamWorldSimulator render failed");
}
console.log("DreamWorldSimulator test passed");
