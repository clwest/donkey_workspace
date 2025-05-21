import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MemoryFlowVisualizer from "./MemoryFlowVisualizer";

const data = {
  nodes: [
    { id: "1", text: "A", tags: [], created_at: "", relevance_score: 0 },
    { id: "2", text: "B", tags: [], created_at: "", relevance_score: 0 },
  ],
  edges: [{ source: "1", target: "2" }],
};

const html = renderToStaticMarkup(<MemoryFlowVisualizer data={data} />);
if (!html.includes("svg")) {
  throw new Error("Flowmap render failed");
}
console.log("MemoryFlowVisualizer test passed");
