import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import MythOSLandingPage from "./MythOSLandingPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <MythOSLandingPage />
  </MemoryRouter>
);
if (!html.includes("MythOS")) {
  throw new Error("MythOSLandingPage render failed");
}
console.log("MythOSLandingPage test passed");
