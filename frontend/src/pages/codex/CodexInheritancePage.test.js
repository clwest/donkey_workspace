import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import CodexInheritancePage from "./CodexInheritancePage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/codex/inheritance/1"]}>
    <CodexInheritancePage />
  </MemoryRouter>
);
if (!html.includes("Codex Inheritance")) {
  throw new Error("CodexInheritancePage render failed");
}
console.log("CodexInheritancePage test passed");
