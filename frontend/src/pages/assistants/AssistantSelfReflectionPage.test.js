import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantSelfReflectionPage from "./AssistantSelfReflectionPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <AssistantSelfReflectionPage />
  </MemoryRouter>
);
if (!html.includes("Self Reflection")) {
  throw new Error("AssistantSelfReflectionPage render failed");
}
console.log("AssistantSelfReflectionPage test passed");
