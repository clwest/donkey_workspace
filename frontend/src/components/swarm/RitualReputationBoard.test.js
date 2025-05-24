import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RitualReputationBoard from "./RitualReputationBoard";

const html = renderToStaticMarkup(<RitualReputationBoard />);
if (!html.includes("Ritual Reputation")) {
  throw new Error("RitualReputationBoard render failed");
}
console.log("RitualReputationBoard test passed");
