import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import DelegationTracePage from "./DelegationTracePage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <DelegationTracePage />
  </MemoryRouter>
);
if (!html.includes("Delegation Trace")) {
  throw new Error("DelegationTracePage render failed");
}
console.log("DelegationTracePage regression test passed");
