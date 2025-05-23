import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import DialogueScriptEditor from "./DialogueScriptEditor";

const html = renderToStaticMarkup(<DialogueScriptEditor />);
if (!html.includes("Dialogue Scripts")) {
  throw new Error("DialogueScriptEditor render failed");
}
console.log("DialogueScriptEditor test passed");
