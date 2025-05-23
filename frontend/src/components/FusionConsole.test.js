import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import FusionConsole from "./FusionConsole";

const html = renderToStaticMarkup(<FusionConsole />);
if (!html.includes("Archetype Fusions")) {
  throw new Error("FusionConsole render failed");
}
console.log("FusionConsole test passed");
