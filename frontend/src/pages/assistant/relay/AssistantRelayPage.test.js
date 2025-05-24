import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantRelayPage from "./AssistantRelayPage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/assistants/test/relay"]}>
    <AssistantRelayPage />
  </MemoryRouter>
);
if (!html.includes("Relay Console")) {
  throw new Error("AssistantRelayPage render failed");
}
console.log("AssistantRelayPage test passed");
