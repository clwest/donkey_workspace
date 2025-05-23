import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import DreamframePlayer from "./DreamframePlayer";

const html = renderToStaticMarkup(<DreamframePlayer />);
if (!html.includes("Dreamframe Segments")) {
  throw new Error("DreamframePlayer render failed");
}
console.log("DreamframePlayer test passed");
