import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import AlignmentMarketBoard from "./AlignmentMarketBoard";

const html = renderToStaticMarkup(<AlignmentMarketBoard />);
if (!html.includes("Alignment Market")) {
  throw new Error("AlignmentMarketBoard render failed");
}
console.log("AlignmentMarketBoard test passed");
