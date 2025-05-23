import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import ContinuityAnchorPage from "./ContinuityAnchorPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <ContinuityAnchorPage />
  </MemoryRouter>
);
if (!html.includes("Continuity Anchor")) {
  throw new Error("ContinuityAnchorPage render failed");
}
console.log("ContinuityAnchorPage test passed");
