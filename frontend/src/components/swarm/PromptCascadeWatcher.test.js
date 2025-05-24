import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import PromptCascadeWatcher from "./PromptCascadeWatcher";

const html = renderToStaticMarkup(<PromptCascadeWatcher promptId="x" />);
if (!html.includes("Prompt Cascade")) {
  throw new Error("PromptCascadeWatcher render failed");
}
console.log("PromptCascadeWatcher test passed");
