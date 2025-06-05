import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantRagSelfTestPage from "./AssistantRagSelfTestPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <AssistantRagSelfTestPage />
  </MemoryRouter>
);
if (!html.includes("RAG Diagnostic Runner")) {
  throw new Error("AssistantRagSelfTestPage render failed");
}
console.log("AssistantRagSelfTestPage test passed");
