import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantTutorialPage from "./AssistantTutorialPage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/assistant/123/tutorial"]}>
    <AssistantTutorialPage />
  </MemoryRouter>
);
if (!html.includes("Assistant Tutorial")) {
  throw new Error("AssistantTutorialPage render failed");
}
console.log("AssistantTutorialPage test passed");
