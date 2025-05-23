import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import DirectiveTrackerPanel from "./DirectiveTrackerPanel";

const html = renderToStaticMarkup(<DirectiveTrackerPanel assistantId={1} />);
if (!html.includes("Directive Tracker")) {
  throw new Error("DirectiveTrackerPanel render failed");
}
console.log("DirectiveTrackerPanel test passed");
