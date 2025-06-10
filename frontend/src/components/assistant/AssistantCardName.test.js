import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import AssistantCard from "./AssistantCard";

const html = renderToStaticMarkup(
  <AssistantCard assistant={{ id: 1, slug: "a", identity: { display_name: "Zoe" } }} />
);
if (!html.includes("Zoe")) {
  throw new Error("Display name not rendered");
}
console.log("AssistantCardName test passed");
