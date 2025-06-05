import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import DelegationSummaryPage from "./DelegationSummaryPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <DelegationSummaryPage />
  </MemoryRouter>
);
if (!html.includes("Delegation Summary")) {
  throw new Error("DelegationSummaryPage render failed");
}
console.log("DelegationSummaryPage test passed");
