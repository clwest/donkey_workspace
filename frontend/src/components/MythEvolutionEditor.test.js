import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MythEvolutionEditor from "./MythEvolutionEditor";

const html = renderToStaticMarkup(<MythEvolutionEditor />);
if (!html.includes("Myth Evolution")) {
  throw new Error("MythEvolutionEditor render failed");
}
console.log("MythEvolutionEditor test passed");
