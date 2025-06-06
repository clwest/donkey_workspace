import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import SymbolicAnchorAdminPage from "./SymbolicAnchorAdminPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <SymbolicAnchorAdminPage />
  </MemoryRouter>
);
if (!html.includes("Glossary Anchor Admin")) {
  throw new Error("SymbolicAnchorAdminPage render failed");
}
if (!html.includes("Protect Anchor")) {
  throw new Error("Protected toggle missing");
}
console.log("SymbolicAnchorAdminPage test passed");
