import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import SimpleSparkline from "./SimpleSparkline";

const html = renderToStaticMarkup(<SimpleSparkline data={[1, 2, 3]} />);
if (!html.includes("svg")) {
  throw new Error("Sparkline failed");
}
console.log("SimpleSparkline test passed");
