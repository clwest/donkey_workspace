import React from "react";
import { MemoryRouter } from "react-router-dom";
import { renderToStaticMarkup } from "react-dom/server";
import RelayChainNodeCard from "./RelayChainNodeCard";

const node = { assistant: "Assistant A", message: "Hi", status: "delivered" };

const html = renderToStaticMarkup(
  <MemoryRouter>
    <RelayChainNodeCard node={node} />
  </MemoryRouter>
);
if (!html.includes("Assistant A") || !html.includes("Hi")) {
  throw new Error("RelayChainNodeCard render failed");
}
console.log("RelayChainNodeCard test passed");
