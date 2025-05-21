import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MythRegistryViewer from "./MythRegistryViewer";

const html = renderToStaticMarkup(<MythRegistryViewer />);
if (!html.includes("Myth Registry")) {
  throw new Error("MythRegistryViewer render failed");
}
console.log("MythRegistryViewer test passed");
