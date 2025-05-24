import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantIdentityPage from "./AssistantIdentityPage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/assistants/1/identity"]}>
    <AssistantIdentityPage />
  </MemoryRouter>
);
if (!html.includes("Identity Anchor")) {
  throw new Error("AssistantIdentityPage render failed");
}
console.log("AssistantIdentityPage test passed");
