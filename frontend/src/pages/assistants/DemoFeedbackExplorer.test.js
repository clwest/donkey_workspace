import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import DemoFeedbackExplorer from "./DemoFeedbackExplorer";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <DemoFeedbackExplorer />
  </MemoryRouter>
);
if (!html.includes("Demo Feedback Explorer")) {
  throw new Error("DemoFeedbackExplorer render failed");
}
console.log("DemoFeedbackExplorer test passed");
