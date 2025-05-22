import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ResurrectionTemplateEditor from "./ResurrectionTemplateEditor";

const html = renderToStaticMarkup(<ResurrectionTemplateEditor />);
if (!html.includes("Resurrection Templates")) {
  throw new Error("ResurrectionTemplateEditor render failed");
}
console.log("ResurrectionTemplateEditor test passed");
