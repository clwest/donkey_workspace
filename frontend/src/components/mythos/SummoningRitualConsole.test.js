import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import SummoningRitualConsole from "./SummoningRitualConsole";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <SummoningRitualConsole />
  </MemoryRouter>
);
if (!html.includes("Summoning Ritual")) {
  throw new Error("SummoningRitualConsole render failed");
}
console.log("SummoningRitualConsole test passed");
