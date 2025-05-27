import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantLineagePage from "./AssistantLineagePage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/assistants/1/lineage"]}>
    <AssistantLineagePage />
  </MemoryRouter>
);
if (!html.includes("Assistant Lineage")) {
  throw new Error("AssistantLineagePage render failed");
}
console.log("AssistantLineagePage test passed");
