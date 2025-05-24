import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import CodexClauseMutatorPage from "./CodexClauseMutatorPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <CodexClauseMutatorPage />
  </MemoryRouter>
);
if (!html.includes("Codex Clause Mutator")) {
  throw new Error("CodexClauseMutatorPage render failed");
}
console.log("CodexClauseMutatorPage test passed");
