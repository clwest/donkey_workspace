import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantMythRebirthFramework from "./AssistantMythRebirthFramework";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <AssistantMythRebirthFramework assistantId="1" />
  </MemoryRouter>
);
if (!html.includes("Assistant Rebirth")) {
  throw new Error("AssistantMythRebirthFramework render failed");
}
console.log("AssistantMythRebirthFramework test passed");
