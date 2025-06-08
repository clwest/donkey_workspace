import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import GrowthRecapModal from "./GrowthRecapModal";

const html = renderToStaticMarkup(
  <GrowthRecapModal stage={1} summary="Well done" onClose={() => {}} />
);
if (!html.includes("Well done")) {
  throw new Error("GrowthRecapModal missing summary");
}
console.log("GrowthRecapModal test passed");
