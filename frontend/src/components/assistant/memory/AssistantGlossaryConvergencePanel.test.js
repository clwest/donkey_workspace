import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantGlossaryConvergencePanel from "./AssistantGlossaryConvergencePanel";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <AssistantGlossaryConvergencePanel />
  </MemoryRouter>
);
if (!html.includes("Glossary Convergence")) {
  throw new Error("AssistantGlossaryConvergencePanel render failed");
}
console.log("AssistantGlossaryConvergencePanel test passed");
