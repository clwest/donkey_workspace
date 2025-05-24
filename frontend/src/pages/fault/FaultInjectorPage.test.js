import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import FaultInjectorPage from "./FaultInjectorPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <FaultInjectorPage />
  </MemoryRouter>
);
if (!html.includes("Symbolic Fault Injector")) {
  throw new Error("FaultInjectorPage render failed");
}
console.log("FaultInjectorPage test passed");
