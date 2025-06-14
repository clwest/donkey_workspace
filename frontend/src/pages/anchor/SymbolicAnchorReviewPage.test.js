import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import SymbolicAnchorReviewPage from "./SymbolicAnchorReviewPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <SymbolicAnchorReviewPage />
  </MemoryRouter>
);
if (!html.includes("Symbolic Anchor Review")) {
  throw new Error("SymbolicAnchorReviewPage render failed");
}
if (!html.includes("Pending Mutations")) {
  throw new Error("Tabs missing");
}
console.log("SymbolicAnchorReviewPage test passed");
