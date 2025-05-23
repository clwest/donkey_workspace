import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import RitualContainersPage from "./RitualContainersPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <RitualContainersPage />
  </MemoryRouter>
);
if (!html.includes("Ritual Containers")) {
  throw new Error("RitualContainersPage render failed");
}
console.log("RitualContainersPage test passed");
