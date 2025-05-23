import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import IdentityCardViewer from "./IdentityCardViewer";

const html = renderToStaticMarkup(<IdentityCardViewer />);
if (!html.includes("Mythic Identity Cards")) {
  throw new Error("IdentityCardViewer render failed");
}
console.log("IdentityCardViewer test passed");
