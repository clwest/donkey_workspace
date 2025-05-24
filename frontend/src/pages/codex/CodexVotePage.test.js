import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import CodexVotePage from "./CodexVotePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <CodexVotePage />
  </MemoryRouter>
);
if (!html.includes("Codex Clause Voting")) {
  throw new Error("CodexVotePage render failed");
}
console.log("CodexVotePage test passed");
