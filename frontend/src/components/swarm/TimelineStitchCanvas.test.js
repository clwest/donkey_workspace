import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import TimelineStitchCanvas from "./TimelineStitchCanvas";

const html = renderToStaticMarkup(<TimelineStitchCanvas />);
if (!html.includes("Timeline Stitch Logs")) {
  throw new Error("TimelineStitchCanvas render failed");
}
console.log("TimelineStitchCanvas test passed");
