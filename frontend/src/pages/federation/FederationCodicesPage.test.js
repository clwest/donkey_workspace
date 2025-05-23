import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import FederationCodicesPage from "./FederationCodicesPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <FederationCodicesPage />
  </MemoryRouter>
);
if (!html.includes("Codex Federation")) {
  throw new Error("FederationCodicesPage render failed");
}
console.log("FederationCodicesPage test passed");
