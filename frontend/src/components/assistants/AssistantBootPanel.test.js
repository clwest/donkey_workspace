import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantBootPanel from "./AssistantBootPanel";

const assistant = { slug: "boot", tone: "", preferred_model: "gpt" };
const html = renderToStaticMarkup(<AssistantBootPanel assistant={assistant} />);
if (!html.includes("Boot Profile")) {
  throw new Error("AssistantBootPanel render failed");
}
console.log("AssistantBootPanel test passed");
