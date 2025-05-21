import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import RegisterPage from "./RegisterPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <RegisterPage />
  </MemoryRouter>
);
if (!html.includes("Register")) {
  throw new Error("RegisterPage render failed");
}
console.log("RegisterPage test passed");
