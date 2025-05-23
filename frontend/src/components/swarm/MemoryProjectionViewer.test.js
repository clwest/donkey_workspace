import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MemoryProjectionViewer from "./MemoryProjectionViewer";

const html = renderToStaticMarkup(<MemoryProjectionViewer />);
if (!html.includes("Memory Projection Frames")) {
  throw new Error("MemoryProjectionViewer render failed");
}
console.log("MemoryProjectionViewer test passed");
