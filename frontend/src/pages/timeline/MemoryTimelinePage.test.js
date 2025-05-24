import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import MemoryTimelinePage from "./MemoryTimelinePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <MemoryTimelinePage />
  </MemoryRouter>
);
if (!html.includes("Memory Timeline")) {
  throw new Error("MemoryTimelinePage render failed");
}
console.log("MemoryTimelinePage test passed");
