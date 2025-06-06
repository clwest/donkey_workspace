import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RAGPlaybackPanel from "./RAGPlaybackPanel";

const html = renderToStaticMarkup(<RAGPlaybackPanel />);
if (!html.includes("RAG Playback")) {
  throw new Error("RAGPlaybackPanel render failed");
}
console.log("RAGPlaybackPanel test passed");
