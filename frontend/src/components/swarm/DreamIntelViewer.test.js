import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import DreamIntelViewer from "./DreamIntelViewer";

const html = renderToStaticMarkup(<DreamIntelViewer />);
if (!html.includes("Dream Intelligence")) {
  throw new Error("DreamIntelViewer render failed");
}
console.log("DreamIntelViewer test passed");
