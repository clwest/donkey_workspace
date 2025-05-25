import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import MythgraphViewerPage from "./MythgraphViewerPage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/mythgraph/123"]}>
    <MythgraphViewerPage />
  </MemoryRouter>
);
if (!html.includes("Mythgraph Viewer")) {
  throw new Error("MythgraphViewerPage render failed");
}
console.log("MythgraphViewerPage test passed");
