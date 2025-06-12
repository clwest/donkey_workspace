import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MemoryTimelinePanel from "./MemoryTimelinePanel";

const entries = [
  { id: "1", event: "Insight stored", created_at: "2024-01-01T00:00:00Z" },
];
const html = renderToStaticMarkup(
  <MemoryTimelinePanel
    assistantId="a1"
    documentId="d1"
    initialEntries={entries}
  />
);
if (
  !html.includes("Memory Timeline") ||
  !html.includes("Insight stored") ||
  !html.includes("📝")
) {
  throw new Error("MemoryTimelinePanel render failed");
}
console.log("MemoryTimelinePanel test passed");
