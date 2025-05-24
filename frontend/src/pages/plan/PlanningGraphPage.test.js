import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import PlanningGraphPage from "./PlanningGraphPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <PlanningGraphPage />
  </MemoryRouter>
);
if (!html.includes("Multi-Agent Planning Graph")) {
  throw new Error("PlanningGraphPage render failed");
}
console.log("PlanningGraphPage test passed");
