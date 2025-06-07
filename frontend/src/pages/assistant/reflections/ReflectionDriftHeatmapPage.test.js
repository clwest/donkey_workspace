import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import ReflectionDriftHeatmapPage from "./ReflectionDriftHeatmapPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <ReflectionDriftHeatmapPage />
  </MemoryRouter>
);
if (!html.includes("Glossary Drift Heatmap")) {
  throw new Error("ReflectionDriftHeatmapPage render failed");
}
console.log("ReflectionDriftHeatmapPage test passed");
