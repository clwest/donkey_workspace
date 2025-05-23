import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ConflictResolutionBoard from "./ConflictResolutionBoard";

const html = renderToStaticMarkup(<ConflictResolutionBoard />);
if (!html.includes("Conflict Resolutions")) {
  throw new Error("ConflictResolutionBoard render failed");
}
console.log("ConflictResolutionBoard test passed");
