import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import NarrativeEventDetailPage from "./NarrativeEventDetailPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <NarrativeEventDetailPage />
  </MemoryRouter>
);
if (!html.includes("Scene Summary")) {
  throw new Error("Render failed");
}
console.log("NarrativeEventDetailPage test passed");
