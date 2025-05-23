import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MythpathExplorerComponent from "./MythpathExplorerComponent";

const html = renderToStaticMarkup(<MythpathExplorerComponent />);
if (!html.includes("Mythpath Explorer")) {
  throw new Error("MythpathExplorerComponent render failed");
}
console.log("MythpathExplorerComponent test passed");
