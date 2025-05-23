import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RitualContractRunner from "./RitualContractRunner";

const html = renderToStaticMarkup(<RitualContractRunner />);
if (!html.includes("Ritual Contracts")) {
  throw new Error("RitualContractRunner render failed");
}
console.log("RitualContractRunner test passed");
