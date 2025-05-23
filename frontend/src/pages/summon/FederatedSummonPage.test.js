import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import FederatedSummonPage from "./FederatedSummonPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <FederatedSummonPage />
  </MemoryRouter>
);
if (!html.includes("Federated Assistant Summoner")) {
  throw new Error("FederatedSummonPage render failed");
}
console.log("FederatedSummonPage test passed");
