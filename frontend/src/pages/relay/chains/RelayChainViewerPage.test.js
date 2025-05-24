import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import RelayChainViewerPage from "./RelayChainViewerPage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/relay/chains/demo"]}>
    <RelayChainViewerPage />
  </MemoryRouter>
);
if (!html.includes("Relay Chain Viewer")) {
  throw new Error("RelayChainViewerPage render failed");
}
console.log("RelayChainViewerPage test passed");
