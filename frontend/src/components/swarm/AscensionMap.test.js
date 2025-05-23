import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import AscensionMap from "./AscensionMap";

const html = renderToStaticMarkup(<AscensionMap />);
if (!html.includes("Ascension Structures")) {
  throw new Error("AscensionMap render failed");
}
console.log("AscensionMap test passed");
