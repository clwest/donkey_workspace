import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantInterfaceRenderer from "./AssistantInterfaceRenderer";

const html = renderToStaticMarkup(
  <AssistantInterfaceRenderer assistantId={1} />
);
if (!html.includes("Codex Anchors")) {
  throw new Error("AssistantInterfaceRenderer render failed");
}
console.log("AssistantInterfaceRenderer test passed");
