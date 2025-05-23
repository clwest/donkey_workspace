import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RitualActionPanel from "./RitualActionPanel";

const html = renderToStaticMarkup(<RitualActionPanel />);
if (!html.includes("Ritual Launcher")) {
  throw new Error("RitualActionPanel render failed");
}
console.log("RitualActionPanel test passed");
