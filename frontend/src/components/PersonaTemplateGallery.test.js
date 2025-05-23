import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import PersonaTemplateGallery from "./PersonaTemplateGallery";

const html = renderToStaticMarkup(<PersonaTemplateGallery />);
if (!html.includes("Persona Templates")) {
  throw new Error("PersonaTemplateGallery render failed");
}
console.log("PersonaTemplateGallery test passed");
