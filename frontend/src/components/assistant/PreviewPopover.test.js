import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import PreviewPopover from "./PreviewPopover";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <PreviewPopover slug="test"><span>Hi</span></PreviewPopover>
  </MemoryRouter>
);
if (!html.includes("assistant-preview-popover")) {
  throw new Error("PreviewPopover render failed");
}
console.log("PreviewPopover test passed");
