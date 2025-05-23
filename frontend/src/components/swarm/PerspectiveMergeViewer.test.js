import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import PerspectiveMergeViewer from "./PerspectiveMergeViewer";

const html = renderToStaticMarkup(<PerspectiveMergeViewer />);
if (!html.includes("Perspective Merges")) {
  throw new Error("PerspectiveMergeViewer render failed");
}
console.log("PerspectiveMergeViewer test passed");
