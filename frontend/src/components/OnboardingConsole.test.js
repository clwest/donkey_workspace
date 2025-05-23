import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import OnboardingConsole from "./OnboardingConsole";

const html = renderToStaticMarkup(<OnboardingConsole />);
if (!html.includes("Onboarding Console")) {
  throw new Error("OnboardingConsole render failed");
}
console.log("OnboardingConsole test passed");
