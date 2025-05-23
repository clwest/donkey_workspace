import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import CodexAnchorPanel from "./CodexAnchorPanel";

const html = renderToStaticMarkup(<CodexAnchorPanel assistantId={1} />);
if (!html.includes("Codex Anchors")) {
  throw new Error("CodexAnchorPanel render failed");
}
console.log("CodexAnchorPanel test passed");
