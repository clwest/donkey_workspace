import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import ProfilePage from "./ProfilePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <ProfilePage />
  </MemoryRouter>
);
if (!html.includes("User Profile")) {
  throw new Error("ProfilePage render failed");
}
console.log("ProfilePage test passed");
