import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RitualQuickActionsLayer from "./RitualQuickActionsLayer";

const html = renderToStaticMarkup(
  <RitualQuickActionsLayer assistantId={1} />
);
if (!html.includes("Reflect")) {
  throw new Error("RitualQuickActionsLayer render failed");
}
console.log("RitualQuickActionsLayer test passed");
