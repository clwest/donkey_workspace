import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantMythpathPage from "./AssistantMythpathPage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/assistants/1/mythpath"]}>
    <AssistantMythpathPage />
  </MemoryRouter>
);
if (!html.includes("Mythpath Timeline")) {
  throw new Error("AssistantMythpathPage render failed");
}
console.log("AssistantMythpathPage test passed");
