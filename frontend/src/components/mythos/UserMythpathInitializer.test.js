import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import UserMythpathInitializer from "./UserMythpathInitializer";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <UserMythpathInitializer />
  </MemoryRouter>
);
if (!html.includes("Choose Your Mythpath")) {
  throw new Error("UserMythpathInitializer render failed");
}
console.log("UserMythpathInitializer test passed");
