import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import DemoReplayPage from "./DemoReplayPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <DemoReplayPage />
  </MemoryRouter>
);
if (!html.includes("Demo Replay")) {
  throw new Error("DemoReplayPage render failed");
}
console.log("DemoReplayPage test passed");
