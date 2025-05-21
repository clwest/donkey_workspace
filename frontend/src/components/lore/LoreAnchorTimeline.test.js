import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import LoreAnchorTimeline from "./LoreAnchorTimeline";

const html = renderToStaticMarkup(<LoreAnchorTimeline />);
if (!html.includes("Lore Anchors")) {
  throw new Error("LoreAnchorTimeline render failed");
}
console.log("LoreAnchorTimeline test passed");
