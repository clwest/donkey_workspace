import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import RitualLawPage from "./RitualLawPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <RitualLawPage />
  </MemoryRouter>
);
if (!html.includes("Ritual Law")) {
  throw new Error("RitualLawPage render failed");
}
console.log("RitualLawPage test passed");
