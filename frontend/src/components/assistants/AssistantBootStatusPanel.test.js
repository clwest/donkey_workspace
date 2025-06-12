import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantBootStatusPanel from "./AssistantBootStatusPanel";

const html = renderToStaticMarkup(<AssistantBootStatusPanel slug="demo" />);
if (!html.includes("Boot Status")) {
  throw new Error("AssistantBootStatusPanel render failed");
}
console.log("AssistantBootStatusPanel test passed");
