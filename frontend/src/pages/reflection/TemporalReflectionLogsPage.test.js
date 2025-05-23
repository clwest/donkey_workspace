import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import TemporalReflectionLogsPage from "./TemporalReflectionLogsPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <TemporalReflectionLogsPage />
  </MemoryRouter>
);
if (!html.includes("Temporal Reflection Logs")) {
  throw new Error("TemporalReflectionLogsPage render failed");
}
console.log("TemporalReflectionLogsPage test passed");
