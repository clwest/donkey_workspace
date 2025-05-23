import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ContinuityTraceboard from "./ContinuityTraceboard";

const html = renderToStaticMarkup(<ContinuityTraceboard />);
if (!html.includes("Continuity Engine Nodes")) {
  throw new Error("ContinuityTraceboard render failed");
}
console.log("ContinuityTraceboard test passed");
