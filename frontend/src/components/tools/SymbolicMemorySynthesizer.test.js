import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import SymbolicMemorySynthesizer from "./SymbolicMemorySynthesizer";

const html = renderToStaticMarkup(<SymbolicMemorySynthesizer />);
if (!html.includes("Symbolic Memory Synthesizer")) {
  throw new Error("SymbolicMemorySynthesizer render failed");
}
console.log("SymbolicMemorySynthesizer test passed");
