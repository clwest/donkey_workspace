import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ContinuityAnchorCard from "./ContinuityAnchorCard";

const html = renderToStaticMarkup(<ContinuityAnchorCard />);
if (!html.includes("Continuity Anchors")) {
  throw new Error("ContinuityAnchorCard render failed");
}
console.log("ContinuityAnchorCard test passed");
