import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import NarrativeWalkthroughPlayer from "./NarrativeWalkthroughPlayer";

const html = renderToStaticMarkup(<NarrativeWalkthroughPlayer />);
if (!html.includes("Belief Narrative Walkthroughs")) {
  throw new Error("NarrativeWalkthroughPlayer render failed");
}
console.log("NarrativeWalkthroughPlayer test passed");
