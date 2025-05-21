import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import LogoutPage from "./LogoutPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <LogoutPage />
  </MemoryRouter>
);
if (!html.includes("Logging out")) {
  throw new Error("LogoutPage render failed");
}
console.log("LogoutPage test passed");
