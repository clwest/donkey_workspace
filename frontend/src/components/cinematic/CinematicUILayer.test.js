import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import CinematicUILayer from "./CinematicUILayer";

const html = renderToStaticMarkup(
  <CinematicUILayer title="Test Layer">
    <p>content</p>
  </CinematicUILayer>
);
if (!html.includes("Test Layer")) {
  throw new Error("CinematicUILayer render failed");
}
console.log("CinematicUILayer test passed");
