import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RagDebugPanel from "./RagDebugPanel";

const html = renderToStaticMarkup(<RagDebugPanel slug="a1" />);
if (!html.includes("Query")) {
  throw new Error("RagDebugPanel render failed");
}
console.log("RagDebugPanel test passed");

