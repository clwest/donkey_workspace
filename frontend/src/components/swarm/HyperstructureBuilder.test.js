import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import HyperstructureBuilder from "./HyperstructureBuilder";

const html = renderToStaticMarkup(<HyperstructureBuilder />);
if (!html.includes("Myth Hyperstructures")) {
  throw new Error("HyperstructureBuilder render failed");
}
console.log("HyperstructureBuilder test passed");
