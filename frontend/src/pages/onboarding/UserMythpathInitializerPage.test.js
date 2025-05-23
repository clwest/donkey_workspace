import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import UserMythpathInitializerPage from "./UserMythpathInitializerPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <UserMythpathInitializerPage />
  </MemoryRouter>
);
if (!html.includes("Choose Your Mythpath")) {
  throw new Error("UserMythpathInitializerPage render failed");
}
console.log("UserMythpathInitializerPage test passed");
