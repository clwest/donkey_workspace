import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import RitualForecastPage from "./RitualForecastPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <RitualForecastPage />
  </MemoryRouter>
);
if (!html.includes("Ritual Forecast")) {
  throw new Error("RitualForecastPage render failed");
}
console.log("RitualForecastPage test passed");
