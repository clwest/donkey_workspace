import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import DemoOverlayPage from "./DemoOverlayPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <DemoOverlayPage />
  </MemoryRouter>
);
if (!html.includes("Demo Overlay")) {
  throw new Error("DemoOverlayPage render failed");
}
console.log("DemoOverlayPage test passed");
