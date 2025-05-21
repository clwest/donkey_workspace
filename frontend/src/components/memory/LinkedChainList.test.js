import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import LinkedChainList from "./LinkedChainList";

const chains = [
  { id: "1", title: "Chain", summary: "sum", projects: ["P"], assistants: ["A"] },
];

const html = renderToStaticMarkup(<LinkedChainList chains={chains} />);
if (!html.includes("Chain") || !html.includes("P") || !html.includes("A")) {
  throw new Error("LinkedChainList render failed");
}
console.log("LinkedChainList test passed");
