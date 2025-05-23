import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ReflectionLoopPanel from "./ReflectionLoopPanel";
const html = renderToStaticMarkup(<ReflectionLoopPanel />);
if (!html.includes("Reflection Loops")) {
  throw new Error("ReflectionLoopPanel render failed");
}
console.log("ReflectionLoopPanel test passed");
