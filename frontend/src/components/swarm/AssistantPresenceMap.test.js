import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantPresenceMap from "./AssistantPresenceMap";

const html = renderToStaticMarkup(<AssistantPresenceMap />);
if (!html.includes("Assistant Presence")) {
  throw new Error("AssistantPresenceMap render failed");
}
console.log("AssistantPresenceMap test passed");
