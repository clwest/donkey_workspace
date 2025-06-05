import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RagPlaybackPanel from "./RagPlaybackPanel";

const html = renderToStaticMarkup(<RagPlaybackPanel slug="a1" />);
if (!html.includes("Anchor")) {
  throw new Error("RagPlaybackPanel render failed");
}
console.log("RagPlaybackPanel test passed");

