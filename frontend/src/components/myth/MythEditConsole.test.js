import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MythEditConsole from "./MythEditConsole";

const html = renderToStaticMarkup(<MythEditConsole />);
if (!html.includes("Myth Edit Log")) {
  throw new Error("MythEditConsole render failed");
}
console.log("MythEditConsole test passed");
