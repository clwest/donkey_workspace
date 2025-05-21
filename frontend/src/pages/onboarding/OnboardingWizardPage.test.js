import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import OnboardingWizardPage from "./OnboardingWizardPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <OnboardingWizardPage />
  </MemoryRouter>
);
if (!html.includes("Onboarding Wizard")) {
  throw new Error("Onboarding wizard render failed");
}
console.log("OnboardingWizardPage test passed");
