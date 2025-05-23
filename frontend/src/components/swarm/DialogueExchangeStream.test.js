import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import DialogueExchangeStream from "./DialogueExchangeStream";
const html = renderToStaticMarkup(<DialogueExchangeStream sessionId={1} />);
if (!html) {
  throw new Error("DialogueExchangeStream render failed");
}
console.log("DialogueExchangeStream test passed");
