import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import DemoReflectionComposer from "./DemoReflectionComposer";

const html = renderToStaticMarkup(
  <DemoReflectionComposer slug="a" sessionId="s" show />
);
if (!html.includes("Demo Reflection")) {
  throw new Error("DemoReflectionComposer render failed");
}
console.log("DemoReflectionComposer test passed");
