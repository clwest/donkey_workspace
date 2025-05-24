import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import CodexVotePanel from "./CodexVotePanel";

const html = renderToStaticMarkup(<CodexVotePanel />);
if (!html.includes("Codex Clause Votes")) {
  throw new Error("CodexVotePanel render failed");
}
console.log("CodexVotePanel test passed");
