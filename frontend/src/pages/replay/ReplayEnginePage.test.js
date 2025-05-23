import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import ReplayEnginePage from "./ReplayEnginePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <ReplayEnginePage />
  </MemoryRouter>
);
if (!html.includes("Belief Replay Engine")) {
  throw new Error("ReplayEnginePage render failed");
}
console.log("ReplayEnginePage test passed");
