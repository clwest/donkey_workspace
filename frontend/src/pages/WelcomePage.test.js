import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import WelcomePage from "./WelcomePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <WelcomePage />
  </MemoryRouter>
);
if (!html.includes("first assistant")) {
  throw new Error("WelcomePage render failed");
}
console.log("WelcomePage test passed");
