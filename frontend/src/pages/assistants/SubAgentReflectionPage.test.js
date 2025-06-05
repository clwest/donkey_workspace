import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import SubAgentReflectionPage from "./SubAgentReflectionPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <SubAgentReflectionPage />
  </MemoryRouter>
);
if (!html.includes("Sub-Agent Reflection")) {
  throw new Error("SubAgentReflectionPage render failed");
}
console.log("SubAgentReflectionPage test passed");
