import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import EmbeddingDebug from "./EmbeddingDebug.jsx";
import * as hook from "../../../hooks/useAuditEmbeddingLinks";

hook.default = () => ({
  rows: [
    {
      assistant: "a",
      assistant_name: "Test",
      context_id: "c1",
      count: 1,
      status: "pending",
    },
  ],
  error: null,
  reload: () => {},
});

const html = renderToStaticMarkup(<EmbeddingDebug />);
if (!html.includes("Embedding Debug")) {
  throw new Error("EmbeddingDebug render failed");
}
if (!html.includes("Fix") || !html.includes("Ignore")) {
  throw new Error("EmbeddingDebug actions missing");
}
console.log("EmbeddingDebug test passed");
