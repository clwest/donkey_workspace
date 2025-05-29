import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantOnboardingCard from "./AssistantOnboardingCard";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <AssistantOnboardingCard />
  </MemoryRouter>
);
if (!html.includes("Assistant Identity Card")) {
  throw new Error("AssistantOnboardingCard render failed");
}
console.log("AssistantOnboardingCard test passed");
