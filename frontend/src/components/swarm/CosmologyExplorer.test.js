import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import CosmologyExplorer from "./CosmologyExplorer";

const html = renderToStaticMarkup(<CosmologyExplorer />);
if (!html.includes("Swarm Cosmologies")) {
  throw new Error("CosmologyExplorer render failed");
}
console.log("CosmologyExplorer test passed");
