import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import ArchetypeSelectionChamberPage from "./ArchetypeSelectionChamberPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <ArchetypeSelectionChamberPage />
  </MemoryRouter>
);
if (!html.includes("Archetype Selection")) {
  throw new Error("ArchetypeSelectionChamberPage render failed");
}
console.log("ArchetypeSelectionChamberPage test passed");
