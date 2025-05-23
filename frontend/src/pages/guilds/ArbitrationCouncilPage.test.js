import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import ArbitrationCouncilPage from "./ArbitrationCouncilPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <ArbitrationCouncilPage />
  </MemoryRouter>
);
if (!html.includes("Arbitration Council")) {
  throw new Error("ArbitrationCouncilPage render failed");
}
console.log("ArbitrationCouncilPage test passed");
