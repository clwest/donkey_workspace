import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ArchetypeFieldMap from "./ArchetypeFieldMap";

const html = renderToStaticMarkup(<ArchetypeFieldMap />);
if (!html.includes("Archetype Fields")) {
  throw new Error("ArchetypeFieldMap render failed");
}
console.log("ArchetypeFieldMap test passed");
