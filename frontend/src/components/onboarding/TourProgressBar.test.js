import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import TourProgressBar from "./TourProgressBar";

jest.mock("@/hooks/useTourProgress", () => () => ({ percent_complete: 50, next_hint: "glossary_tour" }));
jest.mock("@/hooks/useAssistantHints", () => () => ({ hints: [{ id: "glossary_tour", label: "Teach a Term" }] }));

const html = renderToStaticMarkup(<TourProgressBar assistantSlug="a" />);
if (!html.includes("Teach a Term")) {
  throw new Error("TourProgressBar missing label");
}
console.log("TourProgressBar test passed");
