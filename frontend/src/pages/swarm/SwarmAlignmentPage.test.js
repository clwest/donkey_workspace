import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import SwarmAlignmentPage from "./SwarmAlignmentPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <SwarmAlignmentPage />
  </MemoryRouter>
);
if (!html.includes("Swarm Alignment")) {
  throw new Error("SwarmAlignmentPage render failed");
}
console.log("SwarmAlignmentPage test passed");
