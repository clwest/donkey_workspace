import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import ReviewIngestPage from "./ReviewIngestPage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/assistants/1/review-ingest/1"]}>
    <ReviewIngestPage />
  </MemoryRouter>
);
if (!html.includes("Document Review")) {
  throw new Error("ReviewIngestPage render failed");
}
console.log("ReviewIngestPage test passed");
