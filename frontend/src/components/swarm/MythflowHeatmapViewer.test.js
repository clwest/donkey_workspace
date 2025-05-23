import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MythflowHeatmapViewer from "./MythflowHeatmapViewer";

const html = renderToStaticMarkup(<MythflowHeatmapViewer />);
if (!html.includes("Mythflow Heatmap")) {
  throw new Error("MythflowHeatmapViewer render failed");
}
console.log("MythflowHeatmapViewer test passed");
