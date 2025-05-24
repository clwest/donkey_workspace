import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import RitualReputationPage from "./RitualReputationPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <RitualReputationPage />
  </MemoryRouter>
);
if (!html.includes("Ritual Reputation")) {
  throw new Error("RitualReputationPage render failed");
}
console.log("RitualReputationPage test passed");
