import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import CinemythComposer from "./CinemythComposer";

const html = renderToStaticMarkup(<CinemythComposer />);
if (!html.includes("Cinemyth Storylines")) {
  throw new Error("CinemythComposer render failed");
}
console.log("CinemythComposer test passed");
