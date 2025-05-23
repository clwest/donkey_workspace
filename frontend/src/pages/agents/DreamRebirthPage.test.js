import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import DreamRebirthPage from "./DreamRebirthPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <DreamRebirthPage />
  </MemoryRouter>
);
if (!html.includes("Dream Rebirth Console")) {
  throw new Error("DreamRebirthPage render failed");
}
console.log("DreamRebirthPage test passed");
