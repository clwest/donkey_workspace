import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import ThreadsOverviewPage from "./ThreadsOverviewPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <ThreadsOverviewPage />
  </MemoryRouter>
);
if (!html.includes("Continuity")) {
  throw new Error("ThreadsOverviewPage render failed");
}
console.log("ThreadsOverviewPage test passed");
