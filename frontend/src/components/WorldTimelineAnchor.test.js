import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import WorldTimelineAnchor from "./WorldTimelineAnchor";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <WorldTimelineAnchor />
  </MemoryRouter>
);
if (!html.includes("World Timeline")) {
  throw new Error("WorldTimelineAnchor render failed");
}
console.log("WorldTimelineAnchor test passed");
