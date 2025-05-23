import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import WorldTimelinePage from "./WorldTimelinePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <WorldTimelinePage />
  </MemoryRouter>
);
if (!html.includes("World Timeline")) {
  throw new Error("WorldTimelinePage render failed");
}
console.log("WorldTimelinePage test passed");
