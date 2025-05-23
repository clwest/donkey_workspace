import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import ProphecyEnginePage from "./ProphecyEnginePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <ProphecyEnginePage />
  </MemoryRouter>
);
if (!html.includes("Prophecy Engine")) {
  throw new Error("ProphecyEnginePage render failed");
}
console.log("ProphecyEnginePage test passed");
