import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RitualComplianceDashboard from "./RitualComplianceDashboard";

const html = renderToStaticMarkup(<RitualComplianceDashboard />);
if (!html.includes("Ritual Compliance")) {
  throw new Error("RitualComplianceDashboard render failed");
}
console.log("RitualComplianceDashboard test passed");
