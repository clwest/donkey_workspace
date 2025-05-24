import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import BeliefForecastPage from "./BeliefForecastPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <BeliefForecastPage />
  </MemoryRouter>
);
if (!html.includes("Belief Resonance Forecast")) {
  throw new Error("BeliefForecastPage render failed");
}
console.log("BeliefForecastPage test passed");
