import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import RitualOnboardingPage from "./RitualOnboardingPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <RitualOnboardingPage />
  </MemoryRouter>
);
if (!html.includes("Ritual Onboarding")) {
  throw new Error("RitualOnboardingPage render failed");
}
console.log("RitualOnboardingPage test passed");
