import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import SymbolicMemorySynthesizerPage from "./SymbolicMemorySynthesizerPage";

const html = renderToStaticMarkup(
  <MemoryRouter>
    <SymbolicMemorySynthesizerPage />
  </MemoryRouter>
);
if (!html.includes("Symbolic Memory Synthesizer")) {
  throw new Error("SymbolicMemorySynthesizerPage render failed");
}
console.log("SymbolicMemorySynthesizerPage test passed");
