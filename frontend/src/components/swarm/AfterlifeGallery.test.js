import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import AfterlifeGallery from "./AfterlifeGallery";

const html = renderToStaticMarkup(<AfterlifeGallery />);
if (!html.includes("Mythic Afterlife Registry")) {
  throw new Error("AfterlifeGallery render failed");
}
console.log("AfterlifeGallery test passed");
