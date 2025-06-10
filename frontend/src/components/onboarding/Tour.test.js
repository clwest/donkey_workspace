import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import Tour from "./Tour";

const steps = [
  { target: "body", content: "hi" }
];

const html = renderToStaticMarkup(<Tour steps={steps} />);
if (!html.includes("div")) {
  throw new Error("Tour failed to render");
}
console.log("Tour component test passed");
