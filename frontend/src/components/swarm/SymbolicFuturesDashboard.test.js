import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import SymbolicFuturesDashboard from "./SymbolicFuturesDashboard";

const html = renderToStaticMarkup(<SymbolicFuturesDashboard />);
if (!html.includes("Symbolic Future Contracts")) {
  throw new Error("SymbolicFuturesDashboard render failed");
}
console.log("SymbolicFuturesDashboard test passed");
