import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import MemorySandboxPage from "./MemorySandboxPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <MemorySandboxPage />
  </MemoryRouter>
);
if (!html.includes("Memory Alignment Sandbox")) {
  throw new Error("MemorySandboxPage render failed");
}
console.log("MemorySandboxPage test passed");
