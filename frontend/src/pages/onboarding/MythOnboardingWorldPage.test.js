import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import MythOnboardingWorldPage from "./MythOnboardingWorldPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <MythOnboardingWorldPage />
  </MemoryRouter>
);
if (!html.includes("MythOS Onboarding World")) {
  throw new Error("MythOnboardingWorldPage render failed");
}
console.log("MythOnboardingWorldPage test passed");
