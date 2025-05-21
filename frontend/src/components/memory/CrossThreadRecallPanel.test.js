import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import CrossThreadRecallPanel from "./CrossThreadRecallPanel";

const entries = [{ id: "1", summary: "hello" }];
const html = renderToStaticMarkup(<CrossThreadRecallPanel entries={entries} />);
if (!html.includes("hello")) {
  throw new Error("CrossThreadRecallPanel render failed");
}
console.log("CrossThreadRecallPanel test passed");
