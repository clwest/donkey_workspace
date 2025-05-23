import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import LearningTrailViewer from "./LearningTrailViewer";

const html = renderToStaticMarkup(<LearningTrailViewer />);
if (!html.includes("Learning Trail")) {
  throw new Error("LearningTrailViewer render failed");
}
console.log("LearningTrailViewer test passed");
