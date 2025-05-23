import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import MythOnboardingWorld from "./MythOnboardingWorld";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <MythOnboardingWorld />
  </MemoryRouter>
);
if (!html.includes("MythOS Onboarding World")) {
  throw new Error("MythOnboardingWorld render failed");
}
console.log("MythOnboardingWorld test passed");
