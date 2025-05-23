import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import MythpathExplorerPage from "./MythpathExplorerPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <MythpathExplorerPage />
  </MemoryRouter>
);
if (!html.includes("Mythpath Explorer")) {
  throw new Error("MythpathExplorerPage render failed");
}
console.log("MythpathExplorerPage test passed");
