import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import LoginPage from "./LoginPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <LoginPage />
  </MemoryRouter>
);
if (!html.includes("Login")) {
  throw new Error("LoginPage render failed");
}
console.log("LoginPage test passed");
