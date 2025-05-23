import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ReturnCycleViewer from "./ReturnCycleViewer";

const html = renderToStaticMarkup(<ReturnCycleViewer />);
if (!html.includes("Eternal Return Cycles")) {
  throw new Error("ReturnCycleViewer render failed");
}
console.log("ReturnCycleViewer test passed");
