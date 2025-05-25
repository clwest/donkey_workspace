import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import MythOSProjectComposerPage from "./MythOSProjectComposerPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <MythOSProjectComposerPage />
  </MemoryRouter>
);
if (!html.includes("Project Composer")) {
  throw new Error("MythOSProjectComposerPage render failed");
}
console.log("MythOSProjectComposerPage test passed");
