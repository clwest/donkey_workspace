import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import GlossaryConvergencePage from "./GlossaryConvergencePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <GlossaryConvergencePage />
  </MemoryRouter>
);
if (!html.includes("Glossary Convergence")) {
  throw new Error("GlossaryConvergencePage render failed");
}
console.log("GlossaryConvergencePage test passed");
