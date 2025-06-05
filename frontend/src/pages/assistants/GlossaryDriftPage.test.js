import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import GlossaryDriftPage from "./GlossaryDriftPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <GlossaryDriftPage />
  </MemoryRouter>
);
if (!html.includes("Glossary Drift Report")) {
  throw new Error("GlossaryDriftPage render failed");
}
console.log("GlossaryDriftPage test passed");
