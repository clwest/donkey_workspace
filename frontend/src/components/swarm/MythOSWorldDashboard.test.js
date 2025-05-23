import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MythOSWorldDashboard from "./MythOSWorldDashboard";

const html = renderToStaticMarkup(<MythOSWorldDashboard />);
if (!html.includes("MythOS World Metrics")) {
  throw new Error("MythOSWorldDashboard render failed");
}
console.log("MythOSWorldDashboard test passed");
