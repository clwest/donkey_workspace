import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import VisualArchetypeCard from "./VisualArchetypeCard";

const html = renderToStaticMarkup(<VisualArchetypeCard assistantId={1} />);
if (!html.includes("Ritual State")) {
  throw new Error("VisualArchetypeCard render failed");
}
console.log("VisualArchetypeCard test passed");
