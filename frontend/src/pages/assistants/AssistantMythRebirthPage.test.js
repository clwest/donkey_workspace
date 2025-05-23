import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantMythRebirthPage from "./AssistantMythRebirthPage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/assistants/1/rebirth"]}>
    <AssistantMythRebirthPage />
  </MemoryRouter>
);
if (!html.includes("Assistant Rebirth")) {
  throw new Error("AssistantMythRebirthPage render failed");
}
console.log("AssistantMythRebirthPage test passed");
