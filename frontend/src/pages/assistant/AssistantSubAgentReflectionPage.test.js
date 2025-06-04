import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantSubAgentReflectionPage from "./AssistantSubAgentReflectionPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <AssistantSubAgentReflectionPage />
  </MemoryRouter>
);
if (!html.includes("Sub-Agent Reflection")) {
  throw new Error("AssistantSubAgentReflectionPage render failed");
}
console.log("AssistantSubAgentReflectionPage test passed");
