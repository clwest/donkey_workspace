import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import CodexContractPage from "./CodexContractPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <CodexContractPage />
  </MemoryRouter>
);
if (!html.includes("Prompt Contract")) {
  throw new Error("CodexContractPage render failed");
}
console.log("CodexContractPage test passed");
