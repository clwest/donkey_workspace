import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import GlossaryMutationReviewPanel from "./GlossaryMutationReviewPanel";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <GlossaryMutationReviewPanel />
  </MemoryRouter>
);

if (!html.includes("Auto-Suggest Missing Labels")) {
  throw new Error("GlossaryMutationReviewPanel render failed");
}

console.log("GlossaryMutationReviewPanel test passed");

