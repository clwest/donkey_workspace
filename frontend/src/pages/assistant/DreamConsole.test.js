import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import DreamConsole from "./DreamConsole";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <DreamConsole />
  </MemoryRouter>
);
if (!html.includes("Dream Console")) {
  throw new Error("DreamConsole render failed");
}
console.log("DreamConsole test passed");
