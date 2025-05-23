import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import PersonaStageRenderer from "./PersonaStageRenderer";
const html = renderToStaticMarkup(<PersonaStageRenderer assistantId={1} />);
if (!html) {
  throw new Error("PersonaStageRenderer render failed");
}
console.log("PersonaStageRenderer test passed");
