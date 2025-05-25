import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import RunTaskPage from "./RunTaskPage";

const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={["/assistants/a/run-task"]}>
    <RunTaskPage />
  </MemoryRouter>
);
if (!html.includes("Run Task")) {
  throw new Error("RunTaskPage render failed");
}
console.log("RunTaskPage test passed");
