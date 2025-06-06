import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import OnboardingWorldPage from "./OnboardingWorldPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <OnboardingWorldPage />
  </MemoryRouter>
);
if (!html.includes("Onboarding World")) {
  throw new Error("OnboardingWorldPage render failed");
}
console.log("OnboardingWorldPage test passed");
