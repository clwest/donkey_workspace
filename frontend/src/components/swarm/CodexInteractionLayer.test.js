import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import CodexInteractionLayer from "./CodexInteractionLayer";

const html = renderToStaticMarkup(<CodexInteractionLayer />);
if (!html.includes("Codex Interaction")) {
  throw new Error("CodexInteractionLayer render failed");
}
console.log("CodexInteractionLayer test passed");
