import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantInterface from "./AssistantInterfacePage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/assistants/1/interface"]}>
    <AssistantInterface />
  </MemoryRouter>
);
if (!html.includes("Codex Anchors")) {
  throw new Error("AssistantInterface page render failed");
}
console.log("AssistantInterface page test passed");
