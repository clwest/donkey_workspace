import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import SignalArtifactTransmitter from "./SignalArtifactTransmitter";

const html = renderToStaticMarkup(<SignalArtifactTransmitter />);
if (!html.includes("Signal Artifacts")) {
  throw new Error("SignalArtifactTransmitter render failed");
}
console.log("SignalArtifactTransmitter test passed");
