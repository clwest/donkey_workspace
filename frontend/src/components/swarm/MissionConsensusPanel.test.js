import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MissionConsensusPanel from "./MissionConsensusPanel";

const html = renderToStaticMarkup(<MissionConsensusPanel />);
if (!html.includes("Mission Consensus Rounds")) {
  throw new Error("MissionConsensusPanel render failed");
}
console.log("MissionConsensusPanel test passed");
