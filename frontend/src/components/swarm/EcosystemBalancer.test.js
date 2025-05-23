import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import EcosystemBalancer from "./EcosystemBalancer";

const html = renderToStaticMarkup(<EcosystemBalancer />);
if (!html.includes("Reflective Ecosystem Engines")) {
  throw new Error("EcosystemBalancer render failed");
}
console.log("EcosystemBalancer test passed");
