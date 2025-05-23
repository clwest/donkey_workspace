import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import LegacyVaultViewer from "./LegacyVaultViewer";

const html = renderToStaticMarkup(<LegacyVaultViewer />);
if (!html.includes("Legacy Continuity Vaults")) {
  throw new Error("LegacyVaultViewer render failed");
}
console.log("LegacyVaultViewer test passed");
