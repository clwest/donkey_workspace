import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import ArchetypeSelectionChamber from "./ArchetypeSelectionChamber";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <ArchetypeSelectionChamber />
  </MemoryRouter>
);
if (!html.includes("Archetype Selection")) {
  throw new Error("ArchetypeSelectionChamber render failed");
}
console.log("ArchetypeSelectionChamber test passed");
