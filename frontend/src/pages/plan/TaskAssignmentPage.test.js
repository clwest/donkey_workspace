import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import TaskAssignmentPage from "./TaskAssignmentPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <TaskAssignmentPage />
  </MemoryRouter>
);
if (!html.includes("Role-Adaptive Task Assignment")) {
  throw new Error("TaskAssignmentPage render failed");
}
console.log("TaskAssignmentPage test passed");
