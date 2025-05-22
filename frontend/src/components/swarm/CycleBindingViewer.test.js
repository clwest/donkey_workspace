import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import CycleBindingViewer from "./CycleBindingViewer";

const html = renderToStaticMarkup(<CycleBindingViewer />);
if (!html.includes("Myth Cycle")) {
  throw new Error("CycleBindingViewer render failed");
}
console.log("CycleBindingViewer test passed");
