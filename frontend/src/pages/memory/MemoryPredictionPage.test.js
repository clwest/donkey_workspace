import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import MemoryPredictionPage from "./MemoryPredictionPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <MemoryPredictionPage />
  </MemoryRouter>
);
if (!html.includes("Memory Prediction")) {
  throw new Error("MemoryPredictionPage render failed");
}
console.log("MemoryPredictionPage test passed");
