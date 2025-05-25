import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantRunTaskPanel from "./AssistantRunTaskPanel";

const html = renderToStaticMarkup(<AssistantRunTaskPanel slug="a1" />);
if (!html.includes("Run Task")) {
  throw new Error("AssistantRunTaskPanel render failed");
}
console.log("AssistantRunTaskPanel test passed");
