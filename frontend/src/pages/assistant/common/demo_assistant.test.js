import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantDemoPage from "./AssistantDemoPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <AssistantDemoPage />
  </MemoryRouter>
);

if (!html.includes("prompt_pal")) {
  throw new Error("Example button missing starter query");
}
if (!html.includes("Reset Demos")) {
  throw new Error("Reset Demos button missing");
}
if (!html.includes("Demos are being reloaded")) {
  throw new Error("Empty state message missing");
}

console.log("demo_assistant test passed");
