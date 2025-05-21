import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import NarrativeEventEditor from "./NarrativeEventEditor";

const html = renderToStaticMarkup(<NarrativeEventEditor onSave={() => {}} />);
if (!html.includes("Save Event")) {
  throw new Error("Editor render failed");
}
console.log("NarrativeEventEditor test passed");
