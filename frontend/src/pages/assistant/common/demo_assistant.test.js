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

console.log("demo_assistant test passed");
