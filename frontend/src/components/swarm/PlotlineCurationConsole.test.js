import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import PlotlineCurationConsole from "./PlotlineCurationConsole";
const html = renderToStaticMarkup(<PlotlineCurationConsole />);
if (!html.includes("Plotline Curations")) {
  throw new Error("PlotlineCurationConsole render failed");
}
console.log("PlotlineCurationConsole test passed");
