import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import PurposeLoopPlayer from "./PurposeLoopPlayer";

const html = renderToStaticMarkup(<PurposeLoopPlayer />);
if (!html.includes("Purpose Loop Engines")) {
  throw new Error("PurposeLoopPlayer render failed");
}
console.log("PurposeLoopPlayer test passed");
