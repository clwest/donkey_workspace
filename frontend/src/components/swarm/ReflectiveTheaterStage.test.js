import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ReflectiveTheaterStage from "./ReflectiveTheaterStage";

const html = renderToStaticMarkup(<ReflectiveTheaterStage />);
if (!html.includes("Reflective Theater Sessions")) {
  throw new Error("ReflectiveTheaterStage render failed");
}
console.log("ReflectiveTheaterStage test passed");
