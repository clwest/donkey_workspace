import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantForkPage from "./AssistantForkPage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/assistants/1/fork"]}>
    <AssistantForkPage />
  </MemoryRouter>
);
if (!html.includes("Assistant Forks")) {
  throw new Error("AssistantForkPage render failed");
}
console.log("AssistantForkPage test passed");
