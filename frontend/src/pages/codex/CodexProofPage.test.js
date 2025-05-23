import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import CodexProofPage from "./CodexProofPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <CodexProofPage />
  </MemoryRouter>
);
if (!html.includes("Codex Integrity Proof")) {
  throw new Error("CodexProofPage render failed");
}
console.log("CodexProofPage test passed");
