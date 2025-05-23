import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import BeliefEnginePanel from "./BeliefEnginePanel";

const html = renderToStaticMarkup(<BeliefEnginePanel assistantId={1} />);
if (!html.includes("Update Belief Engine")) {
  throw new Error("BeliefEnginePanel render failed");
}
console.log("BeliefEnginePanel test passed");
