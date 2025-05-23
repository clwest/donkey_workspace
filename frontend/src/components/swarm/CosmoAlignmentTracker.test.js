import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import CosmoAlignmentTracker from "./CosmoAlignmentTracker";

const html = renderToStaticMarkup(<CosmoAlignmentTracker />);
if (!html.includes("Cosmo-Economic Alignment")) {
  throw new Error("CosmoAlignmentTracker render failed");
}
console.log("CosmoAlignmentTracker test passed");
