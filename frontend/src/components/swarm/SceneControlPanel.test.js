import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import SceneControlPanel from "./SceneControlPanel";

const html = renderToStaticMarkup(<SceneControlPanel />);
if (!html.includes("Scene Control")) {
  throw new Error("SceneControlPanel render failed");
}
console.log("SceneControlPanel test passed");
