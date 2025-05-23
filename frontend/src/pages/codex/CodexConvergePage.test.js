import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import CodexConvergePage from "./CodexConvergePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <CodexConvergePage />
  </MemoryRouter>
);
if (!html.includes("Codex Convergence")) {
  throw new Error("CodexConvergePage render failed");
}
console.log("CodexConvergePage test passed");
