import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import BeliefSignalTree from "./BeliefSignalTree";

const html = renderToStaticMarkup(<BeliefSignalTree />);
if (!html.includes("Belief Signals")) {
  throw new Error("BeliefSignalTree render failed");
}
console.log("BeliefSignalTree test passed");
