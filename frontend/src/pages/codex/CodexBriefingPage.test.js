import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import CodexBriefingPage from "./CodexBriefingPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <CodexBriefingPage />
  </MemoryRouter>
);
if (!html.includes("Codex Briefing")) {
  throw new Error("CodexBriefingPage render failed");
}
console.log("CodexBriefingPage test passed");
