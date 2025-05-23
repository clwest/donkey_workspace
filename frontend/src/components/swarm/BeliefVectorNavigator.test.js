import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import BeliefVectorNavigator from "./BeliefVectorNavigator";

const html = renderToStaticMarkup(<BeliefVectorNavigator />);
if (!html.includes("Belief Navigation Vectors")) {
  throw new Error("BeliefVectorNavigator render failed");
}
console.log("BeliefVectorNavigator test passed");
