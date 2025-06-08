import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import DemoComparisonCard from "./DemoComparisonCard";

const data = {
  name: "Prompt Pal",
  demo_slug: "prompt_pal",
  flair: "✨",
  tone: "friendly",
  traits: ["helpful"],
  motto: "Let's build!",
  preview_chat: ["Hi", "Hello"],
};

const html = renderToStaticMarkup(
  <MemoryRouter>
    <DemoComparisonCard assistant={data} />
  </MemoryRouter>
);
if (!html.includes("prefill=prompt_pal")) {
  throw new Error("Customize link missing prefill param");
}
console.log("DemoComparisonCard test passed");
