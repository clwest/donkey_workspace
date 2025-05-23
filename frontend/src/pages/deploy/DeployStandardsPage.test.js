import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import DeployStandardsPage from "./DeployStandardsPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <DeployStandardsPage />
  </MemoryRouter>
);
if (!html.includes("Deployment Standards")) {
  throw new Error("DeployStandardsPage render failed");
}
console.log("DeployStandardsPage test passed");
