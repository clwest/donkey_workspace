import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import WelcomeBackPage from "./WelcomeBackPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <WelcomeBackPage />
  </MemoryRouter>
);
if (!html.includes("Welcome Back")) {
  throw new Error("WelcomeBackPage render failed");
}
console.log("WelcomeBackPage test passed");

