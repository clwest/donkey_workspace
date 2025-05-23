import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import SummoningRitualConsolePage from "./SummoningRitualConsolePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <SummoningRitualConsolePage />
  </MemoryRouter>
);
if (!html.includes("Summoning Ritual")) {
  throw new Error("SummoningRitualConsolePage render failed");
}
console.log("SummoningRitualConsolePage test passed");
