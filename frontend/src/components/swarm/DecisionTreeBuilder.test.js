import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import DecisionTreeBuilder from "./DecisionTreeBuilder";

const html = renderToStaticMarkup(<DecisionTreeBuilder />);
if (!html.includes("Decision Trees")) {
  throw new Error("DecisionTreeBuilder render failed");
}
console.log("DecisionTreeBuilder test passed");
