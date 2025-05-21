import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import ThreadEditorPage from "./ThreadEditorPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <ThreadEditorPage />
  </MemoryRouter>
);
if (!html.includes("Thread Editor")) {
  throw new Error("ThreadEditorPage render failed");
}
console.log("ThreadEditorPage test passed");
