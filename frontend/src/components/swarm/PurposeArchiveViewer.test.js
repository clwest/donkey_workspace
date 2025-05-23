import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import PurposeArchiveViewer from "./PurposeArchiveViewer";

const html = renderToStaticMarkup(<PurposeArchiveViewer />);
if (!html.includes("Purpose Archives")) {
  throw new Error("PurposeArchiveViewer render failed");
}
console.log("PurposeArchiveViewer test passed");
