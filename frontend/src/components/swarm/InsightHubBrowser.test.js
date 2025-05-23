import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import InsightHubBrowser from "./InsightHubBrowser";

const html = renderToStaticMarkup(<InsightHubBrowser />);
if (!html.includes("Insight Hubs")) {
  throw new Error("InsightHubBrowser render failed");
}
console.log("InsightHubBrowser test passed");
