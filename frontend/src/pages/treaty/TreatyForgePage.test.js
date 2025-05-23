import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import TreatyForgePage from "./TreatyForgePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <TreatyForgePage />
  </MemoryRouter>
);
if (!html.includes("Treaty Forge")) {
  throw new Error("TreatyForgePage render failed");
}
console.log("TreatyForgePage test passed");
