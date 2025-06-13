import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import RagDiagnosticsDashboard from "./RagDiagnosticsDashboard";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <RagDiagnosticsDashboard />
  </MemoryRouter>
);
if (!html.includes("RAG Diagnostics")) {
  throw new Error("RagDiagnosticsDashboard render failed");
}
console.log("RagDiagnosticsDashboard test passed");
