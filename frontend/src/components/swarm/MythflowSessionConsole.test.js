import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MythflowSessionConsole from "./MythflowSessionConsole";
const html = renderToStaticMarkup(<MythflowSessionConsole />);
if (!html.includes("Mythflow Sessions")) {
  throw new Error("MythflowSessionConsole render failed");
}
console.log("MythflowSessionConsole test passed");
