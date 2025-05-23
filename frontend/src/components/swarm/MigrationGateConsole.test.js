import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MigrationGateConsole from "./MigrationGateConsole";

const html = renderToStaticMarkup(<MigrationGateConsole />);
if (!html.includes("Archetype Migration Gates")) {
  throw new Error("MigrationGateConsole render failed");
}
console.log("MigrationGateConsole test passed");
