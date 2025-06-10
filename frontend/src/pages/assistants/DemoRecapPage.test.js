import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import DemoRecapPage from "./DemoRecapPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <DemoRecapPage />
  </MemoryRouter>
);
if (!html.includes("Demo Recap")) {
  throw new Error("DemoRecapPage render failed");
}
console.log("DemoRecapPage test passed");
