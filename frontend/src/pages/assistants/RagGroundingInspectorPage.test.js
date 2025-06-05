import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import RagGroundingInspectorPage from "./RagGroundingInspectorPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <RagGroundingInspectorPage />
  </MemoryRouter>
);
if (!html.includes("RAG Grounding Inspector")) {
  throw new Error("RagGroundingInspectorPage render failed");
}
console.log("RagGroundingInspectorPage test passed");

