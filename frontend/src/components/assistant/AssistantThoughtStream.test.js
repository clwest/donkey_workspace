import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantThoughtStream from "./AssistantThoughtStream";

const html = renderToStaticMarkup(
  <AssistantThoughtStream assistantId={1} />
);
if (!html.includes("Thought Stream")) {
  throw new Error("AssistantThoughtStream render failed");
}
console.log("AssistantThoughtStream test passed");
