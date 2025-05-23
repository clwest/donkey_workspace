import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import TemporalReflectionLogViewer from "./TemporalReflectionLogViewer";

const html = renderToStaticMarkup(<TemporalReflectionLogViewer />);
if (!html.includes("Temporal Reflection Logs")) {
  throw new Error("TemporalReflectionLogViewer render failed");
}
console.log("TemporalReflectionLogViewer test passed");
