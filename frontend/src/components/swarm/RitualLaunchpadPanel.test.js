import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RitualLaunchpadPanel from "./RitualLaunchpadPanel";

const html = renderToStaticMarkup(<RitualLaunchpadPanel />);
if (!html.includes("Ritual Launchpads")) {
  throw new Error("RitualLaunchpadPanel render failed");
}
console.log("RitualLaunchpadPanel test passed");
