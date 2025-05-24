import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import SwarmAlignmentMeter from "./SwarmAlignmentMeter";

const html = renderToStaticMarkup(<SwarmAlignmentMeter />);
if (!html.includes("Swarm Alignment Score")) {
  throw new Error("SwarmAlignmentMeter render failed");
}
console.log("SwarmAlignmentMeter test passed");
