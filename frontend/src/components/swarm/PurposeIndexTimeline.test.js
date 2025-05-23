import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import PurposeIndexTimeline from "./PurposeIndexTimeline";

const html = renderToStaticMarkup(<PurposeIndexTimeline />);
if (!html.includes("Purpose Index")) {
  throw new Error("PurposeIndexTimeline render failed");
}
console.log("PurposeIndexTimeline test passed");
