import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import EntropyBalancerDashboard from "./EntropyBalancerDashboard";

const html = renderToStaticMarkup(<EntropyBalancerDashboard />);
if (!html.includes("Entropy Balancer")) {
  throw new Error("EntropyBalancerDashboard render failed");
}
console.log("EntropyBalancerDashboard test passed");
