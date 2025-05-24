import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import ExecutionChainPage from "./ExecutionChainPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <ExecutionChainPage />
  </MemoryRouter>
);
if (!html.includes("Assistant Execution Chains")) {
  throw new Error("ExecutionChainPage render failed");
}
console.log("ExecutionChainPage test passed");
